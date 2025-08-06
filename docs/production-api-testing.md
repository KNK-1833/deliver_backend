# 本番環境APIテスト設定ガイド

## 概要
ローカル環境から本番環境（Railway）のバックエンドAPIをテストするための設定手順を説明します。

## 現在の本番環境URL
- **バックエンドAPI**: https://deliverbackend-production-6353.up.railway.app/api/
- **フロントエンド**: https://deliverfrontend-production.up.railway.app/

## 1. Railway側で必要な設定

### 1.1 CORS設定の追加
現在の設定では以下のオリジンが許可されています：
```python
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",        # ✅ 設定済み
    "http://127.0.0.1:3000",       # ✅ 設定済み 
    "http://192.168.10.4:3000",    # ✅ 設定済み
    "https://deliverfrontend-production.up.railway.app",  # ✅ 設定済み
]
```

**追加が必要なオリジン（Railway環境変数で設定）:**

Railway Dashboardで以下の環境変数を追加：

| 環境変数名 | 値 | 説明 |
|-----------|---|-----|
| `ALLOWED_TEST_ORIGINS` | `http://localhost:8080,http://127.0.0.1:8080` | ローカルテスト用ポート |

### 1.2 Django設定の更新が必要
`backend/config/settings.py`に以下を追加：

```python
# テスト用CORS設定（Railway環境変数から）
if IS_PRODUCTION:
    test_origins = os.environ.get('ALLOWED_TEST_ORIGINS', '')
    if test_origins:
        CORS_ALLOWED_ORIGINS.extend(test_origins.split(','))
```

### 1.3 CSRF設定の確認
現在の設定は適切：
```python
CSRF_TRUSTED_ORIGINS = [
    'https://deliverbackend-production-6353.up.railway.app',
    'https://*.up.railway.app',
]
```

## 2. ローカル環境でのテスト設定

### 2.1 テスト用スクリプト作成

```bash
# test_production_api.py
import requests
import json

API_BASE = "https://deliverbackend-production-6353.up.railway.app/api"

def test_api_connection():
    """API接続テスト"""
    try:
        response = requests.get(f"{API_BASE}/auth/profile/", timeout=10)
        print(f"接続テスト: {response.status_code}")
        return response.status_code == 401  # 認証が必要なので401が正常
    except requests.exceptions.RequestException as e:
        print(f"接続エラー: {e}")
        return False

def test_login(email, password):
    """ログインテスト"""
    data = {
        "username": email,
        "password": password
    }
    
    try:
        response = requests.post(f"{API_BASE}/auth/token/", json=data, timeout=10)
        if response.status_code == 200:
            tokens = response.json()
            print(f"ログイン成功: {email}")
            return tokens
        else:
            print(f"ログイン失敗: {response.status_code} - {response.text}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"リクエストエラー: {e}")
        return None

def test_authenticated_request(access_token):
    """認証付きリクエストテスト"""
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(f"{API_BASE}/auth/profile/", headers=headers, timeout=10)
        if response.status_code == 200:
            profile = response.json()
            print(f"プロフィール取得成功: {profile.get('email')}")
            return profile
        else:
            print(f"プロフィール取得失敗: {response.status_code}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"リクエストエラー: {e}")
        return None

# テスト実行
if __name__ == "__main__":
    print("🚀 本番API接続テスト開始")
    
    # 1. 接続テスト
    print("\n1. API接続テスト")
    if not test_api_connection():
        print("❌ API接続失敗")
        exit(1)
    
    # 2. ログインテスト
    print("\n2. ログインテスト")
    tokens = test_login("admin@example.com", "AdminTest123!")
    if not tokens:
        print("❌ ログイン失敗")
        exit(1)
    
    # 3. 認証付きリクエストテスト
    print("\n3. 認証付きリクエストテスト")
    profile = test_authenticated_request(tokens['access'])
    if not profile:
        print("❌ 認証付きリクエスト失敗")
        exit(1)
    
    print("\n✅ 全てのテストが成功しました！")
```

### 2.2 Postmanコレクション設定

**Environment設定:**
```json
{
  "name": "Railway Production",
  "values": [
    {
      "key": "base_url",
      "value": "https://deliverbackend-production-6353.up.railway.app/api",
      "enabled": true
    },
    {
      "key": "admin_email", 
      "value": "admin@example.com",
      "enabled": true
    },
    {
      "key": "admin_password",
      "value": "AdminTest123!",
      "enabled": true
    }
  ]
}
```

**主要なリクエスト:**

1. **ログイン (POST)**
   ```
   URL: {{base_url}}/auth/token/
   Body (JSON):
   {
     "username": "{{admin_email}}",
     "password": "{{admin_password}}"
   }
   ```

2. **プロフィール取得 (GET)**
   ```
   URL: {{base_url}}/auth/profile/
   Headers:
   Authorization: Bearer {{access_token}}
   ```

### 2.3 cURLコマンド例

```bash
# 1. ログイン
curl -X POST https://deliverbackend-production-6353.up.railway.app/api/auth/token/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin@example.com",
    "password": "AdminTest123!"
  }'

# 2. プロフィール取得 (アクセストークンを上記レスポンスから取得)
curl -X GET https://deliverbackend-production-6353.up.railway.app/api/auth/profile/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN_HERE"

# 3. 配送依頼一覧取得
curl -X GET https://deliverbackend-production-6353.up.railway.app/api/delivery/requests/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN_HERE"
```

## 3. テスト用シードユーザー

| アカウント | メールアドレス | パスワード | 権限 |
|-----------|---------------|-----------|------|
| 管理者 | admin@example.com | AdminTest123! | スーパーユーザー |
| 事業者 | company@example.com | CompanyTest123! | 事業者権限 |
| ドライバー | driver@example.com | DriverTest123! | ドライバー権限 |

## 4. よくあるエラーと対処法

### 4.1 CORS エラー
```
Access to XMLHttpRequest at '...' from origin 'http://localhost:3000' has been blocked by CORS policy
```

**対処法:**
1. Railway環境変数 `ALLOWED_TEST_ORIGINS` を追加
2. Django設定を更新してデプロイ

### 4.2 認証エラー
```
401 Unauthorized
```

**対処法:**
1. ユーザー情報が正しいか確認
2. トークンの有効期限を確認（60分）
3. リフレッシュトークンを使用

### 4.3 接続タイムアウト
```
ConnectTimeout: Connection timeout
```

**対処法:**
1. Railway サービスが稼働中か確認
2. ネットワーク接続を確認
3. タイムアウト値を増加

## 5. 監視・ログ確認

### 5.1 Railway ログ確認
```bash
# リアルタイムログ確認
railway logs --service deliver_backend

# 特定時間のログ確認
railway logs --service deliver_backend --since 1h
```

### 5.2 エラーログの確認ポイント
- CORS関連エラー
- 認証エラー
- データベース接続エラー
- Claude API接続エラー

## 6. セキュリティ考慮事項

### 6.1 本番環境テスト時の注意
- テスト用データのみ使用
- 本番データを変更しない
- APIレート制限に注意
- 認証情報の適切な管理

### 6.2 推奨テストシナリオ
1. 認証フロー全体のテスト
2. CRUD操作の基本動作確認
3. ファイルアップロード機能のテスト
4. エラーハンドリングの確認
5. レスポンス時間の測定

## 7. 自動化テストスクリプト

```bash
#!/bin/bash
# production_api_test.sh

API_BASE="https://deliverbackend-production-6353.up.railway.app/api"
ADMIN_EMAIL="admin@example.com"
ADMIN_PASSWORD="AdminTest123!"

echo "🚀 本番API自動テスト開始"

# ログイン
echo "📋 ログインテスト..."
LOGIN_RESPONSE=$(curl -s -X POST "$API_BASE/auth/token/" \
  -H "Content-Type: application/json" \
  -d "{\"username\":\"$ADMIN_EMAIL\",\"password\":\"$ADMIN_PASSWORD\"}")

if [[ $LOGIN_RESPONSE == *"access"* ]]; then
  echo "✅ ログイン成功"
  ACCESS_TOKEN=$(echo $LOGIN_RESPONSE | grep -o '"access":"[^"]*' | grep -o '[^"]*$')
else
  echo "❌ ログイン失敗"
  echo $LOGIN_RESPONSE
  exit 1
fi

# プロフィール取得
echo "👤 プロフィール取得テスト..."
PROFILE_RESPONSE=$(curl -s -X GET "$API_BASE/auth/profile/" \
  -H "Authorization: Bearer $ACCESS_TOKEN")

if [[ $PROFILE_RESPONSE == *"email"* ]]; then
  echo "✅ プロフィール取得成功"
else
  echo "❌ プロフィール取得失敗"
  exit 1
fi

echo "🎉 全テスト完了！"
```

実行権限を付与して使用：
```bash
chmod +x production_api_test.sh
./production_api_test.sh
```