#!/usr/bin/env python
"""
本番環境でのテストユーザー作成スクリプト
Railway等のクラウド環境で実行する想定
"""
import os
import sys
import django
from django.core.management import execute_from_command_line

# Django設定を読み込み
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model
from apps.users.models import DriverProfile

User = get_user_model()

def create_test_users():
    """テスト用ユーザーを作成"""
    
    # 1. 管理者ユーザー
    if not User.objects.filter(email='admin@delivery-test.com').exists():
        admin_user = User.objects.create_superuser(
            email='admin@delivery-test.com',
            password='AdminTest123!',
            first_name='管理者',
            last_name='テスト',
            user_type='business'
        )
        print(f"✅ 管理者ユーザー作成: {admin_user.email}")
    else:
        print("⚠️  管理者ユーザー既存: admin@delivery-test.com")
    
    # 2. 事業者ユーザー
    if not User.objects.filter(email='business@delivery-test.com').exists():
        business_user = User.objects.create_user(
            email='business@delivery-test.com',
            password='BusinessTest123!',
            first_name='事業者',
            last_name='テスト',
            user_type='business'
        )
        print(f"✅ 事業者ユーザー作成: {business_user.email}")
    else:
        print("⚠️  事業者ユーザー既存: business@delivery-test.com")
    
    # 3. ドライバーユーザー
    if not User.objects.filter(email='driver@delivery-test.com').exists():
        driver_user = User.objects.create_user(
            email='driver@delivery-test.com',
            password='DriverTest123!',
            first_name='ドライバー',
            last_name='テスト',
            user_type='driver'
        )
        
        # ドライバープロフィールを作成
        DriverProfile.objects.create(
            user=driver_user,
            license_number='TEST-12345',
            vehicle_type='軽トラック',
            phone_number='090-1234-5678',
            address='東京都渋谷区テスト1-2-3'
        )
        print(f"✅ ドライバーユーザー作成: {driver_user.email}")
        print("✅ ドライバープロフィール作成完了")
    else:
        print("⚠️  ドライバーユーザー既存: driver@delivery-test.com")
    
    # 4. 追加ドライバーユーザー
    if not User.objects.filter(email='driver2@delivery-test.com').exists():
        driver_user2 = User.objects.create_user(
            email='driver2@delivery-test.com',
            password='DriverTest123!',
            first_name='ドライバー2',
            last_name='テスト',
            user_type='driver'
        )
        
        # ドライバープロフィールを作成
        DriverProfile.objects.create(
            user=driver_user2,
            license_number='TEST-67890',
            vehicle_type='バン',
            phone_number='090-5678-9012',
            address='東京都新宿区テスト4-5-6'
        )
        print(f"✅ ドライバーユーザー2作成: {driver_user2.email}")
        print("✅ ドライバープロフィール2作成完了")
    else:
        print("⚠️  ドライバーユーザー2既存: driver2@delivery-test.com")
    
    print("\n" + "="*50)
    print("🎉 テストユーザー作成完了！")
    print("="*50)
    print("\n📋 作成されたアカウント:")
    print("1. 管理者:")
    print("   Email: admin@delivery-test.com")
    print("   Password: AdminTest123!")
    print("   URL: https://your-domain.railway.app/admin/")
    
    print("\n2. 事業者:")
    print("   Email: business@delivery-test.com")
    print("   Password: BusinessTest123!")
    
    print("\n3. ドライバー:")
    print("   Email: driver@delivery-test.com")
    print("   Password: DriverTest123!")
    
    print("\n4. ドライバー2:")
    print("   Email: driver2@delivery-test.com")
    print("   Password: DriverTest123!")
    
    print(f"\n📊 総ユーザー数: {User.objects.count()}")
    print(f"📊 ドライバー数: {DriverProfile.objects.count()}")

if __name__ == '__main__':
    try:
        create_test_users()
    except Exception as e:
        print(f"❌ エラー: {e}")
        sys.exit(1)