# Railway デプロイ手順書

## 概要
このドキュメントでは、配送サポートシステムをRailwayにデプロイする手順を説明します。
バックエンド（Django）とフロントエンド（React）を別々のサービスとしてデプロイします。

## 前提条件
- Railwayアカウント（https://railway.app）
- GitHubアカウント
- Railway CLI（オプション）

## 全体的な構成
```
delivery_support/
├── backend/     → Railway Service 1 (Django API)
├── frontend/    → Railway Service 2 (React App)
└── docs/
```

---

## 1. バックエンド（Django）のデプロイ

### 1.1 必要なファイルの準備

#### requirements.txt の作成
`backend/requirements.txt` ファイルを作成：
```txt
Django==4.2.7
djangorestframework==3.14.0
djangorestframework-simplejwt==5.3.0
django-cors-headers==4.3.0
python-dotenv==1.0.0
anthropic==0.39.0
Pillow==10.1.0
psycopg2-binary==2.9.9
gunicorn==21.2.0
whitenoise==6.6.0
dj-database-url==2.1.0
```

#### railway.json の作成
`backend/railway.json` ファイルを作成：
```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS",
    "buildCommand": "pip install -r requirements.txt"
  },
  "deploy": {
    "startCommand": "python manage.py migrate && python manage.py collectstatic --noinput && gunicorn config.wsgi:application --bind 0.0.0.0:$PORT",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

#### Procfile の作成
`backend/Procfile` ファイルを作成：
```
web: python manage.py migrate && python manage.py collectstatic --noinput && gunicorn config.wsgi:application --bind 0.0.0.0:$PORT
```

#### runtime.txt の作成
`backend/runtime.txt` ファイルを作成：
```
python-3.11.9
```

### 1.2 Django設定の本番対応

`backend/config/settings.py` を以下のように更新：

```python
import os
import dj_database_url
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

# Railway環境の判定
IS_RAILWAY = os.environ.get('RAILWAY_ENVIRONMENT') is not None

# セキュリティ設定
SECRET_KEY = os.environ.get('SECRET_KEY', 'your-default-secret-key-change-in-production')
DEBUG = not IS_RAILWAY
ALLOWED_HOSTS = ['*'] if IS_RAILWAY else ['localhost', '127.0.0.1']

# Railway環境でのCSRF設定
if IS_RAILWAY:
    CSRF_TRUSTED_ORIGINS = [
        f"https://{os.environ.get('RAILWAY_PUBLIC_DOMAIN')}",
        f"https://{os.environ.get('RAILWAY_STATIC_URL', '')}"
    ]

# データベース設定
if IS_RAILWAY:
    DATABASES = {
        'default': dj_database_url.config(
            default=os.environ.get('DATABASE_URL'),
            conn_max_age=600,
            conn_health_checks=True,
        )
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# 静的ファイル設定
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# メディアファイル設定
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# CORS設定（フロントエンドURL追加）
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

if IS_RAILWAY:
    frontend_domain = os.environ.get('FRONTEND_URL')
    if frontend_domain:
        CORS_ALLOWED_ORIGINS.append(frontend_domain)

# Middleware設定（WhiteNoiseを追加）
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # 静的ファイル配信用
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]
```

### 1.3 Railway環境変数の設定

Railwayダッシュボードで以下の環境変数を設定：

```bash
# Django設定
SECRET_KEY=bbh!$hiif8gs4k7s-yah62ac_=80k3qz^v!5fv)f1q3s9=g$kx
DJANGO_SETTINGS_MODULE=config.settings

# Claude API
CLAUDE_API_KEY=<Claude APIキー>

# フロントエンドURL（CORS用）
FRONTEND_URL=https://your-frontend.railway.app

# データベース（Railwayが自動設定）
DATABASE_URL=<自動設定される>
```

### 1.4 バックエンドのデプロイ手順

1. **GitHubリポジトリの作成**
   ```bash
   cd backend
   git init
   git add .
   git commit -m "Initial backend commit for Railway"
   git remote add origin https://github.com/your-username/delivery-backend.git
   git push -u origin main
   ```

2. **Railwayでプロジェクト作成**
   - Railway（https://railway.app）にログイン
   - 「New Project」をクリック
   - 「Deploy from GitHub repo」を選択
   - リポジトリを選択してデプロイ

3. **PostgreSQLの追加**
   - Railwayダッシュボードで「New」→「Database」→「PostgreSQL」
   - 自動的にDATABASE_URL環境変数が設定される

4. **管理者ユーザーの作成**
   - Railway CLIを使用するか、Railwayダッシュボードのコンソールで：
   ```bash
   python manage.py createsuperuser
   ```

---

## 2. フロントエンド（React）のデプロイ

### 2.1 必要なファイルの準備

#### railway.json の作成
`frontend/railway.json` ファイルを作成：
```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS",
    "buildCommand": "npm ci && npm run build"
  },
  "deploy": {
    "startCommand": "npm run start:prod",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

#### package.json の更新
`frontend/package.json` にプロダクション用スクリプトを追加：
```json
{
  "scripts": {
    "start": "react-scripts start",
    "build": "react-scripts build",
    "start:prod": "serve -s build -l $PORT",
    "test": "react-scripts test",
    "eject": "react-scripts eject"
  },
  "dependencies": {
    // 既存の依存関係...
    "serve": "^14.2.1"
  }
}
```

### 2.2 環境変数の設定

#### .env.production の作成
`frontend/.env.production` ファイルを作成：
```env
REACT_APP_API_URL=https://your-backend.railway.app/api
REACT_APP_ENVIRONMENT=production
```

### 2.3 API設定の更新

`frontend/src/api/client.ts` を環境変数対応に更新：
```typescript
import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

const apiClient = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// トークン管理
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

export default apiClient;
```

### 2.4 フロントエンドのデプロイ手順

1. **GitHubリポジトリの作成**
   ```bash
   cd frontend
   git init
   git add .
   git commit -m "Initial frontend commit for Railway"
   git remote add origin https://github.com/your-username/delivery-frontend.git
   git push -u origin main
   ```

2. **Railwayでプロジェクト作成**
   - 「New Project」をクリック
   - 「Deploy from GitHub repo」を選択
   - フロントエンドリポジトリを選択

3. **環境変数の設定**
   Railwayダッシュボードで：
   ```bash
   REACT_APP_API_URL=https://your-backend.railway.app/api
   PORT=3000
   ```

---

## 3. デプロイ後の確認

### 3.1 ヘルスチェック

#### バックエンド
```bash
curl https://your-backend.railway.app/api/health/
```

#### フロントエンド
ブラウザで `https://your-frontend.railway.app` にアクセス

### 3.2 トラブルシューティング

#### よくある問題と解決方法

1. **CORS エラー**
   - バックエンドの `CORS_ALLOWED_ORIGINS` にフロントエンドURLを追加
   - 環境変数 `FRONTEND_URL` を正しく設定

2. **データベース接続エラー**
   - `DATABASE_URL` が正しく設定されているか確認
   - PostgreSQLサービスが起動しているか確認

3. **静的ファイルが見つからない**
   - `python manage.py collectstatic` が実行されているか確認
   - WhiteNoiseが正しく設定されているか確認

4. **環境変数が読み込まれない**
   - Railwayダッシュボードで環境変数を確認
   - デプロイを再実行

### 3.3 ログの確認

Railwayダッシュボードまたは CLI で：
```bash
railway logs
```

---

## 4. CI/CD の設定（オプション）

### GitHub Actions を使用した自動デプロイ

`.github/workflows/deploy.yml` を作成：

```yaml
name: Deploy to Railway

on:
  push:
    branches: [main]

jobs:
  deploy-backend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Deploy Backend to Railway
        uses: berviantoleo/railway-deploy@v1
        with:
          railway_token: ${{ secrets.RAILWAY_TOKEN }}
          service: backend

  deploy-frontend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Deploy Frontend to Railway
        uses: berviantoleo/railway-deploy@v1
        with:
          railway_token: ${{ secrets.RAILWAY_TOKEN }}
          service: frontend
```

---

## 5. セキュリティのベストプラクティス

### 5.1 環境変数の管理
- 秘密鍵は絶対にコードに含めない
- Railway の環境変数機能を使用
- `.env` ファイルは `.gitignore` に追加

### 5.2 HTTPS の使用
- Railway は自動的に HTTPS を提供
- HTTP から HTTPS へのリダイレクトを設定

### 5.3 セキュリティヘッダー
Django の設定に追加：
```python
if IS_RAILWAY:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
```

---

## 6. モニタリングとメンテナンス

### 6.1 ログ監視
- Railway のログビューアを定期的に確認
- エラーログをSlackやEmailに転送（Railway の Integration 機能）

### 6.2 バックアップ
- PostgreSQL の自動バックアップを設定
- メディアファイルは外部ストレージ（S3等）への移行を検討

### 6.3 スケーリング
- Railway のダッシュボードから簡単にスケールアップ可能
- 必要に応じてレプリカ数を増やす

---

## まとめ

このドキュメントに従って設定することで、配送サポートシステムを Railway に正常にデプロイできます。
デプロイ後は定期的にログを確認し、パフォーマンスを監視することをお勧めします。

## サポート

問題が発生した場合は、以下を確認してください：
- Railway ドキュメント: https://docs.railway.app
- Django デプロイガイド: https://docs.djangoproject.com/en/4.2/howto/deployment/
- React デプロイガイド: https://create-react-app.dev/docs/deployment/