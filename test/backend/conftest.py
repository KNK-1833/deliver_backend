import os
import sys
import pytest

# プロジェクトのバックエンドディレクトリをPythonパスに追加
backend_path = os.path.join(os.path.dirname(__file__), '../../backend')
sys.path.insert(0, backend_path)

# Django設定
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

import django
from django.conf import settings
django.setup()

from django.test import override_settings
from rest_framework.test import APIClient

from django.contrib.auth import get_user_model
from apps.users.models import DriverProfile
from apps.delivery.models import DeliveryRequest, Assignment
from apps.files.models import FileUpload

User = get_user_model()


@pytest.fixture
def api_client():
    """APIクライアントのフィクスチャ"""
    return APIClient()


@pytest.fixture
def user_data():
    """ユーザー作成用のテストデータ"""
    return {
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'testpass123',
        'password_confirm': 'testpass123',
        'phone_number': '090-1234-5678',
        'user_type': 'company'
    }


@pytest.fixture
def driver_data():
    """ドライバー作成用のテストデータ"""
    return {
        'username': 'testdriver',
        'email': 'driver@example.com',
        'password': 'testpass123',
        'password_confirm': 'testpass123',
        'phone_number': '090-9876-5432',
        'user_type': 'driver'
    }


@pytest.fixture
def create_user(db):
    """ユーザー作成ヘルパー"""
    counter = 0
    def _create_user(email=None, user_type='company', **kwargs):
        nonlocal counter
        counter += 1
        if email is None:
            email = f'test{counter}@example.com'
        defaults = {
            'username': f'testuser{counter}',
            'email': email,
            'user_type': user_type,
            'phone_number': '090-1234-5678'
        }
        defaults.update(kwargs)
        user = User.objects.create_user(**defaults)
        user.set_password('testpass123')
        user.save()
        return user
    return _create_user


@pytest.fixture
def create_driver(db):
    """ドライバー作成ヘルパー"""
    counter = 0
    def _create_driver(email=None, **kwargs):
        nonlocal counter
        counter += 1
        if email is None:
            email = f'driver{counter}@example.com'
        defaults = {
            'username': f'testdriver{counter}',
            'email': email,
            'user_type': 'driver',
            'phone_number': '090-9876-5432'
        }
        defaults.update(kwargs)
        user = User.objects.create_user(**defaults)
        user.set_password('testpass123')
        user.save()
        
        # ドライバープロフィール作成
        DriverProfile.objects.create(
            user=user,
            vehicle_type='motorcycle',
            is_available=True
        )
        return user
    return _create_driver


@pytest.fixture
def authenticated_client(api_client, create_user):
    """認証済みクライアント"""
    user = create_user()
    api_client.force_authenticate(user=user)
    return api_client, user


@pytest.fixture
def authenticated_driver_client(api_client, create_driver):
    """認証済みドライバークライアント"""
    driver = create_driver()
    api_client.force_authenticate(user=driver)
    return api_client, driver


@pytest.fixture
def delivery_request_data():
    """配送依頼作成用のテストデータ"""
    return {
        'title': 'テスト配送依頼',
        'description': 'テスト用の配送依頼です',
        'sender_name': '送付太郎',
        'sender_phone': '03-1234-5678',
        'sender_address': '東京都渋谷区1-1-1',
        'recipient_name': '受取花子',
        'recipient_phone': '03-9876-5432',
        'recipient_address': '東京都新宿区2-2-2',
        'item_name': 'テスト商品',
        'item_quantity': 1,
        'delivery_date': '2024-12-31',
        'delivery_time': '午前中',
        'special_instructions': '特別な指示なし'
    }


@pytest.fixture
def sample_extracted_data():
    """Claude APIから抽出されたサンプルデータ"""
    return {
        'sender_name': '山田太郎',
        'sender_phone': '03-1111-2222',
        'sender_address': '東京都港区1-1-1',
        'recipient_name': '佐藤花子',
        'recipient_phone': '03-3333-4444',
        'recipient_address': '東京都品川区2-2-2',
        'item_name': 'ドキュメント',
        'item_quantity': 1,
        'delivery_date': '2024-12-25',
        'delivery_time': '14:00-16:00',
        'special_instructions': '直接手渡し希望'
    }


@pytest.fixture
def mock_claude_response():
    """Claude APIのモックレスポンス"""
    return {
        'id': 'msg_test123',
        'type': 'message',
        'role': 'assistant',
        'content': [
            {
                'type': 'text',
                'text': '''```json
{
  "sender_name": "山田太郎",
  "sender_phone": "03-1111-2222",
  "sender_address": "東京都港区1-1-1",
  "recipient_name": "佐藤花子",
  "recipient_phone": "03-3333-4444",
  "recipient_address": "東京都品川区2-2-2",
  "item_name": "ドキュメント",
  "item_quantity": 1,
  "delivery_date": "2024-12-25",
  "delivery_time": "14:00-16:00",
  "special_instructions": "直接手渡し希望"
}
```'''
            }
        ],
        'model': 'claude-3-sonnet-20240229',
        'stop_reason': 'end_turn',
        'usage': {
            'input_tokens': 100,
            'output_tokens': 150
        }
    }


# テスト用設定のオーバーライド
@pytest.fixture(autouse=True)
def use_test_settings():
    """テスト用設定の適用"""
    with override_settings(
        DATABASES={
            'default': {
                'ENGINE': 'django.db.backends.postgresql',
                'NAME': 'test_delivery_support',
                'USER': 'postgres',
                'PASSWORD': 'password',
                'HOST': 'localhost',
                'PORT': '5432',
                'TEST': {
                    'NAME': 'test_delivery_support_test',
                },
            }
        },
        CLAUDE_API_KEY='test-api-key',
        EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend',
        MEDIA_ROOT='/tmp/test_media',
        CELERY_ALWAYS_EAGER=True
    ):
        yield