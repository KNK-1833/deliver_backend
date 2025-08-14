# フロントエンドデザインコンセプト

## 1. デザイン理念

### 基本方針
配送サポートシステムは、個人事業主の配送ドライバーと事業者を繋ぐプラットフォームとして、**効率性**、**明確性**、**信頼性**を最優先に設計されています。

### ターゲットユーザー
- **主要ユーザー**: 個人事業主の配送ドライバーを統括する事業者
- **副次ユーザー**: 個人事業主の配送ドライバー
- **利用環境**: モバイル端末（スマートフォン）、タブレット、デスクトップPC
- **使用シーン**: 移動中、現場作業中、オフィス業務中

### デザイン原則
1. **モバイルファースト**: スマートフォンでの操作性を最優先
2. **ミニマリズム**: 必要最小限の要素で最大の効果
3. **一貫性**: 統一されたインタラクションパターン
4. **アクセシビリティ**: すべてのユーザーが利用可能

---

## 2. デザインシステム基盤

### コンポーネントライブラリ
**shadcn/ui** (https://ui.shadcn.com/docs/components)
- Radix UIをベースとした高品質なコンポーネント
- 完全なカスタマイズ性とアクセシビリティ対応
- TypeScriptによる型安全性

### デザインガイドライン
**デジタル庁デザインシステム** (https://design.digital.go.jp/foundations/)
- 日本の公共サービス向けデザイン原則に準拠
- ユーザビリティとアクセシビリティを重視
- 明確で分かりやすい情報設計

---

## 3. カラーシステム

### プライマリカラー
```css
--primary: 222.2 47.4% 11.2%;        /* メインアクション、重要な要素 */
--primary-foreground: 210 40% 98%;   /* プライマリ上のテキスト */
```

### セマンティックカラー
```css
/* 成功・完了状態 */
--success: 142 76% 36%;
--success-foreground: 355 100% 100%;

/* 警告・注意状態 */
--warning: 38 92% 50%;
--warning-foreground: 48 96% 89%;

/* エラー・危険状態 */
--destructive: 0 84.2% 60.2%;
--destructive-foreground: 210 40% 98%;

/* 情報提供 */
--info: 199 89% 48%;
--info-foreground: 221 100% 100%;
```

### ニュートラルカラー
```css
--background: 0 0% 100%;              /* 背景色 */
--foreground: 222.2 84% 4.9%;        /* テキスト色 */
--muted: 210 40% 96%;                /* 補助的な背景 */
--muted-foreground: 215.4 16.3% 46.9%; /* 補助テキスト */
```

### 使用ルール
- **プライマリカラー**: CTA、主要なアクション
- **セカンダリカラー**: 補助的なアクション
- **セマンティックカラー**: 状態表示（成功、警告、エラー）
- **ニュートラルカラー**: 背景、ボーダー、テキスト

---

## 4. タイポグラフィ

### フォントファミリー
```css
--font-sans: 'Inter', 'Hiragino Kaku Gothic ProN', 'Hiragino Sans', 
             Meiryo, sans-serif;
--font-mono: 'JetBrains Mono', 'SF Mono', Consolas, monospace;
```

### フォントサイズ（モバイル優先）
```css
/* モバイル（base） */
--text-xs: 0.75rem;    /* 12px - 補足情報 */
--text-sm: 0.875rem;   /* 14px - 標準テキスト */
--text-base: 1rem;     /* 16px - 本文 */
--text-lg: 1.125rem;   /* 18px - 小見出し */
--text-xl: 1.25rem;    /* 20px - 見出し */
--text-2xl: 1.5rem;    /* 24px - 大見出し */

/* デスクトップ（768px以上） */
@media (min-width: 768px) {
  /* 各サイズを1.125倍にスケール */
}
```

### フォントウェイト
- **通常テキスト**: 400 (Regular)
- **強調テキスト**: 500 (Medium)
- **見出し**: 600 (SemiBold)
- **重要な見出し**: 700 (Bold)

### 行間
- **タイトテキスト**: 1.25
- **本文**: 1.5
- **リラックステキスト**: 1.75

---

## 5. スペーシングシステム

### 8pxグリッドシステム
```css
--space-0: 0;        /* 0px */
--space-1: 0.25rem;  /* 4px */
--space-2: 0.5rem;   /* 8px */
--space-3: 0.75rem;  /* 12px */
--space-4: 1rem;     /* 16px */
--space-5: 1.25rem;  /* 20px */
--space-6: 1.5rem;   /* 24px */
--space-8: 2rem;     /* 32px */
--space-10: 2.5rem;  /* 40px */
--space-12: 3rem;    /* 48px */
```

### 使用ガイドライン
- **コンポーネント内部**: space-2, space-3
- **コンポーネント間**: space-4, space-6
- **セクション間**: space-8, space-12
- **モバイルでは1段階小さいスペーシングを使用**

---

## 6. コンポーネント設計

### shadcn/uiコンポーネント使用方針

#### Button
```tsx
// プライマリアクション
<Button variant="default">配送依頼作成</Button>

// セカンダリアクション
<Button variant="outline">キャンセル</Button>

// 危険なアクション
<Button variant="destructive">削除</Button>

// モバイル最適化
<Button className="w-full" size="lg">次へ</Button>
```

#### Card
```tsx
// 情報表示カード
<Card>
  <CardHeader>
    <CardTitle>配送依頼 #001</CardTitle>
    <CardDescription>2024年8月8日</CardDescription>
  </CardHeader>
  <CardContent>
    {/* コンテンツ */}
  </CardContent>
</Card>
```

#### Form
```tsx
// react-hook-form + zodによる型安全なフォーム
<Form {...form}>
  <FormField
    control={form.control}
    name="email"
    render={({ field }) => (
      <FormItem>
        <FormLabel>メールアドレス</FormLabel>
        <FormControl>
          <Input placeholder="example@domain.com" {...field} />
        </FormControl>
        <FormMessage />
      </FormItem>
    )}
  />
</Form>
```

### モバイル対応パターン

#### レスポンシブグリッド
```tsx
// モバイル: 1カラム、タブレット: 2カラム、デスクトップ: 3カラム
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
  {/* カードコンポーネント */}
</div>
```

#### タッチフレンドリーUI
```tsx
// 最小タッチターゲット: 44x44px
<Button className="min-h-[44px] min-w-[44px]">
  <Icon className="h-5 w-5" />
</Button>
```

#### モバイルナビゲーション
```tsx
// Sheet（サイドドロワー）によるナビゲーション
<Sheet>
  <SheetTrigger asChild>
    <Button variant="ghost" size="icon">
      <Menu className="h-5 w-5" />
    </Button>
  </SheetTrigger>
  <SheetContent side="right">
    {/* ナビゲーションメニュー */}
  </SheetContent>
</Sheet>
```

---

## 7. インタラクション設計

### タッチインタラクション
- **最小タッチ領域**: 44x44px（デジタル庁ガイドライン準拠）
- **タップフィードバック**: active状態でscale(0.95)
- **スワイプ対応**: 横スワイプでナビゲーション表示

### トランジション
```css
--transition-fast: 150ms ease-in-out;    /* ホバー効果 */
--transition-base: 200ms ease-in-out;    /* 通常の状態変化 */
--transition-slow: 300ms ease-in-out;    /* モーダル表示 */
```

### ローディング状態
```tsx
// スピナー表示
<Button disabled={isLoading}>
  {isLoading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
  {isLoading ? '処理中...' : '送信'}
</Button>
```

### エラー処理
```tsx
// エラーメッセージ表示
<div className="bg-destructive/15 border border-destructive/20 text-destructive">
  <AlertCircle className="h-4 w-4" />
  <span>{error.message}</span>
</div>
```

---

## 8. レスポンシブデザイン

### ブレークポイント
```css
/* Tailwind CSS デフォルト */
sm: 640px   /* スマートフォン（横向き） */
md: 768px   /* タブレット */
lg: 1024px  /* 小型デスクトップ */
xl: 1280px  /* デスクトップ */
2xl: 1536px /* 大型デスクトップ */
```

### モバイルファースト設計
1. **基本設計はモバイル幅（320px-375px）**
2. **プログレッシブエンハンスメント**で大画面対応
3. **コンテンツ優先順位**の明確化

### レイアウトパターン

#### モバイル（< 768px）
- シングルカラムレイアウト
- 垂直スタック
- フルワイドボタン
- 折りたたみ可能なナビゲーション

#### タブレット（768px - 1024px）
- 2カラムグリッド
- サイドバーナビゲーション
- モーダルダイアログ

#### デスクトップ（> 1024px）
- 3カラムグリッド
- 固定ヘッダー・サイドバー
- ホバーインタラクション

---

## 9. パフォーマンス最適化

### 画像最適化
- WebP形式の使用
- 遅延ローディング
- レスポンシブ画像（srcset）

### コンポーネント最適化
- React.memoによるメモ化
- useMemoとuseCallbackの適切な使用
- 仮想スクロール（大量データ表示時）

### バンドルサイズ
- shadcn/uiの必要コンポーネントのみインポート
- Tree-shakingによる未使用コード削除
- Code splittingによる遅延ローディング

---

## 10. アクセシビリティ

### WCAG 2.1 Level AA準拠
- **カラーコントラスト**: 最小4.5:1（通常テキスト）、3:1（大きいテキスト）
- **キーボードナビゲーション**: すべての機能がキーボードで操作可能
- **スクリーンリーダー対応**: 適切なARIAラベルとロール

### フォーカス管理
```css
/* フォーカスリング */
:focus-visible {
  outline: 2px solid var(--ring);
  outline-offset: 2px;
}
```

### エラーメッセージ
- 明確で具体的なエラー内容
- 解決方法の提示
- アイコンと色による視覚的補助

---

## 11. 実装ガイドライン

### コンポーネント作成手順
1. shadcn/uiの既存コンポーネントを確認
2. デジタル庁ガイドラインとの整合性確認
3. モバイルファーストで実装
4. アクセシビリティテスト
5. パフォーマンステスト

### 命名規則
- **コンポーネント**: PascalCase（例: `DeliveryCard`）
- **ユーティリティ関数**: camelCase（例: `formatDate`）
- **定数**: UPPER_SNAKE_CASE（例: `MAX_FILE_SIZE`）
- **CSSクラス**: kebab-case（Tailwind CSS準拠）

### テスト方針
- モバイル端末での実機テスト必須
- 主要ブラウザ（Chrome, Safari, Firefox）対応
- タッチデバイスとマウスデバイス両対応

---

## 12. 今後の拡張性

### プログレッシブウェブアプリ（PWA）
- オフライン対応
- プッシュ通知
- ホーム画面追加

### 国際化（i18n）
- 多言語対応の準備
- RTL（右から左）レイアウト対応

### ダークモード
- システム設定連動
- 手動切り替え機能
- カラーシステムの拡張

---

## 参考資料

- [shadcn/ui Documentation](https://ui.shadcn.com/docs/components)
- [デジタル庁デザインシステム](https://design.digital.go.jp/foundations/)
- [WCAG 2.1 Guidelines](https://www.w3.org/WAI/WCAG21/quickref/)
- [Material Design for Mobile](https://material.io/design/platform-guidance/android-mobile.html)
- [iOS Human Interface Guidelines](https://developer.apple.com/design/human-interface-guidelines/)