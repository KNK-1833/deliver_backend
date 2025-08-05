# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Instructions

- 回答はすべて日本語で生成すること
- ファイルの修正はspecに記載された仕様およびユーザーによるプロンプトで明記された内容に基づいてのみ行う

## Python環境

- **仮想環境パス**: `/Users/shoichi/Desktop/Projects/delivery_support/.venv`
- **重要**: Python関連のコマンドを実行する前に、必ず仮想環境を有効化すること
  ```bash
  source .venv/bin/activate
  ```
- Windows環境の場合: `.venv/Scripts/activate`

## プロジェクト構造

このプロジェクトは配送サポートシステムで、以下の構成で実装されています：

- **backend/**: Django REST Framework APIサーバー（実装済み）
- **frontend/**: React Webアプリケーション（基本構造作成済み）
- **docs/**: プロジェクト仕様書

### バックエンド構成
- **apps/users**: ユーザー管理（カスタムUserモデル、DriverProfile）
- **apps/delivery**: 配送案件管理（DeliveryRequest, Assignment） 
- **apps/files**: ファイル管理・Claude API連携（FileUpload）
- **config/**: Django設定（JWT認証、CORS、環境変数管理）

### バックエンド開発コマンド（Django）
```bash
# サーバー起動
source .venv/bin/activate && cd backend && python manage.py runserver

# マイグレーション作成
source .venv/bin/activate && cd backend && python manage.py makemigrations

# マイグレーション適用
source .venv/bin/activate && cd backend && python manage.py migrate

# 管理者ユーザー作成
source .venv/bin/activate && cd backend && python manage.py createsuperuser

# Django shell
source .venv/bin/activate && cd backend && python manage.py shell
```

## 実装済み機能

### 認証・認可システム
- カスタムUserモデル（email認証、ユーザータイプ）
- JWT認証（SimpleJWT使用）
- ロールベース認可（ドライバー/事業者）
- ユーザー登録・ログインAPI

### 配送管理機能
- 配送依頼（DeliveryRequest）の作成・管理
- ドライバーアサイン（Assignment）機能
- ステータス管理（受付中→アサイン済み→配送中→完了）
- ドライバープロフィール管理

### ファイル・Claude API連携
- ファイルアップロード機能
- Claude API連携による帳票OCR・構造化
- 抽出データから配送依頼自動作成
- 画像（JPG/PNG）・PDF対応

### その他
- Django管理画面設定
- CORS設定（React用）
- メディアファイル管理

## API エンドポイント

### 認証関連 (`/api/auth/`)
- `POST /register/` - ユーザー登録
- `POST /token/` - JWTトークン取得
- `POST /token/refresh/` - トークンリフレッシュ
- `GET /profile/` - ユーザープロフィール取得
- `PUT /profile/` - ユーザープロフィール更新
- `GET /driver-profile/` - ドライバープロフィール取得
- `PUT /driver-profile/` - ドライバープロフィール更新

### 配送関連 (`/api/delivery/`)
- `GET /requests/` - 配送依頼一覧
- `POST /requests/` - 配送依頼作成
- `GET /requests/{id}/` - 配送依頼詳細
- `POST /requests/{id}/accept/` - 配送案件受諾
- `GET /assignments/` - アサイン一覧
- `POST /assignments/{id}/status/` - アサインステータス更新

### ファイル関連 (`/api/files/`)
- `GET /uploads/` - ファイル一覧
- `POST /uploads/` - ファイルアップロード
- `POST /uploads/{id}/process/` - Claude API処理
- `POST /uploads/{id}/create-delivery/` - ファイルから配送依頼作成

### データベース設定
- 開発環境: SQLite（USE_SQLITE=True）
- 本番環境: PostgreSQL（USE_SQLITE=False）
- 環境変数: `backend/.env`ファイルで管理
- 必要な環境変数: `CLAUDE_API_KEY`（Claude API連携用）

## テスト

### テスト実行
```bash
# 全テスト実行
python run_tests.py

# カバレッジ測定付き
python run_tests.py --coverage

# 特定モジュールのみ
python run_tests.py --module users
python run_tests.py --module delivery
python run_tests.py --module files
python run_tests.py --module integration
```

### テスト構成
- **test/backend/test_users.py**: ユーザー認証APIテスト
- **test/backend/test_delivery.py**: 配送管理APIテスト
- **test/backend/test_files.py**: ファイル管理・Claude APIテスト
- **test/backend/test_integration.py**: 統合テスト

### 前提条件
- camera_image.jpgがtest/backend/に配置済み
- 仮想環境アクティブ化済み
- pytest, pytest-django, pytest-mock等インストール済み