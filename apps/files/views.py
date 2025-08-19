import json
import base64
import requests
from pathlib import Path
from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.conf import settings
from django.http import HttpResponse
import pdfplumber
import pandas as pd
import fitz  # PyMuPDF
from .models import FileUpload
from .serializers import FileUploadSerializer


def get_file_extension(filename):
    """ファイル拡張子を取得"""
    return Path(filename).suffix.lower()


def extract_images_from_pdf(file_path):
    """PDFから画像を抽出"""
    try:
        doc = fitz.open(file_path)
        images = []
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            image_list = page.get_images()
            
            for img_index, img in enumerate(image_list):
                # 画像を抽出
                xref = img[0]
                pix = fitz.Pixmap(doc, xref)
                
                # CMYK画像はRGBに変換
                if pix.n - pix.alpha < 4:
                    img_data = pix.tobytes("png")
                    images.append({
                        'page': page_num + 1,
                        'index': img_index,
                        'data': base64.b64encode(img_data).decode('utf-8'),
                        'format': 'png'
                    })
                else:
                    pix1 = fitz.Pixmap(fitz.csRGB, pix)
                    img_data = pix1.tobytes("png")
                    images.append({
                        'page': page_num + 1,
                        'index': img_index,
                        'data': base64.b64encode(img_data).decode('utf-8'),
                        'format': 'png'
                    })
                    pix1 = None
                
                pix = None
        
        doc.close()
        return images
    except Exception as e:
        return f"PDF画像抽出エラー: {str(e)}"


def extract_text_from_pdf(file_path):
    """PDFからテキストと表を抽出（画像ベースPDFの判定含む）"""
    try:
        text_content = ""
        tables_content = []
        is_image_based = False

        with pdfplumber.open(file_path) as pdf:
            total_text_length = 0
            
            for page_num, page in enumerate(pdf.pages):
                # テキストを抽出
                page_text = page.extract_text()
                if page_text:
                    text_content += f"--- ページ {page_num + 1} ---\n"
                    text_content += page_text + "\n\n"
                    total_text_length += len(page_text.strip())

                # 表を抽出
                tables = page.find_tables()
                for table_num, table in enumerate(tables):
                    try:
                        table_data = table.extract()
                        if table_data:
                            tables_content.append({
                                'page': page_num + 1,
                                'table': table_num + 1,
                                'data': table_data
                            })
                    except Exception:
                        continue

            # 画像ベースPDFかどうかを判定（テキストが極端に少ない場合）
            if total_text_length < 50:  # 閾値: 50文字未満の場合は画像ベースと判定
                is_image_based = True
                # 画像を抽出
                extracted_images = extract_images_from_pdf(file_path)
                if isinstance(extracted_images, list) and len(extracted_images) > 0:
                    return {
                        'type': 'image_based_pdf',
                        'images': extracted_images,
                        'text': text_content.strip(),
                        'tables': tables_content,
                        'has_tables': len(tables_content) > 0
                    }

        # 結果を整理
        result = {
            'type': 'text_based_pdf',
            'text': text_content.strip(),
            'tables': tables_content,
            'has_tables': len(tables_content) > 0,
            'is_image_based': is_image_based
        }

        # 表がある場合は、表の内容も文字列として追加
        if tables_content:
            result['text'] += "\n\n--- 抽出された表 ---\n"
            for table_info in tables_content:
                result['text'] += f"\nページ{table_info['page']} 表{table_info['table']}:\n"
                for row in table_info['data']:
                    if row:  # 空行をスキップ
                        result['text'] += " | ".join(str(cell)
                                                     if cell else "" for cell in row) + "\n"

        return result
    except Exception as e:
        return f"PDF読み取りエラー: {str(e)}"


def extract_data_from_excel(file_path):
    """Excelファイルからデータを抽出"""
    try:
        df = pd.read_excel(file_path, engine='openpyxl')
        # データフレームを辞書形式に変換
        data = df.to_dict('records')
        return {
            'headers': df.columns.tolist(),
            'data': data,
            'summary': f"{len(df)}行 × {len(df.columns)}列のデータ"
        }
    except Exception as e:
        return f"Excel読み取りエラー: {str(e)}"


def extract_data_from_csv(file_path):
    """CSVファイルからデータを抽出"""
    try:
        df = pd.read_csv(file_path, encoding='utf-8')
        data = df.to_dict('records')
        return {
            'headers': df.columns.tolist(),
            'data': data,
            'summary': f"{len(df)}行 × {len(df.columns)}列のデータ"
        }
    except UnicodeDecodeError:
        # UTF-8で読めない場合はShift_JISを試す
        try:
            df = pd.read_csv(file_path, encoding='shift_jis')
            data = df.to_dict('records')
            return {
                'headers': df.columns.tolist(),
                'data': data,
                'summary': f"{len(df)}行 × {len(df.columns)}列のデータ"
            }
        except Exception as e:
            return f"CSV読み取りエラー: {str(e)}"
    except Exception as e:
        return f"CSV読み取りエラー: {str(e)}"


def process_file_content(file_upload):
    """ファイル形式に応じてコンテンツを処理"""
    file_extension = get_file_extension(file_upload.original_name)
    
    # DB保存形式（file_data）から読み込み
    if file_upload.file_data:
        # Base64デコードしてファイルコンテンツを取得
        file_content = base64.b64decode(file_upload.file_data)
        
        # 画像ファイル（JPEG, PNG）の場合
        if file_extension in ['.jpg', '.jpeg', '.png']:
            return {
                'type': 'image',
                'base64': file_upload.file_data,  # すでにBase64エンコード済み
                'media_type': file_upload.mime_type
            }
    # 旧形式（FileField）からの読み込み（互換性のため）
    elif file_upload.file:
        file_path = file_upload.file.path
        
        # 画像ファイル（JPEG, PNG）の場合
        if file_extension in ['.jpg', '.jpeg', '.png']:
            try:
                # 画像をBase64エンコード
                with open(file_path, 'rb') as f:
                    file_content = f.read()
                    file_base64 = base64.b64encode(file_content).decode('utf-8')

                return {
                    'type': 'image',
                    'base64': file_base64,
                    'media_type': file_upload.mime_type
                }
            except Exception as e:
                return {'type': 'error', 'message': f"画像処理エラー: {str(e)}"}

    # PDFファイルの場合
    elif file_extension == '.pdf':
        pdf_result = extract_text_from_pdf(file_path)
        if isinstance(pdf_result, dict):
            # 画像ベースPDFの場合
            if pdf_result.get('type') == 'image_based_pdf':
                return {
                    'type': 'image_based_pdf',
                    'images': pdf_result.get('images', []),
                    'content': pdf_result['text'],
                    'tables': pdf_result.get('tables', []),
                    'has_tables': pdf_result.get('has_tables', False)
                }
            # 通常のテキストベースPDFの場合
            else:
                return {
                    'type': 'text',
                    'content': pdf_result['text'],
                    'tables': pdf_result.get('tables', []),
                    'has_tables': pdf_result.get('has_tables', False)
                }
        else:
            return {
                'type': 'error',
                'message': pdf_result
            }

    # Excelファイルの場合
    elif file_extension in ['.xlsx', '.xlsm', '.xls']:
        excel_data = extract_data_from_excel(file_path)
        return {
            'type': 'excel',
            'content': excel_data
        }

    # CSVファイルの場合
    elif file_extension == '.csv':
        csv_data = extract_data_from_csv(file_path)
        return {
            'type': 'csv',
            'content': csv_data
        }

    else:
        return {
            'type': 'error',
            'message': f"サポートされていないファイル形式: {file_extension}"
        }


class FileUploadListCreateView(generics.ListCreateAPIView):
    """ファイルアップロード一覧・作成API"""
    serializer_class = FileUploadSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # シードユーザーは全ファイルを表示可能
        if self.request.user.user_type == 'seed':
            # all_files=trueクエリパラメータがある場合は全ファイルを返す
            if self.request.query_params.get('all_files') == 'true':
                return FileUpload.objects.all().order_by('-created_at')
            else:
                return FileUpload.objects.filter(uploader=self.request.user)
        else:
            # 通常ユーザーは自分のファイルのみ
            return FileUpload.objects.filter(uploader=self.request.user)
    
    def create(self, request, *args, **kwargs):
        """ファイルアップロード処理（DB保存）"""
        file = request.FILES.get('file')
        if not file:
            return Response({'error': 'ファイルが指定されていません。'}, status=status.HTTP_400_BAD_REQUEST)
        
        # ファイルサイズチェック（10MB制限）
        if file.size > 10 * 1024 * 1024:  # 10MB
            return Response({'error': 'ファイルサイズは10MB以下にしてください。'}, status=status.HTTP_400_BAD_REQUEST)
        
        # ファイルをBase64エンコード
        file_content = file.read()
        file_base64 = base64.b64encode(file_content).decode('utf-8')
        
        # FileUploadオブジェクト作成
        file_upload = FileUpload.objects.create(
            uploader=request.user,
            file_data=file_base64,
            original_name=file.name,
            file_type=request.POST.get('file_type', 'delivery_document'),
            file_size=file.size,
            mime_type=file.content_type or 'application/octet-stream'
        )
        
        serializer = self.get_serializer(file_upload)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class FileUploadDetailView(generics.RetrieveDestroyAPIView):
    """ファイルアップロード詳細API"""
    serializer_class = FileUploadSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return FileUpload.objects.filter(uploader=self.request.user)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def process_with_claude(request, pk):
    """Claude APIで帳票を処理するAPI"""
    try:
        file_upload = FileUpload.objects.get(pk=pk, uploader=request.user)
    except FileUpload.DoesNotExist:
        return Response({'error': 'ファイルが見つかりません。'}, status=status.HTTP_404_NOT_FOUND)

    if file_upload.is_processed:
        return Response({'error': '既に処理済みです。'}, status=status.HTTP_400_BAD_REQUEST)

    # Claude APIキーの確認
    if not settings.CLAUDE_API_KEY:
        return Response({'error': 'Claude APIキーが設定されていません。'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    try:
        # ファイル形式に応じてコンテンツを処理
        processed_content = process_file_content(file_upload)

        if processed_content['type'] == 'error':
            return Response({
                'error': processed_content['message']
            }, status=status.HTTP_400_BAD_REQUEST)

        # Claude APIリクエスト
        headers = {
            'Content-Type': 'application/json',
            'x-api-key': settings.CLAUDE_API_KEY,
            'anthropic-version': '2023-06-01'
        }

        # ファイル形式に応じたプロンプトを生成
        if processed_content['type'] == 'image':
            # 画像ファイルの場合
            prompt = """
This is a Japanese delivery instruction document or delivery-related image. Please extract the following information and return it in JSON format:

{
  "sender_name": "Sender's name",
  "sender_phone": "Sender's phone number",
  "sender_address": "Sender's address",
  "recipient_name": "Recipient's name",
  "recipient_phone": "Recipient's phone number",
  "recipient_address": "Delivery address",
  "item_name": "Item name",
  "item_quantity": "Quantity (numeric value)",
  "delivery_date": "Preferred delivery date (YYYY-MM-DD format)",
  "delivery_time": "Preferred delivery time",
  "special_instructions": "Special instructions",
  "request_amount": "Request amount (numeric value, extract monetary value if present)"
}

The document may be rotated or handwritten. For items that cannot be read, please use empty strings.
"""

            payload = {
                "model": "claude-sonnet-4-20250514",
                "max_tokens": 1000,
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": prompt
                            },
                            {
                                "type": "image",
                                "source": {
                                    "type": "base64",
                                    "media_type": processed_content['media_type'],
                                    "data": processed_content['base64']
                                }
                            }
                        ]
                    }
                ]
            }

        elif processed_content['type'] == 'image_based_pdf':
            # 画像ベースPDFの場合
            prompt = """
This is a scanned PDF containing Japanese delivery instruction documents. Please analyze all the images and extract the following information in JSON format:

{
  "sender_name": "Sender's name",
  "sender_phone": "Sender's phone number",
  "sender_address": "Sender's address",
  "recipient_name": "Recipient's name",
  "recipient_phone": "Recipient's phone number",
  "recipient_address": "Delivery address",
  "item_name": "Item name",
  "item_quantity": "Quantity (numeric value)",
  "delivery_date": "Preferred delivery date (YYYY-MM-DD format)",
  "delivery_time": "Preferred delivery time",
  "special_instructions": "Special instructions",
  "request_amount": "Request amount (numeric value, extract monetary value if present)"
}

The images may contain rotated or handwritten text. Please analyze all provided images carefully.
For items that cannot be read, please use empty strings.
"""

            # 最初の画像を使用（複数ある場合は最大の画像を選択）
            images = processed_content.get('images', [])
            if not images:
                return Response({
                    'error': 'PDF内に画像が見つかりませんでした。'
                }, status=status.HTTP_400_BAD_REQUEST)

            # 最初の画像を使用
            first_image = images[0]
            
            payload = {
                "model": "claude-sonnet-4-20250514",
                "max_tokens": 1000,
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": prompt
                            },
                            {
                                "type": "image",
                                "source": {
                                    "type": "base64",
                                    "media_type": "image/png",
                                    "data": first_image['data']
                                }
                            }
                        ]
                    }
                ]
            }

        elif processed_content['type'] == 'text':
            # PDFテキストの場合
            has_tables = processed_content.get('has_tables', False)
            table_info = "This includes tabular data." if has_tables else ""

            prompt = f"""
The following is text extracted from a Japanese delivery instruction document or PDF. {table_info}Please extract the following information and return it in JSON format:

{{
  "sender_name": "Sender's name",
  "sender_phone": "Sender's phone number", 
  "sender_address": "Sender's address",
  "recipient_name": "Recipient's name",
  "recipient_phone": "Recipient's phone number",
  "recipient_address": "Delivery address",
  "item_name": "Item name",
  "item_quantity": "Quantity (numeric value)",
  "delivery_date": "Preferred delivery date (YYYY-MM-DD format)",
  "delivery_time": "Preferred delivery time",
  "special_instructions": "Special instructions",
  "request_amount": "Request amount (numeric value, extract monetary value if present)"
}}

If there is table data, please extract information from it as well.
For items that cannot be read, please use empty strings.

Text content:
{processed_content['content']}
"""

            payload = {
                "model": "claude-sonnet-4-20250514",
                "max_tokens": 1000,
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": prompt
                            }
                        ]
                    }
                ]
            }

        elif processed_content['type'] in ['excel', 'csv']:
            # Excel/CSVファイルの場合
            data_str = json.dumps(
                processed_content['content'], ensure_ascii=False, indent=2)
            prompt = f"""
The following is data extracted from a Japanese delivery-related Excel/CSV file. Please analyze the delivery information and extract the following information in JSON format:

{{
  "sender_name": "Sender's name",
  "sender_phone": "Sender's phone number",
  "sender_address": "Sender's address", 
  "recipient_name": "Recipient's name",
  "recipient_phone": "Recipient's phone number",
  "recipient_address": "Delivery address",
  "item_name": "Item name",
  "item_quantity": "Quantity (numeric value)",
  "delivery_date": "Preferred delivery date (YYYY-MM-DD format)",
  "delivery_time": "Preferred delivery time",
  "special_instructions": "Special instructions",
  "request_amount": "Request amount (numeric value, extract monetary value if present)"
}}

If there are multiple delivery requests, please extract information from the first one.
For items that cannot be read, please use empty strings.

Data content:
{data_str}
"""

            payload = {
                "model": "claude-sonnet-4-20250514",
                "max_tokens": 1000,
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": prompt
                            }
                        ]
                    }
                ]
            }

        response = requests.post(
            settings.CLAUDE_API_URL, headers=headers, json=payload)

        if response.status_code == 200:
            claude_response = response.json()

            # レスポンスからJSONデータを抽出
            try:
                content = claude_response['content'][0]['text']
                # JSONブロックを抽出（```json ... ``` の中身）
                if '```json' in content:
                    json_start = content.find('```json') + 7
                    json_end = content.find('```', json_start)
                    json_str = content[json_start:json_end].strip()
                else:
                    json_str = content.strip()

                extracted_data = json.loads(json_str)

                # データベースに保存
                file_upload.claude_response = claude_response
                file_upload.extracted_data = extracted_data
                file_upload.is_processed = True
                file_upload.save()

                return Response({
                    'message': 'Claude APIで処理が完了しました。',
                    'extracted_data': extracted_data
                })

            except (json.JSONDecodeError, KeyError) as e:
                file_upload.claude_response = claude_response
                file_upload.save()
                return Response({
                    'error': 'Claude APIのレスポンスの解析に失敗しました。',
                    'raw_response': claude_response
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response({
                'error': f'Claude API呼び出しに失敗しました。ステータスコード: {response.status_code}',
                'details': response.text
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    except Exception as e:
        return Response({
            'error': f'処理中にエラーが発生しました: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def create_delivery_from_file(request, pk):
    """ファイルから配送依頼を作成するAPI"""
    try:
        file_upload = FileUpload.objects.get(pk=pk, uploader=request.user)
    except FileUpload.DoesNotExist:
        return Response({'error': 'ファイルが見つかりません。'}, status=status.HTTP_404_NOT_FOUND)

    if not file_upload.is_processed or not file_upload.extracted_data:
        return Response({'error': 'ファイルがまだ処理されていません。'}, status=status.HTTP_400_BAD_REQUEST)

    from apps.delivery.models import DeliveryRequest
    from apps.delivery.serializers import DeliveryRequestSerializer

    # 抽出データから配送依頼を作成
    extracted_data = file_upload.extracted_data

    delivery_data = {
        'title': extracted_data.get('item_name', 'ファイルから作成された配送依頼'),
        'sender_name': extracted_data.get('sender_name', ''),
        'sender_phone': extracted_data.get('sender_phone', ''),
        'sender_address': extracted_data.get('sender_address', ''),
        'recipient_name': extracted_data.get('recipient_name', ''),
        'recipient_phone': extracted_data.get('recipient_phone', ''),
        'recipient_address': extracted_data.get('recipient_address', ''),
        'item_name': extracted_data.get('item_name', ''),
        'item_quantity': extracted_data.get('item_quantity', 1),
        'delivery_date': extracted_data.get('delivery_date', ''),
        'delivery_time': extracted_data.get('delivery_time', ''),
        'special_instructions': extracted_data.get('special_instructions', ''),
        'request_amount': extracted_data.get('request_amount', None),
        'requester': request.user
    }

    try:
        delivery_request = DeliveryRequest.objects.create(**delivery_data)

        # ファイルと配送依頼を関連付け
        file_upload.delivery_request = delivery_request
        file_upload.save()

        serializer = DeliveryRequestSerializer(delivery_request)
        return Response({
            'message': '配送依頼を作成しました。',
            'delivery_request': serializer.data
        }, status=status.HTTP_201_CREATED)

    except Exception as e:
        return Response({
            'error': f'配送依頼の作成に失敗しました: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def download_file(request, pk):
    """ファイルダウンロードAPI"""
    try:
        # ユーザーの権限チェック
        if request.user.user_type == 'seed':
            # シードユーザーは全ファイルダウンロード可能
            file_upload = FileUpload.objects.get(pk=pk)
        else:
            # 通常ユーザーは自分のファイルのみ
            file_upload = FileUpload.objects.get(pk=pk, uploader=request.user)
    except FileUpload.DoesNotExist:
        return Response({'error': 'ファイルが見つかりません。'}, status=status.HTTP_404_NOT_FOUND)
    
    # ファイルデータの取得
    if file_upload.file_data:
        # DB保存形式からデコード
        file_content = base64.b64decode(file_upload.file_data)
    elif file_upload.file:
        # 旧形式（FileField）から読み込み
        try:
            with open(file_upload.file.path, 'rb') as f:
                file_content = f.read()
        except Exception as e:
            return Response({'error': f'ファイル読み込みエラー: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        return Response({'error': 'ファイルデータが存在しません。'}, status=status.HTTP_404_NOT_FOUND)
    
    # HTTPレスポンスとして返す
    response = HttpResponse(file_content, content_type=file_upload.mime_type)
    response['Content-Disposition'] = f'attachment; filename="{file_upload.original_name}"'
    response['Content-Length'] = file_upload.file_size
    
    return response
