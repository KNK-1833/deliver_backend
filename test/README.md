# テスト実行ガイド

## 概要

このディレクトリには、配送サポートシステムのバックエンドAPIのテストスイートが含まれています。

## 前提条件

- Python仮想環境が`.venv`に作成済み
- 必要なパッケージがインストール済み
- camera_image.jpgがtest/backend/に配置済み

## テスト実行方法

### 1. 基本実行

```bash
# プロジェクトルートから実行
python run_tests.py
```

### 2. 詳細出力

```bash
python run_tests.py --verbose
```

### 3. カバレッジ測定付き

```bash
python run_tests.py --coverage
```

### 4. 特定モジュールのテストのみ

```bash
# ユーザー認証のテストのみ
python run_tests.py --module users

# 配送管理のテストのみ
python run_tests.py --module delivery

# ファイル管理のテストのみ
python run_tests.py --module files

# 統合テストのみ
python run_tests.py --module integration
```

### 5. 手動でのpytest実行

```bash
# バックエンドディレクトリから実行
cd backend
source ../.venv/bin/activate
python -m pytest ../test/backend/ -v
```

## テストファイル構造

```
test/backend/
├── conftest.py              # テスト設定とフィクスチャ
├── test_users.py            # ユーザー認証APIテスト
├── test_delivery.py         # 配送管理APIテスト
├── test_files.py            # ファイル管理・Claude APIテスト
├── test_integration.py      # 統合テスト
└── camera_image.jpg         # テスト用画像ファイル
```

## テスト内容

### ユーザー認証 (test_users.py)
- ユーザー登録
- JWT認証（ログイン/トークンリフレッシュ）
- ユーザープロフィール取得・更新
- ドライバープロフィール管理
- 権限チェック

### 配送管理 (test_delivery.py)
- 配送依頼のCRUD操作
- ドライバーによる案件受諾
- アサインステータス管理
- 権限別のデータアクセス制御

### ファイル管理 (test_files.py)
- ファイルアップロード
- Claude API連携（モック使用）
- OCR処理と構造化データ抽出
- ファイルから配送依頼作成

### 統合テスト (test_integration.py)
- 完全な配送ワークフロー
- ファイルから配送依頼までの流れ
- 複数ユーザー間の権限境界
- エラーハンドリング
- データ整合性

## カバレッジレポート

カバレッジ測定実行後、`htmlcov/index.html`でHTMLレポートを確認できます。

## 注意事項

- テスト実行時は自動的にテスト用データベースが作成・削除されます
- Claude API呼び出しはモックを使用しているため、実際のAPIキーは不要です
- 一部のテストで実際の画像ファイル（camera_image.jpg）を使用します

## トラブルシューティング

### Django設定エラー
```
django.core.exceptions.ImproperlyConfigured
```
→ backendディレクトリから実行してください

### ファイルが見つからないエラー
```
AssertionError: Test image file not found
```
→ camera_image.jpgがtest/backend/に配置されているか確認してください

### データベースエラー
```
sqlite3.OperationalError: database is locked
```
→ 他のDjangoプロセスが動作していないか確認してください