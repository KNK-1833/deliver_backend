# データベース構成仕様書

## 概要
配送サポートシステムのPostgreSQLデータベース構成を詳述します。

## データベース環境
- **RDBMS**: PostgreSQL
- **ローカル開発**: `delivery_support_dev`
- **本番環境**: Railway PostgreSQL
- **テスト環境**: `test_delivery_support_test`

## テーブル構成

### 🔑 基本情報
- **主キー**: 全テーブルで `id` (BigAutoField)
- **タイムスタンプ**: `created_at`, `updated_at` (自動設定)
- **文字コード**: UTF-8
- **照合順序**: C (PostgreSQL標準)

---

## 📊 ユーザー管理 (users アプリ)

### 1. users_user (メインユーザーテーブル)
Django AbstractUser を拡張したカスタムユーザーモデル

| カラム名 | 型 | 制約 | 説明 |
|---------|---|------|------|
| `id` | BigAutoField | PRIMARY KEY | ユーザーID |
| `username` | CharField(150) | UNIQUE, NOT NULL | ユーザー名 |
| `email` | EmailField(254) | UNIQUE, NOT NULL | メールアドレス(ログイン用) |
| `first_name` | CharField(150) | | 名 |
| `last_name` | CharField(150) | | 姓 |
| `phone_number` | CharField(20) | | 電話番号 |
| `user_type` | CharField(20) | DEFAULT 'driver' | ユーザータイプ |
| `is_verified` | BooleanField | DEFAULT False | メール認証済みフラグ |
| `is_active` | BooleanField | DEFAULT True | アクティブフラグ |
| `is_staff` | BooleanField | DEFAULT False | スタッフ権限 |
| `is_superuser` | BooleanField | DEFAULT False | スーパーユーザー権限 |
| `password` | CharField(128) | NOT NULL | ハッシュ化パスワード |
| `last_login` | DateTimeField | NULL | 最終ログイン日時 |
| `date_joined` | DateTimeField | auto_now_add | アカウント作成日時 |
| `created_at` | DateTimeField | auto_now_add | 作成日時 |
| `updated_at` | DateTimeField | auto_now | 更新日時 |

**インデックス:**
- `email` (UNIQUE)
- `username` (UNIQUE)

**user_type の選択値:**
- `driver`: ドライバー
- `company`: 事業者
- `seed`: シードユーザー

### 2. users_driverprofile (ドライバープロフィール)
ドライバー固有の情報

| カラム名 | 型 | 制約 | 説明 |
|---------|---|------|------|
| `id` | BigAutoField | PRIMARY KEY | プロフィールID |
| `user_id` | BigInteger | FOREIGN KEY, UNIQUE | ユーザーID |
| `license_number` | CharField(50) | | 運転免許証番号 |
| `vehicle_type` | CharField(20) | | 車両タイプ |
| `vehicle_number` | CharField(20) | | 車両番号 |
| `is_available` | BooleanField | DEFAULT True | 稼働可能フラグ |
| `current_location_lat` | DecimalField(9,6) | NULL | 現在位置(緯度) |
| `current_location_lng` | DecimalField(9,6) | NULL | 現在位置(経度) |
| `created_at` | DateTimeField | auto_now_add | 作成日時 |
| `updated_at` | DateTimeField | auto_now | 更新日時 |

**リレーション:**
- `user`: OneToOneField → `users_user.id`

**vehicle_type の選択値:**
- `motorcycle`: バイク
- `light_truck`: 軽トラック
- `truck`: トラック

---

## 🚚 配送管理 (delivery アプリ)

### 3. delivery_deliveryrequest (配送依頼)
配送案件の基本情報

| カラム名 | 型 | 制約 | 説明 |
|---------|---|------|------|
| `id` | BigAutoField | PRIMARY KEY | 配送依頼ID |
| `requester_id` | BigInteger | FOREIGN KEY, NOT NULL | 依頼者ID |
| `title` | CharField(200) | NOT NULL | 案件名 |
| `description` | TextField | | 詳細説明 |
| **差出人情報** |
| `sender_name` | CharField(100) | NOT NULL | 差出人名 |
| `sender_phone` | CharField(20) | NOT NULL | 差出人電話番号 |
| `sender_address` | TextField | NOT NULL | 差出人住所 |
| `sender_lat` | DecimalField(9,6) | NULL | 差出人緯度 |
| `sender_lng` | DecimalField(9,6) | NULL | 差出人経度 |
| **配送先情報** |
| `recipient_name` | CharField(100) | NOT NULL | 受取人名 |
| `recipient_phone` | CharField(20) | NOT NULL | 受取人電話番号 |
| `recipient_address` | TextField | NOT NULL | 配送先住所 |
| `recipient_lat` | DecimalField(9,6) | NULL | 配送先緯度 |
| `recipient_lng` | DecimalField(9,6) | NULL | 配送先経度 |
| **荷物情報** |
| `item_name` | CharField(200) | NOT NULL | 荷物名 |
| `item_quantity` | PositiveIntegerField | DEFAULT 1 | 数量 |
| `item_weight` | DecimalField(5,2) | NULL | 重量(kg) |
| `item_size` | CharField(100) | | サイズ |
| **配送条件** |
| `delivery_date` | DateField | NOT NULL | 配送希望日 |
| `delivery_time` | CharField(50) | | 配送希望時間 |
| `special_instructions` | TextField | | 特別な指示 |
| **料金情報** |
| `request_amount` | DecimalField(10,2) | NULL | 依頼金額 |
| `estimated_fee` | DecimalField(10,2) | NULL | 見積料金 |
| `final_fee` | DecimalField(10,2) | NULL | 確定料金 |
| `driver_reward` | DecimalField(10,2) | NULL | ドライバー報酬 |
| `seed_user_id` | BigInteger | FOREIGN KEY, NULL | 管理シードユーザーID |
| **ステータス** |
| `status` | CharField(20) | DEFAULT 'pending' | ステータス |
| `created_at` | DateTimeField | auto_now_add | 作成日時 |
| `updated_at` | DateTimeField | auto_now | 更新日時 |

**リレーション:**
- `requester`: ForeignKey → `users_user.id`
- `seed_user`: ForeignKey → `users_user.id` (user_type='seed')

**インデックス:**
- `requester_id`
- `status`
- `created_at` (降順)

**status の選択値:**
- `pending`: 受付中
- `assigned`: アサイン済み
- `in_progress`: 配送中
- `completed`: 配送完了
- `cancelled`: キャンセル

### 4. delivery_assignment (配送アサイン)
ドライバーへの配送案件割り当て

| カラム名 | 型 | 制約 | 説明 |
|---------|---|------|------|
| `id` | BigAutoField | PRIMARY KEY | アサインID |
| `delivery_request_id` | BigInteger | FOREIGN KEY, NOT NULL | 配送依頼ID |
| `driver_id` | BigInteger | FOREIGN KEY, NOT NULL | ドライバーID |
| `assigned_by_id` | BigInteger | FOREIGN KEY, NULL | 割り当て者ID |
| `status` | CharField(20) | DEFAULT 'accepted' | アサインステータス |
| **時間記録** |
| `pickup_time` | DateTimeField | NULL | 集荷時刻 |
| `delivery_time` | DateTimeField | NULL | 配送時刻 |
| **評価** |
| `driver_rating` | PositiveIntegerField | NULL | ドライバー評価(1-5) |
| `requester_rating` | PositiveIntegerField | NULL | 依頼者評価(1-5) |
| `notes` | TextField | | メモ |
| `created_at` | DateTimeField | auto_now_add | 作成日時 |
| `updated_at` | DateTimeField | auto_now | 更新日時 |

**リレーション:**
- `delivery_request`: ForeignKey → `delivery_deliveryrequest.id`
- `driver`: ForeignKey → `users_user.id` (user_type='driver')
- `assigned_by`: ForeignKey → `users_user.id`

**インデックス:**
- `delivery_request_id`
- `driver_id`
- `status`
- `created_at` (降順)

**status の選択値:**
- `accepted`: 受諾
- `in_progress`: 配送中
- `completed`: 完了
- `rejected`: 拒否

---

## 📁 ファイル管理 (files アプリ)

### 5. files_fileupload (ファイルアップロード)
アップロードファイルとClaude API処理結果

| カラム名 | 型 | 制約 | 説明 |
|---------|---|------|------|
| `id` | BigAutoField | PRIMARY KEY | ファイルID |
| `uploader_id` | BigInteger | FOREIGN KEY, NOT NULL | アップロード者ID |
| `file` | FileField | NOT NULL | ファイルパス |
| `original_name` | CharField(255) | NOT NULL | 元のファイル名 |
| `file_type` | CharField(20) | DEFAULT 'delivery_document' | ファイルタイプ |
| `file_size` | PositiveIntegerField | NOT NULL | ファイルサイズ(バイト) |
| `mime_type` | CharField(100) | NOT NULL | MIMEタイプ |
| **Claude API関連** |
| `is_processed` | BooleanField | DEFAULT False | Claude処理済みフラグ |
| `claude_response` | JSONField | NULL | Claude APIレスポンス |
| `extracted_data` | JSONField | NULL | 抽出されたデータ |
| `delivery_request_id` | BigInteger | FOREIGN KEY, NULL | 関連配送案件ID |
| `created_at` | DateTimeField | auto_now_add | 作成日時 |
| `updated_at` | DateTimeField | auto_now | 更新日時 |

**リレーション:**
- `uploader`: ForeignKey → `users_user.id`
- `delivery_request`: ForeignKey → `delivery_deliveryrequest.id`

**インデックス:**
- `uploader_id`
- `file_type`
- `is_processed`
- `created_at` (降順)

**file_type の選択値:**
- `delivery_document`: 配送帳票
- `receipt`: 受領書
- `other`: その他

**ファイル保存パス:**
- パターン: `uploads/{YYYY}/{MM}/{DD}/filename`
- 例: `uploads/2025/01/06/document.pdf`

---

## 🔗 システムテーブル (Django標準)

### 6. django_migrations (マイグレーション履歴)
Djangoマイグレーションの実行履歴

| カラム名 | 型 | 制約 | 説明 |
|---------|---|------|------|
| `id` | BigAutoField | PRIMARY KEY | ID |
| `app` | CharField(255) | NOT NULL | アプリ名 |
| `name` | CharField(255) | NOT NULL | マイグレーション名 |
| `applied` | DateTimeField | NOT NULL | 適用日時 |

### 7. auth_group / auth_group_permissions (権限管理)
Django標準の権限管理テーブル

### 8. django_content_type (コンテンツタイプ)
Djangoのコンテンツタイプシステム

### 9. auth_permission (権限)
Django標準の権限テーブル

### 10. django_admin_log (管理画面ログ)
Django管理画面での操作ログ

### 11. django_session (セッション)
Djangoセッション管理

---

## 📐 リレーションシップ図

```
users_user (1)
├─ users_driverprofile (1:1)
├─ delivery_deliveryrequest (1:N) [requester]
├─ delivery_deliveryrequest (1:N) [seed_user] 
├─ delivery_assignment (1:N) [driver]
├─ delivery_assignment (1:N) [assigned_by]
└─ files_fileupload (1:N) [uploader]

delivery_deliveryrequest (1)
├─ delivery_assignment (1:N)
└─ files_fileupload (1:N)
```

## 🗂️ インデックス戦略

### 主要インデックス
- **users_user**: `email` (UNIQUE), `username` (UNIQUE)
- **delivery_deliveryrequest**: `status`, `created_at DESC`, `requester_id`
- **delivery_assignment**: `driver_id`, `status`, `created_at DESC`
- **files_fileupload**: `uploader_id`, `is_processed`, `created_at DESC`

### 複合インデックス候補
- **delivery_deliveryrequest**: (`status`, `created_at DESC`)
- **delivery_assignment**: (`driver_id`, `status`)
- **files_fileupload**: (`uploader_id`, `is_processed`)

## 💾 データ容量見積もり

### テーブルサイズ予想 (1年間)
- **users_user**: ~1,000レコード × 1KB = ~1MB
- **delivery_deliveryrequest**: ~10,000レコード × 2KB = ~20MB
- **delivery_assignment**: ~8,000レコード × 1KB = ~8MB
- **files_fileupload**: ~5,000レコード × 500B = ~2.5MB

**総計**: ~32MB (メタデータ除く)

### ファイルストレージ
- **アップロードファイル**: 月間100GB想定
- **バックアップ**: フルバックアップ月1回、差分バックアップ日次

## 🛡️ セキュリティ設定

### パスワード暗号化
- **アルゴリズム**: Django標準 (PBKDF2)
- **ハッシュ**: SHA256
- **イテレーション**: 390,000回以上

### 機密データ
- **PII保護**: 名前、住所、電話番号
- **位置情報**: 緯度経度データの適切な権限制御
- **ファイル**: アップロードファイルのアクセス制御

### アクセス制御
- **認証**: JWT ベース
- **認可**: ユーザータイプベース
- **API制限**: レート制限、CORS設定

## 📊 監視・メンテナンス

### 定期実行推奨
- **VACUUM**: 週次 (PostgreSQL)
- **REINDEX**: 月次
- **統計情報更新**: 日次
- **バックアップ**: 日次 (Railway自動)

### パフォーマンス監視
- **スロークエリ**: > 1秒
- **接続数**: 同時接続数監視
- **テーブルサイズ**: 成長率監視

---

## 更新履歴
- **2025-01-06**: 初版作成
- **構成**: PostgreSQL統一、Railway本番環境対応