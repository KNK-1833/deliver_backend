#!/usr/bin/env python
"""ユーザー存在確認とパスワードチェック"""
import os
import sys
import django

# Django設定を読み込み
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

# シードユーザーの確認
seed_user = User.objects.filter(email='seed@delivery-test.com').first()
if seed_user:
    print(f'User exists: {seed_user.email}')
    print(f'Username: {seed_user.username}')
    print(f'Is active: {seed_user.is_active}')
    print(f'User type: {seed_user.user_type}')
    print(f'Password check: {seed_user.check_password("SeedTest123!")}')
    
    if not seed_user.check_password("SeedTest123!"):
        print("\n⚠️ Password is incorrect. Resetting...")
        seed_user.set_password("SeedTest123!")
        seed_user.save()
        print("✅ Password has been reset to: SeedTest123!")
        print(f'New password check: {seed_user.check_password("SeedTest123!")}')
else:
    print('❌ Seed user does not exist')
    print('Creating seed user...')
    seed_user = User.objects.create_user(
        username='seed_test',
        email='seed@delivery-test.com',
        password='SeedTest123!',
        first_name='シード',
        last_name='テスト',
        user_type='seed'
    )
    print(f'✅ Created user: {seed_user.email}')

# 全ユーザーの確認
print("\n" + "="*50)
print("All users in database:")
print("="*50)
for user in User.objects.all():
    print(f'Email: {user.email}, Username: {user.username}, Type: {user.user_type}, Active: {user.is_active}')