#!/usr/bin/env python
"""本番環境のユーザーをアクティベート"""
import os
import sys
import django

# Django設定を読み込み
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

print("="*50)
print("Activate Production Users")
print("="*50)

# 全ユーザーの状態確認
print("Current user status:")
print("-" * 30)
for user in User.objects.all():
    print(f"{user.email}: Active={user.is_active}, Type={user.user_type}")

print("\n" + "="*50)
print("Activating test users...")
print("="*50)

# テストユーザーをアクティベート
test_emails = [
    'admin@delivery-test.com',
    'business@delivery-test.com', 
    'driver@delivery-test.com',
    'driver2@delivery-test.com',
    'seed@delivery-test.com'
]

for email in test_emails:
    user = User.objects.filter(email=email).first()
    if user:
        user.is_active = True
        user.save()
        print(f"✅ Activated: {email}")
    else:
        print(f"⚠️  Not found: {email}")

print("\n" + "="*50)
print("Updated user status:")
print("="*50)

# 更新後の状態確認
for user in User.objects.all():
    if user.email.endswith('@delivery-test.com'):
        print(f"✅ {user.email}: Active={user.is_active}, Type={user.user_type}")

# シードユーザーの詳細テスト
print("\n" + "="*50)
print("Seed user detailed check:")
print("="*50)

seed = User.objects.filter(email='seed@delivery-test.com').first()
if seed:
    print(f"Email: {seed.email}")
    print(f"Username: {seed.username}")
    print(f"Is active: {seed.is_active}")
    print(f"Is staff: {seed.is_staff}")
    print(f"User type: {seed.user_type}")
    print(f"Password check: {seed.check_password('SeedTest123!')}")
    print(f"Date joined: {seed.date_joined}")
    print(f"Last login: {seed.last_login}")
else:
    print("❌ Seed user not found!")

print("\n" + "="*50)
print("Activation complete!")
print("="*50)