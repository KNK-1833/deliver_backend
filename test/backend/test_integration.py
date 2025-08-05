import pytest
from unittest.mock import patch, Mock
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework import status
from apps.delivery.models import DeliveryRequest, Assignment
from apps.files.models import FileUpload


@pytest.mark.django_db
class TestFullWorkflow:
    """完全なワークフローの統合テスト"""

    def test_complete_delivery_workflow(self, api_client, user_data, driver_data, delivery_request_data):
        """完全な配送ワークフローのテスト"""
        
        # 1. ユーザー（事業者）登録
        url = reverse('user-register')
        response = api_client.post(url, user_data, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        company_user_id = response.data['user']['id']
        
        # 2. ドライバー登録
        url = reverse('user-register')
        response = api_client.post(url, driver_data, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        driver_user_id = response.data['user']['id']
        
        # 3. 事業者ログイン
        url = reverse('token-obtain-pair')
        login_data = {'username': user_data['email'], 'password': user_data['password']}
        response = api_client.post(url, login_data, format='json')
        assert response.status_code == status.HTTP_200_OK
        company_token = response.data['access']
        
        # 4. ドライバーログイン
        url = reverse('token-obtain-pair')
        login_data = {'username': driver_data['email'], 'password': driver_data['password']}
        response = api_client.post(url, login_data, format='json')
        assert response.status_code == status.HTTP_200_OK
        driver_token = response.data['access']
        
        # 5. 事業者が配送依頼を作成
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {company_token}')
        url = reverse('delivery-request-list')
        response = api_client.post(url, delivery_request_data, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        delivery_request_id = response.data['id']
        assert response.data['status'] == 'pending'
        
        # 6. ドライバーが受付中の案件一覧を確認
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {driver_token}')
        url = reverse('delivery-request-list')
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 1
        assert response.data['results'][0]['id'] == delivery_request_id
        
        # 7. ドライバーが案件を受諾
        url = reverse('accept-delivery', kwargs={'pk': delivery_request_id})
        response = api_client.post(url)
        assert response.status_code == status.HTTP_201_CREATED
        assignment_id = response.data['assignment']['id']
        assert response.data['assignment']['status'] == 'accepted'
        
        # 8. 配送依頼のステータス確認（assigned になっているはず）
        url = reverse('delivery-request-detail', kwargs={'pk': delivery_request_id})
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['status'] == 'assigned'
        
        # 9. ドライバーが配送開始
        url = reverse('update-assignment-status', kwargs={'pk': assignment_id})
        data = {'status': 'in_progress'}
        response = api_client.post(url, data, format='json')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['assignment']['status'] == 'in_progress'
        
        # 10. ドライバーが配送完了
        url = reverse('update-assignment-status', kwargs={'pk': assignment_id})
        data = {'status': 'completed'}
        response = api_client.post(url, data, format='json')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['assignment']['status'] == 'completed'
        
        # 11. 最終ステータス確認
        url = reverse('delivery-request-detail', kwargs={'pk': delivery_request_id})
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['status'] == 'completed'
        
        # 12. 事業者がアサイン一覧を確認
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {company_token}')
        url = reverse('assignment-list')
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 1
        assert response.data['results'][0]['status'] == 'completed'

    @patch('apps.files.views.requests.post')
    def test_file_to_delivery_workflow(self, mock_post, api_client, user_data, mock_claude_response):
        """ファイルから配送依頼作成までのワークフロー"""
        
        # 1. ユーザー登録・ログイン
        url = reverse('user-register')
        response = api_client.post(url, user_data, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        
        url = reverse('token-obtain-pair')
        login_data = {'username': user_data['email'], 'password': user_data['password']}
        response = api_client.post(url, login_data, format='json')
        assert response.status_code == status.HTTP_200_OK
        token = response.data['access']
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        
        # 2. ファイルアップロード
        file_content = b"test image content"
        uploaded_file = SimpleUploadedFile(
            "delivery_document.jpg",
            file_content,
            content_type="image/jpeg"
        )
        
        url = reverse('file-upload-list')
        data = {'file': uploaded_file, 'file_type': 'delivery_document'}
        response = api_client.post(url, data, format='multipart')
        assert response.status_code == status.HTTP_201_CREATED
        file_id = response.data['id']
        
        # 3. Claude API処理
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_claude_response
        mock_post.return_value = mock_response
        
        url = reverse('process-with-claude', kwargs={'pk': file_id})
        response = api_client.post(url)
        assert response.status_code == status.HTTP_200_OK
        assert 'extracted_data' in response.data
        
        # 4. 抽出データから配送依頼作成
        url = reverse('create-delivery-from-file', kwargs={'pk': file_id})
        response = api_client.post(url)
        assert response.status_code == status.HTTP_201_CREATED
        assert 'delivery_request' in response.data
        
        delivery_request = response.data['delivery_request']
        assert delivery_request['sender_name'] == '山田太郎'
        assert delivery_request['recipient_name'] == '佐藤花子'
        assert delivery_request['item_name'] == 'ドキュメント'
        assert delivery_request['status'] == 'pending'
        
        # 5. 配送依頼一覧で確認
        url = reverse('delivery-request-list')
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 1
        assert response.data['results'][0]['id'] == delivery_request['id']

    def test_multiple_drivers_competition(self, api_client, user_data, delivery_request_data):
        """複数ドライバーの案件競合テスト"""
        
        # 1. 事業者とドライバー2人を作成
        # 事業者登録
        url = reverse('user-register')
        response = api_client.post(url, user_data, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        
        # ドライバー1登録
        driver1_data = {
            'username': 'driver1',
            'email': 'driver1@example.com',
            'password': 'testpass123',
            'password_confirm': 'testpass123',
            'user_type': 'driver'
        }
        response = api_client.post(url, driver1_data, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        
        # ドライバー2登録
        driver2_data = {
            'username': 'driver2',
            'email': 'driver2@example.com',
            'password': 'testpass123',
            'password_confirm': 'testpass123',
            'user_type': 'driver'
        }
        response = api_client.post(url, driver2_data, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        
        # 2. 事業者ログイン・配送依頼作成
        url = reverse('token-obtain-pair')
        login_data = {'username': user_data['email'], 'password': user_data['password']}
        response = api_client.post(url, login_data, format='json')
        company_token = response.data['access']
        
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {company_token}')
        url = reverse('delivery-request-list')
        response = api_client.post(url, delivery_request_data, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        delivery_request_id = response.data['id']
        
        # 3. ドライバー1ログイン・受諾
        url = reverse('token-obtain-pair')
        login_data = {'username': 'driver1@example.com', 'password': 'testpass123'}
        response = api_client.post(url, login_data, format='json')
        driver1_token = response.data['access']
        
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {driver1_token}')
        url = reverse('accept-delivery', kwargs={'pk': delivery_request_id})
        response = api_client.post(url)
        assert response.status_code == status.HTTP_201_CREATED
        
        # 4. ドライバー2ログイン・受諾試行（失敗するはず）
        url = reverse('token-obtain-pair')
        login_data = {'username': 'driver2@example.com', 'password': 'testpass123'}
        response = api_client.post(url, login_data, format='json')
        driver2_token = response.data['access']
        
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {driver2_token}')
        url = reverse('accept-delivery', kwargs={'pk': delivery_request_id})
        response = api_client.post(url)
        assert response.status_code == status.HTTP_404_NOT_FOUND  # 既にassignedなので見つからない
        
        # 5. ドライバー2の案件一覧確認（何も表示されないはず）
        url = reverse('delivery-request-list')
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 0  # 受付中の案件なし

    def test_user_permission_boundaries(self, api_client, user_data, driver_data, delivery_request_data):
        """ユーザー権限境界のテスト"""
        
        # 1. 事業者とドライバー作成・ログイン
        url = reverse('user-register')
        api_client.post(url, user_data, format='json')
        api_client.post(url, driver_data, format='json')
        
        # 事業者ログイン
        url = reverse('token-obtain-pair')
        login_data = {'username': user_data['email'], 'password': user_data['password']}
        response = api_client.post(url, login_data, format='json')
        company_token = response.data['access']
        
        # ドライバーログイン
        login_data = {'username': driver_data['email'], 'password': driver_data['password']}
        response = api_client.post(url, login_data, format='json')
        driver_token = response.data['access']
        
        # 2. 事業者が配送依頼作成
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {company_token}')
        url = reverse('delivery-request-list')
        response = api_client.post(url, delivery_request_data, format='json')
        delivery_request_id = response.data['id']
        
        # 3. 事業者がドライバープロフィールアクセス試行（失敗するはず）
        url = reverse('driver-profile')
        response = api_client.get(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN
        
        # 4. ドライバーが他人の配送依頼詳細アクセス試行
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {driver_token}')
        url = reverse('delivery-request-detail', kwargs={'pk': delivery_request_id})
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK  # ドライバーは全ての案件を見れる
        
        # 5. ドライバーが配送依頼作成試行
        url = reverse('delivery-request-list')
        response = api_client.post(url, delivery_request_data, format='json')
        assert response.status_code == status.HTTP_201_CREATED  # ドライバーも依頼作成可能
        
        # 6. 事業者が案件受諾試行（失敗するはず）
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {company_token}')
        url = reverse('accept-delivery', kwargs={'pk': delivery_request_id})
        response = api_client.post(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
class TestErrorHandling:
    """エラーハンドリングのテスト"""

    def test_invalid_token_handling(self, api_client):
        """無効なトークンのハンドリングテスト"""
        api_client.credentials(HTTP_AUTHORIZATION='Bearer invalid_token')
        
        url = reverse('user-profile')
        response = api_client.get(url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_expired_token_handling(self, api_client, create_user):
        """期限切れトークンのハンドリングテスト"""
        # このテストは実際の期限切れを再現するのが困難なため、
        # 無効なトークン形式での動作確認
        user = create_user()
        api_client.credentials(HTTP_AUTHORIZATION='Bearer expired.token.here')
        
        url = reverse('user-profile')
        response = api_client.get(url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_missing_required_fields(self, api_client):
        """必須フィールド不足のハンドリングテスト"""
        url = reverse('user-register')
        incomplete_data = {'username': 'test', 'email': 'test@example.com'}
        response = api_client.post(url, incomplete_data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_invalid_file_upload(self, authenticated_client):
        """無効なファイルアップロードのハンドリングテスト"""
        client, user = authenticated_client
        
        # 空のファイル
        uploaded_file = SimpleUploadedFile("empty.txt", b"", content_type="text/plain")
        
        url = reverse('file-upload-list')
        data = {'file': uploaded_file, 'file_type': 'delivery_document'}
        response = client.post(url, data, format='multipart')
        
        # 空ファイルでもアップロード自体は成功するはず
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['file_size'] == 0


@pytest.mark.django_db
class TestDataConsistency:
    """データ整合性のテスト"""

    def test_cascade_deletion(self, authenticated_client, delivery_request_data, create_driver):
        """カスケード削除のテスト"""
        client, user = authenticated_client
        driver = create_driver()
        
        # 配送依頼とアサインを作成
        delivery_request = DeliveryRequest.objects.create(
            requester=user,
            **delivery_request_data
        )
        assignment = Assignment.objects.create(
            delivery_request=delivery_request,
            driver=driver,
            status='accepted'
        )
        
        # 配送依頼を削除
        delivery_request.delete()
        
        # アサインも削除されているか確認
        assert not Assignment.objects.filter(id=assignment.id).exists()

    def test_user_deletion_impact(self, create_user, create_driver, delivery_request_data):
        """ユーザー削除の影響テスト"""
        user = create_user()
        driver = create_driver()
        
        # 配送依頼を作成
        delivery_request = DeliveryRequest.objects.create(
            requester=user,
            **delivery_request_data
        )
        
        # ファイルアップロードを作成
        file_upload = FileUpload.objects.create(
            uploader=user,
            original_name='test.jpg',
            file_type='delivery_document',
            file_size=1024,
            mime_type='image/jpeg'
        )
        
        # ユーザーを削除
        user.delete()
        
        # 関連データも削除されているか確認
        assert not DeliveryRequest.objects.filter(id=delivery_request.id).exists()
        assert not FileUpload.objects.filter(id=file_upload.id).exists()