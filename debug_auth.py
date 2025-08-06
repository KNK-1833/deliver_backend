#!/usr/bin/env python
"""認証の詳細デバッグ"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model, authenticate
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

User = get_user_model()

print("="*50)
print("Authentication Debug")
print("="*50)

# モデル設定確認
print(f"USERNAME_FIELD: {User.USERNAME_FIELD}")
print(f"REQUIRED_FIELDS: {User.REQUIRED_FIELDS}")

# ユーザー確認
seed = User.objects.filter(email='seed@delivery-test.com').first()
if seed:
    print(f"\nUser found:")
    print(f"  Email: {seed.email}")
    print(f"  Username: {seed.username}")
    print(f"  Is active: {seed.is_active}")
    print(f"  Password check: {seed.check_password('SeedTest123!')}")
    
    # 認証テスト1: email
    print(f"\n1. Authenticate with email:")
    auth1 = authenticate(email='seed@delivery-test.com', password='SeedTest123!')
    print(f"  Result: {auth1}")
    
    # 認証テスト2: username
    print(f"\n2. Authenticate with username:")
    auth2 = authenticate(username='seed_test_1', password='SeedTest123!')
    print(f"  Result: {auth2}")
    
    # TokenObtainPairSerializerテスト
    print(f"\n3. TokenObtainPairSerializer test:")
    try:
        serializer = TokenObtainPairSerializer(data={
            'email': 'seed@delivery-test.com',
            'password': 'SeedTest123!'
        })
        if serializer.is_valid():
            print("  Serializer valid, tokens generated")
            print(f"  Access token: {serializer.validated_data['access']}")
        else:
            print(f"  Serializer errors: {serializer.errors}")
    except Exception as e:
        print(f"  Serializer exception: {e}")

else:
    print("❌ Seed user not found!")

print("\n" + "="*50)
print("Debug complete")
print("="*50)