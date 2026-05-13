# Stack Overflow 学習者つまづき分析

Stack Overflow の質問・タグデータから「学習者がつまづくポイント」を分析するデータアナリストポートフォリオ第3作。

マクロ（言語の盛衰）→ メゾ（タグ共起ネットワーク）→ ミクロ（質問本文クラスタリング）の3層分析で、IT業界の学習・採用市場に対する示唆を導く。

## 公開サイト

**GitHub Pages**: https://tetsuN-0320.github.io/stackoverflow-learner-pitfalls/

スクロールテリング型SPAで、以下の4章構成で分析結果を可視化しています。
- 第1幕: 言語の地殻変動（Developer Survey × 回答率トレンド）
- 第2幕: 言語別つまづきマップ（D3.js force-directed ネットワーク）
- 第3幕: 言語別つまづきランキング（TF-IDF+HDBSCAN クラスタリング）
- 第4幕: 学習ロードマップへの示唆

## セットアップ

### 1. リポジトリのクローン

```bash
git clone https://github.com/tetsuN-0320/stackoverflow-learner-pitfalls.git
cd stackoverflow-learner-pitfalls
```

### 2. 仮想環境の構築

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 3. 環境変数の設定

```bash
cp .env.example .env
# .env を編集して STACKEX_API_KEY を設定
```

Stack Exchange API キーは https://stackapps.com/apps/oauth/register で無料取得できます。

### 4. NLPモデルのダウンロード

```bash
python -c "import nltk; nltk.download('stopwords'); nltk.download('punkt'); nltk.download('wordnet')"
python -m spacy download en_core_web_sm
```

### 5. Developer Survey データの配置

https://survey.stackoverflow.co/datasets から各年のZIPをダウンロードし、解凍後に以下のように配置してください。

```
data/raw/developer_survey/
├── 2022/
│   ├── survey_results_public.csv
│   └── survey_results_schema.csv
├── 2023/
│   └── ...
└── 2024/
    └── ...
```

## データ取得

```bash
# 質問データ取得（全対象言語）
python scripts/fetch_questions.py

# タグ統計取得
python scripts/fetch_tags.py
```

## 分析実行

```bash
# 分析パイプライン全実行
python scripts/run_analysis.py

# フロント用JSON生成
python scripts/build_site.py
```

## プロジェクト構成

```
stackoverflow-learner-pitfalls/
├── config/           # API設定・対象言語定義
├── data/             # データ（生データはgit管理外）
├── notebooks/        # 分析ノートブック（EDA〜クラスタリング）
├── src/              # 再利用可能なPythonモジュール
│   ├── api/          # Stack Exchange APIクライアント
│   ├── preprocessing/# テキスト前処理
│   ├── analysis/     # 3層分析ロジック
│   ├── visualization/# 可視化・JSON生成
│   └── utils/        # ロガー・キャッシュ・レート制御
├── web/              # GitHub Pages 公開用フロントエンド
├── tests/            # ユニットテスト
└── scripts/          # CLIスクリプト
```

## データソース

- **Stack Overflow / Stack Exchange API v2.3**
  [Stack Exchange Network 利用規約](https://stackoverflow.com/legal/terms-of-service/public) に基づきCC-BY-SA 4.0 で利用
- **Stack Overflow Developer Survey**
  [insights.stackoverflow.com/survey](https://insights.stackoverflow.com/survey)

## ライセンス

コード: MIT License
データ: CC BY-SA 4.0（Stack Exchange Network より）
