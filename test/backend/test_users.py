import pytest
from django.urls import reverse
from rest_framework import status
from django.contrib.auth import get_user_model
from apps.users.models import DriverProfile

User = get_user_model()


@pytest.mark.django_db
class TestUserRegistration:
    """ユーザー登録のテスト"""

    def test_user_registration_success(self, api_client, user_data):
        """正常なユーザー登録のテスト"""
        url = reverse('user-register')
        response = api_client.post(url, user_data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert 'user' in response.data
        assert 'message' in response.data
        assert response.data['user']['email'] == user_data['email']
        assert response.data['user']['user_type'] == user_data['user_type']
        
        # データベースにユーザーが作成されているか確認
        user = User.objects.get(email=user_data['email'])
        assert user.username == user_data['username']
        assert user.check_password(user_data['password'])

    def test_driver_registration_creates_profile(self, api_client, driver_data):
        """ドライバー登録時にプロフィールが作成されることのテスト"""
        url = reverse('user-register')
        response = api_client.post(url, driver_data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        
        # ドライバープロフィールが作成されているか確認
        user = User.objects.get(email=driver_data['email'])
        assert hasattr(user, 'driver_profile')
        assert user.driver_profile.user == user

    def test_user_registration_password_mismatch(self, api_client, user_data):
        """パスワード不一致のテスト"""
        user_data['password_confirm'] = 'different_password'
        url = reverse('user-register')
        response = api_client.post(url, user_data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_user_registration_duplicate_email(self, api_client, user_data, create_user):
        """重複メールアドレスのテスト"""
        create_user(email=user_data['email'])
        
        url = reverse('user-register')
        response = api_client.post(url, user_data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestUserAuthentication:
    """ユーザー認証のテスト"""

    def test_token_obtain_success(self, api_client, create_user):
        """JWTトークン取得の成功テスト"""
        user = create_user(email='test@example.com')
        
        url = reverse('token-obtain-pair')
        data = {'username': 'test@example.com', 'password': 'testpass123'}
        response = api_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        assert 'access' in response.data
        assert 'refresh' in response.data

    def test_token_obtain_invalid_credentials(self, api_client, create_user):
        """無効な認証情報でのトークン取得失敗テスト"""
        create_user(email='test@example.com')
        
        url = reverse('token-obtain-pair')
        data = {'username': 'test@example.com', 'password': 'wrongpassword'}
        response = api_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_token_refresh_success(self, api_client, create_user):
        """トークンリフレッシュの成功テスト"""
        user = create_user(email='test@example.com')
        
        # まずトークンを取得
        url = reverse('token-obtain-pair')
        data = {'username': 'test@example.com', 'password': 'testpass123'}
        response = api_client.post(url, data, format='json')
        refresh_token = response.data['refresh']
        
        # リフレッシュを実行
        url = reverse('token-refresh')
        data = {'refresh': refresh_token}
        response = api_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        assert 'access' in response.data


@pytest.mark.django_db
class TestUserProfile:
    """ユーザープロフィールのテスト"""

    def test_get_user_profile(self, authenticated_client):
        """ユーザープロフィール取得のテスト"""
        client, user = authenticated_client
        
        url = reverse('user-profile')
        response = client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['id'] == user.id
        assert response.data['email'] == user.email

    def test_update_user_profile(self, authenticated_client):
        """ユーザープロフィール更新のテスト"""
        client, user = authenticated_client
        
        url = reverse('user-profile')
        data = {'phone_number': '090-0000-0000'}
        response = client.patch(url, data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['phone_number'] == '090-0000-0000'
        
        # データベースの更新確認
        user.refresh_from_db()
        assert user.phone_number == '090-0000-0000'

    def test_unauthenticated_profile_access(self, api_client):
        """未認証でのプロフィールアクセス拒否テスト"""
        url = reverse('user-profile')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestDriverProfile:
    """ドライバープロフィールのテスト"""

    def test_get_driver_profile(self, authenticated_driver_client):
        """ドライバープロフィール取得のテスト"""
        client, driver = authenticated_driver_client
        
        url = reverse('driver-profile')
        response = client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['user']['id'] == driver.id
        assert 'vehicle_type' in response.data

    def test_update_driver_profile(self, authenticated_driver_client):
        """ドライバープロフィール更新のテスト"""
        client, driver = authenticated_driver_client
        
        url = reverse('driver-profile')
        data = {
            'vehicle_type': 'truck',
            'vehicle_number': '品川 123 あ 4567',
            'is_available': False
        }
        response = client.patch(url, data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['vehicle_type'] == 'truck'
        assert response.data['vehicle_number'] == '品川 123 あ 4567'
        assert response.data['is_available'] is False

    def test_non_driver_profile_access(self, authenticated_client):
        """非ドライバーのプロフィールアクセス拒否テスト"""
        client, user = authenticated_client
        
        url = reverse('driver-profile')
        response = client.get(url)
        
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_available_drivers_list(self, api_client, create_driver):
        """稼働可能ドライバー一覧のテスト"""
        # 稼働可能なドライバーを作成
        driver1 = create_driver(email='driver1@example.com')
        driver2 = create_driver(email='driver2@example.com')
        
        # 稼働不可能なドライバーを作成
        driver3 = create_driver(email='driver3@example.com')
        driver3.driver_profile.is_available = False
        driver3.driver_profile.save()
        
        # 認証ユーザーでリクエスト
        api_client.force_authenticate(user=driver1)
        
        url = reverse('available-drivers')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 2  # 稼働可能なドライバーのみ
        
        emails = [item['user']['email'] for item in response.data]
        assert 'driver1@example.com' in emails
        assert 'driver2@example.com' in emails
        assert 'driver3@example.com' not in emails