# 配送案件管理システム デザインガイドライン

## 1. 概要

本ドキュメントは、配送案件管理システムのUIデザインにおける基本方針と実装ガイドラインを定めます。
デジタル庁デザインシステムの原則を参考に、一貫性があり、アクセシブルで、使いやすいインターフェースの実現を目指します。

## 2. デザイン原則

### 2.1 基本理念
- **一貫性**: システム全体で統一された視覚言語を使用
- **明確性**: 情報の優先順位と階層構造を明確に表現
- **アクセシビリティ**: すべてのユーザーが利用可能な設計
- **レスポンシブ**: モバイルファーストで様々なデバイスに対応

## 3. カラーシステム

### 3.1 カラーパレット

#### プライマリカラー
```css
--color-primary-50: #EFF6FF;   /* 最も薄い */
--color-primary-100: #DBEAFE;
--color-primary-200: #BFDBFE;
--color-primary-300: #93C5FD;
--color-primary-400: #60A5FA;
--color-primary-500: #3B82F6;  /* ベース */
--color-primary-600: #2563EB;  /* ホバー */
--color-primary-700: #1D4ED8;
--color-primary-800: #1E40AF;
--color-primary-900: #1E3A8A;  /* 最も濃い */
```

#### ニュートラルカラー
```css
--color-neutral-0: #FFFFFF;
--color-neutral-50: #FAFAFA;
--color-neutral-100: #F4F4F5;
--color-neutral-200: #E4E4E7;
--color-neutral-300: #D4D4D8;
--color-neutral-400: #A1A1AA;
--color-neutral-500: #71717A;
--color-neutral-600: #52525B;
--color-neutral-700: #3F3F46;
--color-neutral-800: #27272A;
--color-neutral-900: #18181B;
```

#### セマンティックカラー
```css
/* 成功 */
--color-success-50: #F0FDF4;
--color-success-500: #22C55E;
--color-success-600: #16A34A;
--color-success-700: #15803D;

/* 警告 */
--color-warning-50: #FFFBEB;
--color-warning-500: #F59E0B;
--color-warning-600: #D97706;
--color-warning-700: #B45309;

/* エラー・危険 */
--color-danger-50: #FEF2F2;
--color-danger-500: #EF4444;
--color-danger-600: #DC2626;
--color-danger-700: #B91C1C;

/* 情報 */
--color-info-50: #EFF6FF;
--color-info-500: #3B82F6;
--color-info-600: #2563EB;
--color-info-700: #1D4ED8;
```

### 3.2 カラー使用ガイドライン

- **背景色**: neutral-0（白）またはneutral-50を基本とする
- **テキスト色**: neutral-900（本文）、neutral-700（補助テキスト）
- **ボーダー**: neutral-200を基本、ホバー時はneutral-300
- **アクション**: primary-600を基本、ホバー時はprimary-700
- **コントラスト比**: WCAG 2.1 AA基準（4.5:1以上）を満たす

## 4. タイポグラフィ

### 4.1 フォントファミリー
```css
--font-sans: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', 
             'Hiragino Kaku Gothic ProN', 'Hiragino Sans', Meiryo, 
             sans-serif;
--font-mono: 'JetBrains Mono', 'SF Mono', Consolas, monospace;
```

### 4.2 フォントサイズ
```css
--text-xs: 0.75rem;    /* 12px */
--text-sm: 0.875rem;   /* 14px */
--text-base: 1rem;     /* 16px - 基本サイズ */
--text-lg: 1.125rem;   /* 18px */
--text-xl: 1.25rem;    /* 20px */
--text-2xl: 1.5rem;    /* 24px */
--text-3xl: 1.875rem;  /* 30px */
--text-4xl: 2.25rem;   /* 36px */
```

### 4.3 フォントウェイト
```css
--font-normal: 400;
--font-medium: 500;
--font-semibold: 600;
--font-bold: 700;
```

### 4.4 行間（Line Height）
```css
--leading-tight: 1.25;
--leading-normal: 1.5;   /* 基本 */
--leading-relaxed: 1.75;
```

## 5. スペーシング

### 5.1 基本単位（8pxグリッド）
```css
--space-0: 0;
--space-1: 0.25rem;   /* 4px */
--space-2: 0.5rem;    /* 8px - 基本単位 */
--space-3: 0.75rem;   /* 12px */
--space-4: 1rem;      /* 16px */
--space-5: 1.25rem;   /* 20px */
--space-6: 1.5rem;    /* 24px */
--space-8: 2rem;      /* 32px */
--space-10: 2.5rem;   /* 40px */
--space-12: 3rem;     /* 48px */
--space-16: 4rem;     /* 64px */
```

### 5.2 スペーシング使用ガイドライン
- **コンポーネント内**: space-2（8px）またはspace-3（12px）
- **コンポーネント間**: space-4（16px）またはspace-6（24px）
- **セクション間**: space-8（32px）またはspace-12（48px）
- **ページパディング**: モバイル space-4、デスクトップ space-6

## 6. レイアウト

### 6.1 ブレークポイント
```css
--breakpoint-sm: 640px;   /* スマートフォン（横向き） */
--breakpoint-md: 768px;   /* タブレット（縦向き） */
--breakpoint-lg: 1024px;  /* タブレット（横向き）・小型デスクトップ */
--breakpoint-xl: 1280px;  /* デスクトップ */
--breakpoint-2xl: 1536px; /* 大型デスクトップ */
```

### 6.2 コンテナ最大幅
```css
--max-width-sm: 640px;
--max-width-md: 768px;
--max-width-lg: 1024px;
--max-width-xl: 1280px;
--max-width-2xl: 1536px;
--max-width-full: 100%;
```

### 6.3 グリッドシステム
- 12カラムグリッドを基本とする
- モバイル: 1-2カラム
- タブレット: 2-3カラム
- デスクトップ: 3-4カラム

## 7. コンポーネント

### 7.1 角丸（Border Radius）
```css
--radius-none: 0;
--radius-sm: 0.125rem;   /* 2px */
--radius-base: 0.25rem;  /* 4px */
--radius-md: 0.375rem;   /* 6px */
--radius-lg: 0.5rem;     /* 8px - 基本 */
--radius-xl: 0.75rem;    /* 12px */
--radius-2xl: 1rem;      /* 16px */
--radius-full: 9999px;   /* 完全円形 */
```

### 7.2 影（Shadow）
```css
--shadow-sm: 0 1px 2px 0 rgb(0 0 0 / 0.05);
--shadow-base: 0 1px 3px 0 rgb(0 0 0 / 0.1), 
               0 1px 2px -1px rgb(0 0 0 / 0.1);
--shadow-md: 0 4px 6px -1px rgb(0 0 0 / 0.1), 
             0 2px 4px -2px rgb(0 0 0 / 0.1);
--shadow-lg: 0 10px 15px -3px rgb(0 0 0 / 0.1), 
             0 4px 6px -4px rgb(0 0 0 / 0.1);
--shadow-xl: 0 20px 25px -5px rgb(0 0 0 / 0.1), 
             0 8px 10px -6px rgb(0 0 0 / 0.1);
```

### 7.3 ボタン
#### サイズ
- **Small**: 高さ32px、パディング8px 12px、フォントサイズ14px
- **Medium**: 高さ40px、パディング10px 16px、フォントサイズ16px（基本）
- **Large**: 高さ48px、パディング12px 20px、フォントサイズ18px

#### バリエーション
- **Primary**: 背景 primary-600、ホバー primary-700
- **Secondary**: 背景 neutral-100、ホバー neutral-200
- **Danger**: 背景 danger-600、ホバー danger-700
- **Ghost**: 背景 transparent、ホバー neutral-100

### 7.4 フォーム要素
- **入力フィールド高さ**: 40px（基本）
- **ボーダー**: 1px solid neutral-300
- **フォーカス**: primary-500のボーダー、shadow-sm
- **ラベル**: フォントサイズ14px、色 neutral-700
- **ヘルプテキスト**: フォントサイズ12px、色 neutral-600
- **エラー**: danger-600のボーダーとテキスト

## 8. インタラクション

### 8.1 トランジション
```css
--transition-fast: 150ms ease-in-out;
--transition-base: 200ms ease-in-out;  /* 基本 */
--transition-slow: 300ms ease-in-out;
```

### 8.2 ホバー状態
- 明度を10%下げる、または影を追加
- カーソルをpointerに変更（クリック可能な要素）
- トランジション時間は200ms

### 8.3 フォーカス状態
- アウトライン: 2px solid primary-500
- アウトラインオフセット: 2px
- 背景色の変更は避ける（アクセシビリティ考慮）

### 8.4 アクティブ状態
- スケール: 0.95（ボタンなど）
- 明度を20%下げる

## 9. アクセシビリティ

### 9.1 基本要件
- WCAG 2.1 レベルAA準拠
- キーボードナビゲーション完全対応
- スクリーンリーダー対応
- 適切なARIAラベルの使用

### 9.2 カラーコントラスト
- 通常テキスト: 4.5:1以上
- 大きいテキスト（18px以上）: 3:1以上
- UIコンポーネント: 3:1以上

### 9.3 タッチターゲット
- 最小サイズ: 44px × 44px（モバイル）
- 推奨サイズ: 48px × 48px
- 要素間の最小余白: 8px

### 9.4 フォーカス管理
- すべてのインタラクティブ要素にフォーカスインジケーター
- タブ順序の論理的な設定
- モーダル内でのフォーカストラップ

## 10. アイコン

### 10.1 サイズ
```css
--icon-xs: 16px;
--icon-sm: 20px;
--icon-base: 24px;  /* 基本 */
--icon-lg: 32px;
--icon-xl: 40px;
```

### 10.2 使用ガイドライン
- ストローク幅: 1.5px〜2px
- 色: テキストと同じ色を使用
- ラベルとの組み合わせ時の余白: 8px
- 装飾的なアイコンには`aria-hidden="true"`を付与

## 11. モバイルファースト設計

### 11.1 タッチ操作の考慮
- スワイプ、ピンチズームなどのジェスチャー対応
- ダブルタップ防止（300msの遅延を避ける）
- 長押しメニューの実装

### 11.2 パフォーマンス
- 画像の遅延読み込み（lazy loading）
- 重要なCSSのインライン化
- フォントの最適化（サブセット化）

## 12. 実装例

### 12.1 ボタンコンポーネント
```css
.btn {
  padding: var(--space-2) var(--space-4);
  font-size: var(--text-base);
  font-weight: var(--font-medium);
  border-radius: var(--radius-lg);
  transition: all var(--transition-base);
  min-height: 40px;
  min-width: 80px;
}

.btn-primary {
  background-color: var(--color-primary-600);
  color: white;
}

.btn-primary:hover {
  background-color: var(--color-primary-700);
}

.btn-primary:focus {
  outline: 2px solid var(--color-primary-500);
  outline-offset: 2px;
}

.btn-primary:active {
  transform: scale(0.95);
}
```

### 12.2 カードコンポーネント
```css
.card {
  background: var(--color-neutral-0);
  border: 1px solid var(--color-neutral-200);
  border-radius: var(--radius-xl);
  padding: var(--space-6);
  box-shadow: var(--shadow-sm);
  transition: all var(--transition-base);
}

.card:hover {
  box-shadow: var(--shadow-md);
  border-color: var(--color-neutral-300);
}
```

## 13. 更新履歴

- 2024.01.08: 初版作成
- デジタル庁デザインシステムの原則を参考に基本方針を策定

## 14. 参考資料

- [デジタル庁デザインシステム](https://design.digital.go.jp/)
- [WCAG 2.1 日本語訳](https://waic.jp/docs/WCAG21/)
- [Material Design Guidelines](https://material.io/design)
- [Apple Human Interface Guidelines](https://developer.apple.com/design/human-interface-guidelines/)