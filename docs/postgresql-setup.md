# PostgreSQL セットアップガイド

## 概要
配送サポートシステムは全環境でPostgreSQLを使用するよう統一されました。このガイドではローカル開発環境でのPostgreSQLセットアップ手順を説明します。

## PostgreSQLのインストール

### macOS (Homebrew)
```bash
# PostgreSQLをインストール
brew install postgresql@15

# サービスを開始
brew services start postgresql@15

# パスを追加
echo 'export PATH="/opt/homebrew/opt/postgresql@15/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

### Ubuntu/Debian
```bash
# PostgreSQLをインストール
sudo apt update
sudo apt install postgresql postgresql-contrib

# サービスを開始
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

### Windows
1. [PostgreSQL公式サイト](https://www.postgresql.org/download/windows/)からインストーラーをダウンロード
2. インストーラーを実行してセットアップ
3. パスワードを設定（デフォルトユーザー: `postgres`）

## データベースセットアップ

### 1. PostgreSQLに接続
```bash
# postgresユーザーでログイン
psql -U postgres
```

### 2. 開発用データベース作成
```sql
-- 開発用データベース作成
CREATE DATABASE delivery_support_dev;

-- テスト用データベース作成
CREATE DATABASE test_delivery_support;

-- ユーザーに権限付与（必要に応じて）
GRANT ALL PRIVILEGES ON DATABASE delivery_support_dev TO postgres;
GRANT ALL PRIVILEGES ON DATABASE test_delivery_support TO postgres;

-- 確認
\l
\q
```

### 3. 環境変数設定

`backend/.env`ファイルを以下のように設定：

```env
# Django Settings
DEBUG=True
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=localhost,127.0.0.1

# PostgreSQL Database Settings
DATABASE_URL=postgresql://postgres:password@localhost:5432/delivery_support_dev
DB_NAME=delivery_support_dev
DB_USER=postgres
DB_PASSWORD=password
DB_HOST=localhost
DB_PORT=5432

# API Keys
CLAUDE_API_KEY=your-claude-api-key-here
```

### 4. マイグレーション実行

```bash
# 仮想環境をアクティブ化
source .venv/bin/activate

# バックエンドディレクトリに移動
cd backend

# マイグレーション実行
python manage.py makemigrations
python manage.py migrate

# 管理者ユーザー作成
python manage.py createsuperuser
```

## データベース構造

### ユーザー関連テーブル
- `users_user`: カスタムユーザーモデル
- `users_driverprofile`: ドライバープロフィール

### 配送関連テーブル
- `delivery_deliveryrequest`: 配送依頼
- `delivery_assignment`: アサインメント

### ファイル関連テーブル
- `files_fileupload`: アップロードファイル管理

## テーブル名確認方法

```bash
# Django shell を開く
python manage.py shell

# テーブル名を確認
from django.db import connection
cursor = connection.cursor()
cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';")
tables = cursor.fetchall()
for table in tables:
    print(table[0])
```

## よくある問題と解決方法

### 1. 接続エラー
```
psycopg2.OperationalError: could not connect to server
```

**解決方法:**
- PostgreSQLサービスが起動しているか確認
- ユーザー名・パスワードが正しいか確認
- ポート5432が使用可能か確認

### 2. 権限エラー
```
django.db.utils.OperationalError: permission denied to create database
```

**解決方法:**
```sql
-- PostgreSQLに管理者として接続
psql -U postgres

-- ユーザーに権限付与
ALTER USER postgres CREATEDB;
```

### 3. パスワード認証エラー
```
psycopg2.OperationalError: FATAL: password authentication failed
```

**解決方法:**
1. `pg_hba.conf`ファイルを編集
2. 認証方式を`trust`または`md5`に変更
3. PostgreSQLを再起動

### 4. マイグレーションエラー
```
django.db.utils.ProgrammingError: relation does not exist
```

**解決方法:**
```bash
# マイグレーションファイルを削除
find . -path "*/migrations/*.py" -not -name "__init__.py" -delete
find . -path "*/migrations/*.pyc" -delete

# マイグレーションを再作成
python manage.py makemigrations
python manage.py migrate
```

## パフォーマンス設定

### postgresql.confの推奨設定
```conf
# メモリ設定
shared_buffers = 256MB
work_mem = 4MB
maintenance_work_mem = 64MB

# 接続設定
max_connections = 100

# ログ設定（開発時）
log_statement = 'all'
log_duration = on
```

## バックアップ・リストア

### バックアップ
```bash
# データベース全体をバックアップ
pg_dump -U postgres -h localhost delivery_support_dev > backup.sql

# 圧縮バックアップ
pg_dump -U postgres -h localhost -Fc delivery_support_dev > backup.dump
```

### リストア
```bash
# SQLファイルからリストア
psql -U postgres -h localhost delivery_support_dev < backup.sql

# 圧縮ファイルからリストア
pg_restore -U postgres -h localhost -d delivery_support_dev backup.dump
```

## 本番環境との違い

| 項目 | ローカル開発 | Railway本番 |
|------|-------------|-------------|
| ホスト | localhost | postgres.railway.internal |
| ポート | 5432 | 5432 |
| 認証 | パスワード | URL接続文字列 |
| SSL | 不要 | 必要 |
| バックアップ | 手動 | Railway自動 |

## 開発ワークフロー

1. **新機能開発時**
   ```bash
   # モデル変更後
   python manage.py makemigrations
   python manage.py migrate
   ```

2. **テスト実行時**
   ```bash
   # テスト用DBが自動作成・削除される
   python run_tests.py
   ```

3. **本番デプロイ時**
   ```bash
   # Railwayが自動でマイグレーション実行
   git push origin main
   ```