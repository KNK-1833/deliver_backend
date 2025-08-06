#!/usr/bin/env python
"""API認証テスト"""
import os
import sys
import django
import json

# Django設定を読み込み
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import authenticate, get_user_model
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()

print("="*50)
print("Authentication Test")
print("="*50)

# ユーザー取得
seed_user = User.objects.filter(email='seed@delivery-test.com').first()
if not seed_user:
    print("❌ Seed user not found")
    sys.exit(1)

print(f"Testing user: {seed_user.email}")
print(f"Username: {seed_user.username}")

# 1. Django認証テスト
print("\n1. Django authenticate test:")
auth_user = authenticate(username=seed_user.username, password='SeedTest123!')
if auth_user:
    print("✅ Django authentication successful")
else:
    print("❌ Django authentication failed")

# 2. JWT トークン生成テスト
print("\n2. JWT token generation test:")
try:
    refresh = RefreshToken.for_user(seed_user)
    access_token = refresh.access_token
    print(f"✅ JWT tokens generated successfully")
    print(f"Access token (first 50 chars): {str(access_token)[:50]}...")
    print(f"Refresh token (first 50 chars): {str(refresh)[:50]}...")
except Exception as e:
    print(f"❌ JWT generation failed: {e}")

# 3. API エンドポイントのシミュレーション
print("\n3. Testing token endpoint logic:")
from apps.users.views import CustomTokenObtainPairView
from django.test import RequestFactory
from rest_framework.test import APIRequestFactory

factory = APIRequestFactory()
request = factory.post('/api/auth/token/', {
    'email': 'seed@delivery-test.com',
    'password': 'SeedTest123!'
}, format='json')

view = CustomTokenObtainPairView.as_view()
try:
    response = view(request)
    print(f"✅ Token endpoint response status: {response.status_code}")
    if response.status_code == 200:
        print("✅ Authentication successful via API endpoint")
        data = response.data
        print(f"Response keys: {data.keys()}")
    else:
        print(f"❌ Authentication failed: {response.data}")
except Exception as e:
    print(f"❌ Token endpoint error: {e}")

print("\n" + "="*50)
print("Test complete")
print("="*50)