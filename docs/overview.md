# Vibe Coding アプリ開発用 アーキテクチャ設計（Claude OCR・React対応版）

## ✅ 技術前提（最新）
- フロントエンド：React（Web）
- 帳票解析：Claude API（画像直接入力によるOCR＋構造化）
- CI/CD：GitHub Actions

---

## 🖥️ フロントエンド（React）
- フレームワーク：React（Vite or Next.js）
- 状態管理：Zustand または Redux Toolkit
- 画面遷移：React Router または Next.js Routing
- ファイルアップロード：`<input type="file">` + `FormData`
- 認証情報保存：localStorage / Cookie（HttpOnly）
- 地図表示：Google Maps JavaScript API または Leaflet

---

## 🔧 バックエンド（APIサーバー）
- 言語／FW：Python（Django REST Framework or FastAPI）
- DB：PostgreSQL（Render / Railway）
- 認証：JWTベース
- ストレージ：S3互換（Supabase Storage等）

---

## 📄 帳票解析（Claude API）

### 処理フロー（更新）
1. Reactフロントから画像をアップロード
2. バックエンドでClaude APIに画像（jpg/png/pdf）をそのまま送信
3. ClaudeがOCRと構造化を一括処理 → JSON出力
4. JSONをDBに保存し、案件として表示

### Claude APIの使い方（概要）
- 画像ファイルをBase64またはマルチパート形式で送信
- プロンプト例（英語）：
This is a Japanese delivery instruction document. Extract structured data including: sender, recipient, delivery address, item name, quantity, and requested date. The document may be rotated or handwritten.

---

## 🛠 CI/CD（GitHub Actions）
- ESLint, Jest, Pytest の自動実行
- React → Netlify / Vercel デプロイ or 静的ビルド
- バックエンド → Render / Railway 自動デプロイ

---

## ☁ ファイル管理
- ファイルはS3互換へ保存し、Claudeへ転送用に一時URLを発行
- 保存後はOCR結果と一緒に紐付け（FileUpload → DeliveryRequest）

---

## 🔐 セキュリティ
- HTTPS通信
- JWT認証＋ロール制御
- Claude APIとのやりとりは内部APIで管理
- アクセス制御：アップロードユーザーまたは案件関係者のみ可

---

## 📌 今後の設計タスク
1. Claude API用の画像→JSONプロンプトテンプレート設計
2. ファイルアップロード→Claude呼び出しまでのAPI設計
3. 画面フロー・UX設計（React側）
4. DBモデル定義（ER図に基づく実装）
