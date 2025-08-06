#!/usr/bin/env python
"""本番環境のシードユーザーを修正"""
import os
import sys
import django

# Django設定を読み込み
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

print("="*50)
print("Production User Fix")
print("="*50)

# 現在のユーザー数を確認
total = User.objects.count()
print(f"Total users in database: {total}")

# シードユーザーを確認/作成
email = 'seed@delivery-test.com'
password = 'SeedTest123!'

user = User.objects.filter(email=email).first()

if user:
    print(f"\n✅ User found: {email}")
    print(f"   Current username: {user.username}")
    print(f"   Is active: {user.is_active}")
    print(f"   User type: {user.user_type}")
    
    # パスワードをリセット
    print("\n🔄 Resetting password...")
    user.set_password(password)
    user.is_active = True
    user.save()
    
    # 確認
    if user.check_password(password):
        print("✅ Password reset successful!")
    else:
        print("❌ Password reset failed!")
else:
    print(f"\n⚠️ User not found: {email}")
    print("Creating new user...")
    
    # ユニークなusernameを生成
    username = 'seed_prod'
    counter = 1
    while User.objects.filter(username=username).exists():
        username = f'seed_prod_{counter}'
        counter += 1
    
    user = User.objects.create_user(
        username=username,
        email=email,
        password=password,
        first_name='シード',
        last_name='テスト',
        user_type='seed',
        is_active=True
    )
    print(f"✅ User created: {user.email}")
    print(f"   Username: {user.username}")

# 最終確認
print("\n" + "="*50)
print("Final verification:")
print("="*50)

# 認証テスト
from django.contrib.auth import authenticate

# emailでの認証（カスタムビューをシミュレート）
test_user = User.objects.get(email=email)
auth_test = authenticate(username=test_user.username, password=password)
if auth_test:
    print(f"✅ Authentication test passed for {email}")
else:
    print(f"❌ Authentication test failed for {email}")

# パスワードチェック
print(f"Direct password check: {test_user.check_password(password)}")

print("\n" + "="*50)
print("Setup complete! You can now login with:")
print(f"Email: {email}")
print(f"Password: {password}")
print("="*50)