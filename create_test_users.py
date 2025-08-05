#!/usr/bin/env python
"""
本番環境でのテストユーザー作成スクリプト
Railway等のクラウド環境で実行する想定
"""
import os
import sys
import django

# Django設定を読み込み
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model
from apps.users.models import DriverProfile

User = get_user_model()

def create_test_users():
    """テスト用ユーザーを作成"""
    
    # 1. 管理者ユーザー
    try:
        if not User.objects.filter(email='admin@delivery-test.com').exists():
            # 既存のusernameをチェック
            username = 'admin_test'
            counter = 1
            while User.objects.filter(username=username).exists():
                username = f'admin_test_{counter}'
                counter += 1
            
            admin_user = User.objects.create_superuser(
                username=username,
                email='admin@delivery-test.com',
                password='AdminTest123!',
                first_name='管理者',
                last_name='テスト',
                user_type='company'
            )
            print(f"✅ 管理者ユーザー作成: {admin_user.email} (username: {username})")
        else:
            print("⚠️  管理者ユーザー既存: admin@delivery-test.com")
    except Exception as e:
        print(f"❌ 管理者ユーザー作成エラー: {e}")
    
    # 2. 事業者ユーザー
    try:
        if not User.objects.filter(email='business@delivery-test.com').exists():
            # 既存のusernameをチェック
            username = 'business_test'
            counter = 1
            while User.objects.filter(username=username).exists():
                username = f'business_test_{counter}'
                counter += 1
                
            business_user = User.objects.create_user(
                username=username,
                email='business@delivery-test.com',
                password='BusinessTest123!',
                first_name='事業者',
                last_name='テスト',
                user_type='company'
            )
            print(f"✅ 事業者ユーザー作成: {business_user.email} (username: {username})")
        else:
            print("⚠️  事業者ユーザー既存: business@delivery-test.com")
    except Exception as e:
        print(f"❌ 事業者ユーザー作成エラー: {e}")
    
    # 3. ドライバーユーザー
    try:
        if not User.objects.filter(email='driver@delivery-test.com').exists():
            # 既存のusernameをチェック
            username = 'driver_test1'
            counter = 1
            while User.objects.filter(username=username).exists():
                username = f'driver_test1_{counter}'
                counter += 1
                
            driver_user = User.objects.create_user(
                username=username,
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
                vehicle_type='light_truck'
            )
            print(f"✅ ドライバーユーザー作成: {driver_user.email} (username: {username})")
            print("✅ ドライバープロフィール作成完了")
        else:
            print("⚠️  ドライバーユーザー既存: driver@delivery-test.com")
    except Exception as e:
        print(f"❌ ドライバーユーザー作成エラー: {e}")
    
    # 4. 追加ドライバーユーザー
    try:
        if not User.objects.filter(email='driver2@delivery-test.com').exists():
            # 既存のusernameをチェック
            username = 'driver_test2'
            counter = 1
            while User.objects.filter(username=username).exists():
                username = f'driver_test2_{counter}'
                counter += 1
                
            driver_user2 = User.objects.create_user(
                username=username,
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
                vehicle_type='truck'
            )
            print(f"✅ ドライバーユーザー2作成: {driver_user2.email} (username: {username})")
            print("✅ ドライバープロフィール2作成完了")
        else:
            print("⚠️  ドライバーユーザー2既存: driver2@delivery-test.com")
    except Exception as e:
        print(f"❌ ドライバーユーザー2作成エラー: {e}")
    
    # 5. シードユーザー
    try:
        if not User.objects.filter(email='seed@delivery-test.com').exists():
            # 既存のusernameをチェック
            username = 'seed_test'
            counter = 1
            while User.objects.filter(username=username).exists():
                username = f'seed_test_{counter}'
                counter += 1
                
            seed_user = User.objects.create_user(
                username=username,
                email='seed@delivery-test.com',
                password='SeedTest123!',
                first_name='シード',
                last_name='テスト',
                user_type='seed'
            )
            print(f"✅ シードユーザー作成: {seed_user.email} (username: {username})")
        else:
            print("⚠️  シードユーザー既存: seed@delivery-test.com")
    except Exception as e:
        print(f"❌ シードユーザー作成エラー: {e}")
    
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
    
    print("\n5. シードユーザー:")
    print("   Email: seed@delivery-test.com")
    print("   Password: SeedTest123!")
    print("   権限: シード管理機能アクセス")
    
    print(f"\n📊 総ユーザー数: {User.objects.count()}")
    print(f"📊 ドライバー数: {DriverProfile.objects.count()}")

if __name__ == '__main__':
    try:
        create_test_users()
    except Exception as e:
        print(f"❌ エラー: {e}")
        sys.exit(1)