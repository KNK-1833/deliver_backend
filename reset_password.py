#!/usr/bin/env python
"""本番環境のユーザーパスワードをリセット"""
import os
import sys
import django

# Django設定を読み込み
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

print("="*50)
print("Password Reset for Test Users")
print("="*50)

# テストユーザーのリスト
test_users = [
    {'email': 'admin@delivery-test.com', 'password': 'AdminTest123!'},
    {'email': 'business@delivery-test.com', 'password': 'BusinessTest123!'},
    {'email': 'driver@delivery-test.com', 'password': 'DriverTest123!'},
    {'email': 'driver2@delivery-test.com', 'password': 'DriverTest123!'},
    {'email': 'seed@delivery-test.com', 'password': 'SeedTest123!'},
]

for user_data in test_users:
    email = user_data['email']
    password = user_data['password']
    
    user = User.objects.filter(email=email).first()
    if user:
        # パスワードをリセット
        user.set_password(password)
        user.is_active = True  # アクティブであることを確認
        user.save()
        
        # 検証
        if user.check_password(password):
            print(f"✅ Password reset successful for: {email}")
            print(f"   Username: {user.username}")
            print(f"   Password: {password}")
        else:
            print(f"❌ Password reset failed for: {email}")
    else:
        print(f"⚠️  User not found: {email}")

print("\n" + "="*50)
print("Password reset complete!")
print("="*50)