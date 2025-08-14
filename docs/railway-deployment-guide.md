# 🚂 Railway デプロイメント設定ガイド

## 📋 必要な環境変数設定

### フロントエンド環境変数（Railway Dashboard で設定）

```bash
# ポート設定（Railwayが自動設定）
PORT=3000

# バックエンドAPI URL
REACT_APP_API_URL=https://deliverbackend-production.up.railway.app/api

# Node.js環境
NODE_ENV=production

# オプション：ビルド最適化
GENERATE_SOURCEMAP=false
CI=false
```

### バックエンド環境変数（すでに設定済み確認用）

```bash
# Django設定
DJANGO_SETTINGS_MODULE=config.settings
SECRET_KEY=[生成された秘密鍵]
DEBUG=False
ALLOWED_HOSTS=deliverbackend-production.up.railway.app,localhost

# データベース（Railway自動設定）
DATABASE_URL=postgresql://[自動設定]

# CORS設定
CORS_ALLOWED_ORIGINS=https://deliverfrontend-production.up.railway.app
FRONTEND_URL=https://deliverfrontend-production.up.railway.app
ALLOWED_TEST_ORIGINS=https://deliver-frontend-production.up.railway.app,https://deliveryfrontend-production.up.railway.app

# Claude API（オプション）
CLAUDE_API_KEY=[APIキー]

# メディアファイル
MEDIA_URL=/media/
STATIC_URL=/static/
```

---

## 🔧 ビルド設定

### Railway.app での設定方法

#### 1. Service Settings で設定する項目

**Build Command:**
```bash
npm run build
```

**Start Command:**
```bash
npx serve build
```

**Watch Paths（自動デプロイ対象）:**
```
/frontend/**
```

**Health Check Path:**
```
/
```

**Health Check Timeout:**
```
100
```

#### 2. Root Directory 設定

フロントエンドがサブディレクトリの場合：
```
/frontend
```

モノレポの場合は適切に設定してください。

---

## 📁 設定ファイル一覧

### 1. railway.toml（Railway固有設定）
```toml
[build]
builder = "nixpacks"
buildCommand = "npm run build"

[deploy]
startCommand = "npx serve build"
healthcheckPath = "/"
healthcheckTimeout = 100
restartPolicyType = "on_failure"
restartPolicyMaxRetries = 3
```

### 2. nixpacks.toml（Nixpacksビルド設定）
```toml
[variables]
NODE_VERSION = "20"

[phases.setup]
nixPkgs = ["nodejs"]

[phases.install]
cmd = "npm ci --no-audit"

[phases.build] 
cmd = "npm run build"

[start]
cmd = "npx serve build"
```

### 3. package.json scripts（確認）
```json
{
  "scripts": {
    "start": "react-scripts start",
    "build": "react-scripts build",
    "serve": "serve -s build -p 3000"
  }
}
```

### 4. serve.json（Serve設定）
```json
{
  "public": "build",
  "headers": [
    {
      "source": "/service-worker.js",
      "headers": [
        {
          "key": "Cache-Control",
          "value": "public, max-age=0, must-revalidate"
        }
      ]
    }
  ],
  "rewrites": [
    { "source": "**", "destination": "/index.html" }
  ]
}
```

### 5. .env.production（本番環境変数）
```env
REACT_APP_API_URL=https://deliverbackend-production.up.railway.app/api
```

---

## 🐛 トラブルシューティング

### ❌ よくあるエラーと解決方法

#### 5. CORS Error
**エラー**: `Access to XMLHttpRequest blocked by CORS policy`

**解決方法**:
- バックエンドの環境変数に`FRONTEND_URL`を追加
- フロントエンドのURLが変更された場合は`ALLOWED_TEST_ORIGINS`に追加
- バックエンドを再デプロイ
- 例：
  ```bash
  FRONTEND_URL=https://your-frontend.up.railway.app
  ALLOWED_TEST_ORIGINS=https://other-frontend.up.railway.app
  ```

#### 1. Health Check Failed
**エラー**: `Healthcheck failed!`

**解決方法**:
- Health Check Timeout を 100秒以上に設定
- Start Command を `npx serve build` に変更
- PORT環境変数が正しく設定されているか確認

#### 2. Build Failed
**エラー**: `npm run build failed`

**解決方法**:
- `CI=false` を環境変数に追加（警告をエラーとして扱わない）
- Node.js バージョンを 20 に固定
- `npm ci` の代わりに `npm install` を試す

#### 3. Module Not Found
**エラー**: `Module not found: Error: Can't resolve './ui'`

**解決方法**:
- ディレクトリの大文字小文字を確認（ui vs UI）
- Git でディレクトリ名の変更が反映されているか確認
- `npm ci` を再実行

#### 4. Application Error
**エラー**: `Application failed to respond`

**解決方法**:
- Start Command に PORT変数を含める
- serve パッケージがインストールされているか確認
- railway logs でエラーログを確認

---

## 🚀 デプロイ手順

### ステップ 1: GitHub リポジトリ接続
1. Railway Dashboard で「New Project」
2. 「Deploy from GitHub repo」を選択
3. `deliver_frontend` リポジトリを選択

### ステップ 2: 環境変数設定
1. Service Settings → Variables
2. 上記の環境変数を設定
3. 「Add Variable」で追加

### ステップ 3: ビルド設定
1. Service Settings → Build & Deploy
2. Build Command: `npm run build`
3. Start Command: `npx serve build`
4. Root Directory: 適切に設定（モノレポの場合）

### ステップ 4: デプロイ実行
1. 「Deploy」ボタンをクリック
2. ビルドログを監視
3. Health Check が成功するまで待つ

### ステップ 5: 動作確認
1. 提供されたURLにアクセス
2. ログイン画面が表示されることを確認
3. APIとの通信を確認

---

## 📊 推奨設定まとめ

### 最小限必要な設定
- ✅ PORT（Railwayが自動設定）
- ✅ REACT_APP_API_URL
- ✅ Build Command: `npm run build`
- ✅ Start Command: `npx serve build`

### パフォーマンス最適化
- ✅ NODE_ENV=production
- ✅ GENERATE_SOURCEMAP=false
- ✅ CI=false（ビルド警告を無視）

### セキュリティ設定
- ✅ HTTPSを強制（Railway自動）
- ✅ CORS設定（バックエンド側）

---

## 🔍 デバッグコマンド

### Railway CLI でログ確認
```bash
railway logs --tail

# 特定サービスのログ
railway logs --service deliver_frontend --tail
```

### ビルドキャッシュクリア
```bash
# Railway Dashboard で
Settings → Clear build cache
```

### 環境変数確認
```bash
railway variables
```

---

## 🎯 チェックリスト

デプロイ前の確認事項：

- [ ] package.json の scripts 設定確認
- [ ] .env.production ファイル作成
- [ ] railway.toml 設定確認
- [ ] nixpacks.toml 設定確認
- [ ] serve.json 設定確認
- [ ] GitHub リポジトリに最新コードをプッシュ
- [ ] Railway で環境変数設定
- [ ] Build/Start Command 設定
- [ ] Health Check 設定

---

## 📞 サポート

問題が解決しない場合：
1. Railway Status Page を確認
2. Railway Discord コミュニティ
3. GitHub Issues でバグ報告

最終更新: 2025年8月10日