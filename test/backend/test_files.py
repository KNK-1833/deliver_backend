import pytest
import os
import json
from unittest.mock import patch, Mock
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework import status
from apps.files.models import FileUpload
from apps.delivery.models import DeliveryRequest


@pytest.mark.django_db
class TestFileUpload:
    """ファイルアップロードのテスト"""

    def test_file_upload_success(self, authenticated_client):
        """ファイルアップロード成功のテスト"""
        client, user = authenticated_client
        
        # テスト用ファイルを作成
        file_content = b"test file content"
        uploaded_file = SimpleUploadedFile(
            "test.jpg",
            file_content,
            content_type="image/jpeg"
        )
        
        url = reverse('file-upload-list')
        data = {'file': uploaded_file, 'file_type': 'delivery_document'}
        response = client.post(url, data, format='multipart')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['original_name'] == 'test.jpg'
        assert response.data['file_type'] == 'delivery_document'
        assert response.data['uploader'] == str(user)
        
        # データベース確認
        file_upload = FileUpload.objects.get(id=response.data['id'])
        assert file_upload.uploader == user
        assert file_upload.original_name == 'test.jpg'
        assert file_upload.file_size == len(file_content)

    def test_file_upload_with_actual_image(self, authenticated_client):
        """実際の画像ファイルアップロードのテスト"""
        client, user = authenticated_client
        
        # テスト用の画像ファイルパス
        image_path = os.path.join(os.path.dirname(__file__), 'camera_image.jpg')
        
        # ファイルが存在することを確認
        assert os.path.exists(image_path), f"Test image file not found: {image_path}"
        
        with open(image_path, 'rb') as f:
            uploaded_file = SimpleUploadedFile(
                "camera_image.jpg",
                f.read(),
                content_type="image/jpeg"
            )
        
        url = reverse('file-upload-list')
        data = {'file': uploaded_file, 'file_type': 'delivery_document'}
        response = client.post(url, data, format='multipart')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['original_name'] == 'camera_image.jpg'
        assert response.data['mime_type'] == 'image/jpeg'

    def test_file_list(self, authenticated_client):
        """ファイル一覧取得のテスト"""
        client, user = authenticated_client
        
        # テスト用ファイルを作成
        file_upload = FileUpload.objects.create(
            uploader=user,
            original_name='test.jpg',
            file_type='delivery_document',
            file_size=1024,
            mime_type='image/jpeg'
        )
        
        url = reverse('file-upload-list')
        response = client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 1
        assert response.data['results'][0]['id'] == file_upload.id

    def test_file_list_user_isolation(self, authenticated_client, create_user):
        """ファイル一覧のユーザー分離テスト"""
        client, user = authenticated_client
        
        # 自分のファイル
        my_file = FileUpload.objects.create(
            uploader=user,
            original_name='my_file.jpg',
            file_type='delivery_document',
            file_size=1024,
            mime_type='image/jpeg'
        )
        
        # 他人のファイル
        other_user = create_user(email='other@example.com')
        other_file = FileUpload.objects.create(
            uploader=other_user,
            original_name='other_file.jpg',
            file_type='delivery_document',
            file_size=1024,
            mime_type='image/jpeg'
        )
        
        url = reverse('file-upload-list')
        response = client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 1  # 自分のファイルのみ
        assert response.data['results'][0]['id'] == my_file.id

    def test_file_detail(self, authenticated_client):
        """ファイル詳細取得のテスト"""
        client, user = authenticated_client
        
        file_upload = FileUpload.objects.create(
            uploader=user,
            original_name='test.jpg',
            file_type='delivery_document',
            file_size=1024,
            mime_type='image/jpeg'
        )
        
        url = reverse('file-upload-detail', kwargs={'pk': file_upload.id})
        response = client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['id'] == file_upload.id

    def test_file_delete(self, authenticated_client):
        """ファイル削除のテスト"""
        client, user = authenticated_client
        
        file_upload = FileUpload.objects.create(
            uploader=user,
            original_name='test.jpg',
            file_type='delivery_document',
            file_size=1024,
            mime_type='image/jpeg'
        )
        
        url = reverse('file-upload-detail', kwargs={'pk': file_upload.id})
        response = client.delete(url)
        
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not FileUpload.objects.filter(id=file_upload.id).exists()

    def test_unauthorized_file_access(self, api_client):
        """未認証でのファイルアクセス拒否テスト"""
        url = reverse('file-upload-list')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestClaudeAPIIntegration:
    """Claude API連携のテスト"""

    @patch('apps.files.views.requests.post')
    def test_process_with_claude_success(self, mock_post, authenticated_client, mock_claude_response, sample_extracted_data):
        """Claude API処理成功のテスト"""
        client, user = authenticated_client
        
        # ファイルアップロードを作成
        file_upload = FileUpload.objects.create(
            uploader=user,
            original_name='test_document.jpg',
            file_type='delivery_document',
            file_size=1024,
            mime_type='image/jpeg',
            file='test/path/file.jpg'
        )
        
        # Claude APIのレスポンスをモック
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_claude_response
        mock_post.return_value = mock_response
        
        url = reverse('process-with-claude', kwargs={'pk': file_upload.id})
        response = client.post(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert 'message' in response.data
        assert 'extracted_data' in response.data
        assert response.data['extracted_data']['sender_name'] == sample_extracted_data['sender_name']
        
        # データベース更新確認
        file_upload.refresh_from_db()
        assert file_upload.is_processed is True
        assert file_upload.claude_response == mock_claude_response
        assert file_upload.extracted_data == sample_extracted_data
        
        # Claude APIが正しく呼び出されたか確認
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        assert call_args[0][0] == 'https://api.anthropic.com/v1/messages'  # URL
        assert 'x-api-key' in call_args[1]['headers']
        assert call_args[1]['headers']['x-api-key'] == 'test-api-key'

    @patch('apps.files.views.requests.post')
    def test_process_with_claude_api_error(self, mock_post, authenticated_client):
        """Claude API エラーのテスト"""
        client, user = authenticated_client
        
        file_upload = FileUpload.objects.create(
            uploader=user,
            original_name='test_document.jpg',
            file_type='delivery_document',
            file_size=1024,
            mime_type='image/jpeg',
            file='test/path/file.jpg'
        )
        
        # Claude APIのエラーレスポンスをモック
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.text = 'Bad Request'
        mock_post.return_value = mock_response
        
        url = reverse('process-with-claude', kwargs={'pk': file_upload.id})
        response = client.post(url)
        
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert 'error' in response.data

    def test_process_already_processed_file(self, authenticated_client, sample_extracted_data):
        """既に処理済みのファイル処理失敗テスト"""
        client, user = authenticated_client
        
        file_upload = FileUpload.objects.create(
            uploader=user,
            original_name='test_document.jpg',
            file_type='delivery_document',
            file_size=1024,
            mime_type='image/jpeg',
            file='test/path/file.jpg',
            is_processed=True,
            extracted_data=sample_extracted_data
        )
        
        url = reverse('process-with-claude', kwargs={'pk': file_upload.id})
        response = client.post(url)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'error' in response.data

    def test_process_nonexistent_file(self, authenticated_client):
        """存在しないファイル処理失敗テスト"""
        client, user = authenticated_client
        
        url = reverse('process-with-claude', kwargs={'pk': 99999})
        response = client.post(url)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND

    @patch('apps.files.views.requests.post')
    def test_process_with_claude_json_parse_error(self, mock_post, authenticated_client):
        """Claude APIレスポンスのJSON解析エラーテスト"""
        client, user = authenticated_client
        
        file_upload = FileUpload.objects.create(
            uploader=user,
            original_name='test_document.jpg',
            file_type='delivery_document',
            file_size=1024,
            mime_type='image/jpeg',
            file='test/path/file.jpg'
        )
        
        # 無効なJSONレスポンスをモック
        invalid_response = {
            'content': [{'text': 'Invalid JSON response'}]
        }
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = invalid_response
        mock_post.return_value = mock_response
        
        url = reverse('process-with-claude', kwargs={'pk': file_upload.id})
        response = client.post(url)
        
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert 'error' in response.data

    @patch('apps.files.views.settings.CLAUDE_API_KEY', None)
    def test_process_without_api_key(self, authenticated_client):
        """Claude APIキー未設定のテスト"""
        client, user = authenticated_client
        
        file_upload = FileUpload.objects.create(
            uploader=user,
            original_name='test_document.jpg',
            file_type='delivery_document',
            file_size=1024,
            mime_type='image/jpeg',
            file='test/path/file.jpg'
        )
        
        url = reverse('process-with-claude', kwargs={'pk': file_upload.id})
        response = client.post(url)
        
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert 'Claude APIキーが設定されていません' in response.data['error']


@pytest.mark.django_db
class TestDeliveryFromFile:
    """ファイルから配送依頼作成のテスト"""

    def test_create_delivery_from_file_success(self, authenticated_client, sample_extracted_data):
        """ファイルから配送依頼作成成功のテスト"""
        client, user = authenticated_client
        
        file_upload = FileUpload.objects.create(
            uploader=user,
            original_name='test_document.jpg',
            file_type='delivery_document',
            file_size=1024,
            mime_type='image/jpeg',
            file='test/path/file.jpg',
            is_processed=True,
            extracted_data=sample_extracted_data
        )
        
        url = reverse('create-delivery-from-file', kwargs={'pk': file_upload.id})
        response = client.post(url)
        
        assert response.status_code == status.HTTP_201_CREATED
        assert 'message' in response.data
        assert 'delivery_request' in response.data
        
        # 配送依頼が作成されているか確認
        delivery_request = DeliveryRequest.objects.get(
            id=response.data['delivery_request']['id']
        )
        assert delivery_request.requester == user
        assert delivery_request.sender_name == sample_extracted_data['sender_name']
        assert delivery_request.recipient_name == sample_extracted_data['recipient_name']
        assert delivery_request.item_name == sample_extracted_data['item_name']
        
        # ファイルと配送依頼の関連付け確認
        file_upload.refresh_from_db()
        assert file_upload.delivery_request == delivery_request

    def test_create_delivery_from_unprocessed_file(self, authenticated_client):
        """未処理ファイルから配送依頼作成失敗のテスト"""
        client, user = authenticated_client
        
        file_upload = FileUpload.objects.create(
            uploader=user,
            original_name='test_document.jpg',
            file_type='delivery_document',
            file_size=1024,
            mime_type='image/jpeg',
            file='test/path/file.jpg',
            is_processed=False
        )
        
        url = reverse('create-delivery-from-file', kwargs={'pk': file_upload.id})
        response = client.post(url)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'ファイルがまだ処理されていません' in response.data['error']

    def test_create_delivery_from_file_without_extracted_data(self, authenticated_client):
        """抽出データなしファイルから配送依頼作成失敗のテスト"""
        client, user = authenticated_client
        
        file_upload = FileUpload.objects.create(
            uploader=user,
            original_name='test_document.jpg',
            file_type='delivery_document',
            file_size=1024,
            mime_type='image/jpeg',
            file='test/path/file.jpg',
            is_processed=True,
            extracted_data=None
        )
        
        url = reverse('create-delivery-from-file', kwargs={'pk': file_upload.id})
        response = client.post(url)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'ファイルがまだ処理されていません' in response.data['error']

    def test_create_delivery_from_nonexistent_file(self, authenticated_client):
        """存在しないファイルから配送依頼作成失敗のテスト"""
        client, user = authenticated_client
        
        url = reverse('create-delivery-from-file', kwargs={'pk': 99999})
        response = client.post(url)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND