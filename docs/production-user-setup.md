# 本番環境ユーザー作成ガイド

## 概要
Railway本番環境でテスト用ユーザーを作成する手順を説明します。

## 作成されるユーザー

### 1. 管理者ユーザー
- **Email**: `admin@example.com`
- **Password**: `AdminTest123!`
- **Username**: `admin`
- **権限**: スーパーユーザー（Django管理画面アクセス可能）
- **用途**: システム管理、全データの確認・管理

### 2. 事業者ユーザー
- **Email**: `company@example.com`
- **Password**: `CompanyTest123!`
- **Username**: `company_user`
- **権限**: 事業者（user_type: company）
- **用途**: 配送依頼の作成、ファイルアップロード

### 3. ドライバーユーザー
- **Email**: `driver@example.com`
- **Password**: `DriverTest123!`
- **Username**: `driver_user`
- **権限**: ドライバー（user_type: driver）
- **プロフィール**: オートバイ（motorcycle）、利用可能状態
- **用途**: 配送案件の受諾、配送管理

---

## Railwayでの実行方法

### 方法1: Railway CLI使用（推奨）

1. **Railway CLIのインストール**
   ```bash
   npm install -g @railway/cli
   ```

2. **Railwayにログイン**
   ```bash
   railway login
   ```

3. **プロジェクトに接続**
   ```bash
   railway link
   ```

4. **シードユーザー作成スクリプト実行**
   ```bash
   railway run python backend/create_seed_users.py
   ```
   
   または、Railway上のサービスで直接実行：
   ```bash
   railway run --service deliver_backend python backend/create_seed_users.py
   ```

### 方法2: Railwayダッシュボード使用

1. [Railway Dashboard](https://railway.app/)にアクセス
2. プロジェクト「DeliveryProject」を選択
3. 「deliver_backend」サービスを選択
4. **「Settings」**タブから**「Shell」**を開く
5. 以下のコマンドを実行:
   ```bash
   cd /app/backend && python create_seed_users.py
   ```

### 方法3: 個別管理者作成（最小限）

管理者のみ作成する場合：
```bash
python manage.py createsuperuser
```
- Email: `admin@example.com`
- Password: `AdminTest123!`

---

## 実行後の確認

### 1. Django管理画面での確認
1. https://deliverbackend-production-6353.up.railway.app/admin/ にアクセス
2. 管理者でログイン（`admin@example.com` / `AdminTest123!`）
3. ユーザー一覧で3名のユーザーが作成されていることを確認

### 2. API経由での確認
```bash
# トークン取得
curl -X POST https://deliverbackend-production-6353.up.railway.app/api/auth/token/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin@example.com",
    "password": "AdminTest123!"
  }'

# プロフィール確認（認証必要）
curl -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
     https://deliverbackend-production-6353.up.railway.app/api/auth/profile/
```

---

## テストシナリオ

### 基本的なワークフロー

1. **事業者としてログイン**
   - `company@example.com` でログイン
   - ファイルをアップロード
   - Claude APIで帳票を解析
   - 配送依頼を作成

2. **ドライバーとしてログイン**
   - `driver@example.com` でログイン
   - 利用可能な配送案件を確認
   - 案件を受諾
   - ステータスを更新（配送中→完了）

3. **管理者として確認**
   - Django管理画面で全体データを確認
   - ユーザー、配送依頼、アサインメントの状況を監視

---

## セキュリティ注意事項

⚠️ **重要**: これらは**テスト用アカウント**です

### 本番運用時の対応
1. **パスワード変更**
   ```bash
   python manage.py changepassword admin@example.com
   ```

2. **テストユーザーの削除**
   ```python
   # Django shell
   python manage.py shell
   
   from django.contrib.auth import get_user_model
   User = get_user_model()
   
   # テストユーザー削除
   User.objects.filter(email__in=['admin@example.com', 'company@example.com', 'driver@example.com']).delete()
   ```

3. **本格的な権限管理**
   - Django管理画面でグループ・権限を適切に設定
   - 必要に応じてカスタム権限を追加

---

## トラブルシューティング

### よくある問題

1. **実行権限エラー**
   ```bash
   chmod +x create_test_users.py
   ```

2. **Django設定エラー**
   環境変数が正しく設定されているか確認:
   ```bash
   echo $DJANGO_SETTINGS_MODULE
   ```

3. **データベース接続エラー**
   PostgreSQLサービスが起動しているか確認

4. **既存ユーザーエラー**
   スクリプトは既存ユーザーをスキップするため、エラーではありません

### ログの確認
```bash
railway logs --tail
```

---

## アクセスURL

### Django管理画面
- **URL**: https://deliverbackend-production-6353.up.railway.app/admin/
- **ログイン**: 管理者アカウント（`admin@example.com` / `AdminTest123!`）を使用

### API エンドポイント
- **ベースURL**: https://deliverbackend-production-6353.up.railway.app/api/
- **認証エンドポイント**: `/api/auth/token/`（JWT認証）

### フロントエンドアプリケーション
- **URL**: https://deliverfrontend-production.up.railway.app/

## 次のステップ

1. **フロントエンド連携**
   - フロントエンドアプリでログイン機能をテスト
   - API通信の動作確認

2. **データの作成**
   - サンプル配送依頼の作成
   - テスト用ファイルのアップロード

3. **パフォーマンステスト**
   - 複数ユーザーでの同時アクセステスト
   - 大容量ファイルアップロードテスト

4. **監視設定**
   - エラーログの監視
   - パフォーマンスメトリクスの設定