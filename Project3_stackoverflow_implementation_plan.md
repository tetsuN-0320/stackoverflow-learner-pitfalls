# 第3案 実装計画書

**プロジェクト名**: Stack Overflow「学習者がつまづくポイント」分析（Learner Pitfalls in Stack Overflow）
**作成日**: 2026年4月30日
**想定実装期間**: 12〜14日間（実働、1日3〜4時間）／カレンダー上3〜4週間

---

## 1. プロジェクト概要

Stack Exchange API v2.3 から Stack Overflow の質問・タグデータを取得し、言語別の質問量推移、タグ共起ネットワーク、テキストマイニングによる「学習者がつまづくテーマ」の抽出を行う。マクロ（言語の盛衰）→メゾ（タグの組み合わせ）→ミクロ（質問本文の頻出語）の3層分析で、IT業界の学習・採用市場に対する含意のあるストーリーを構築する。

第1作・第2作と異なる **テキストマイニング × ネットワーク可視化 × スクロールテリング型UI** を採用し、データアナリストとしての技術的深度をアピールする。

**最終成果物**

1. GitHub Pages で公開するスクロールテリング型 Web サイト（`/web/`）
2. 分析プロセスを示す Jupyter Notebook 群（`/notebooks/`）
3. 再現可能な Python コードベース（`/src/`）と README
4. ポートフォリオ用の解説記事（業界トレンドと学習ロードマップへの示唆）

**第1作・第2作との差別化**

| 観点 | 第1作（人口予測） | 第2作（ふるさと納税） | 第3作（SO分析） |
|---|---|---|---|
| データ性質 | 公的統計（数値） | 商業データ（半構造） | テキスト＋メタ（半構造） |
| 主要技術 | 時系列予測 | クロスデータ分析 | テキストマイニング・ネットワーク分析 |
| UI形式 | 地図＋スライダー | ダッシュボード | スクロールテリング |
| 主な訴求先 | 公共・地域 | EC・マーケティング | IT・教育・採用 |

---

## 2. ファイル構成

```
stackoverflow-learner-pitfalls/
│
├── README.md                       # プロジェクト概要、セットアップ手順、成果物リンク
├── .gitignore                      # APIキー、生データ、キャッシュを除外
├── .env.example                    # 環境変数テンプレート（STACKEX_API_KEY 等）
├── requirements.txt                # 依存ライブラリ
├── pyproject.toml                  # black/ruff 設定
│
├── config/
│   ├── settings.py                 # API設定、定数
│   └── target_languages.yml        # 分析対象言語と関連タグの設定
│
├── data/
│   ├── raw/
│   │   ├── stackex_cache.sqlite    # Stack Exchange APIレスポンスキャッシュ
│   │   └── developer_survey/       # Stack Overflow Developer Survey CSV
│   │       ├── 2023.csv
│   │       └── 2024.csv
│   ├── processed/
│   │   ├── questions.parquet       # 質問データ（クレンジング済み）
│   │   ├── tags.parquet            # タグマスター
│   │   └── tag_cooccurrence.parquet  # タグ共起行列
│   └── analysis/
│       ├── trends.parquet          # 言語別トレンド集計
│       ├── pitfalls.parquet        # つまづきトピック抽出結果
│       └── networks/               # ネットワーク図用JSON
│           ├── python_network.json
│           ├── javascript_network.json
│           └── go_network.json
│
├── notebooks/
│   ├── 01_data_exploration.ipynb   # EDA：取得データの全体像
│   ├── 02_text_preprocessing.ipynb # テキスト前処理プロセスの可視化
│   ├── 03_trend_analysis.ipynb     # 言語別トレンド分析
│   ├── 04_cooccurrence_network.ipynb  # タグ共起ネットワーク
│   └── 05_pitfall_clustering.ipynb # つまづきトピックのクラスタリング
│
├── src/
│   ├── __init__.py
│   ├── api/
│   │   ├── __init__.py
│   │   ├── stackex_client.py       # Stack Exchange API ラッパー
│   │   ├── survey_loader.py        # Developer Survey CSV ローダー
│   │   └── data_fetcher.py         # 取得タスクのオーケストレーション
│   ├── preprocessing/
│   │   ├── __init__.py
│   │   ├── cleaner.py              # 欠損値・型変換
│   │   ├── tokenizer.py            # 英語＋コードのトークナイズ
│   │   ├── error_extractor.py      # エラーメッセージのパターン抽出
│   │   └── stopwords.py            # ドメイン固有ストップワード
│   ├── analysis/
│   │   ├── __init__.py
│   │   ├── trend.py                # 言語別質問数の時系列分析
│   │   ├── network.py              # タグ共起ネットワーク構築
│   │   ├── clustering.py           # 質問のトピッククラスタリング
│   │   └── pitfall.py              # つまづきパターンの抽出ロジック
│   ├── visualization/
│   │   ├── __init__.py
│   │   ├── network_export.py       # D3.js / Pyvis 用JSON生成
│   │   ├── timeseries.py           # トレンド折れ線グラフ
│   │   └── charts.py               # 横棒グラフ・ヒストグラム
│   └── utils/
│       ├── __init__.py
│       ├── logger.py
│       ├── rate_limiter.py         # Stack Exchange APIレート制御
│       └── cache.py                # SQLiteキャッシュユーティリティ
│
├── web/
│   ├── index.html                  # スクロールテリング・メインページ
│   ├── network.html                # ネットワーク図の詳細ページ
│   ├── about.html                  # データソース・手法・免責事項
│   ├── static/
│   │   ├── css/
│   │   │   ├── main.css
│   │   │   ├── scrollytelling.css  # スクロール演出専用
│   │   │   └── responsive.css
│   │   ├── js/
│   │   │   ├── scroll.js           # IntersectionObserver による章切替
│   │   │   ├── network.js          # D3.js force-directed graph
│   │   │   ├── charts.js           # Plotly チャート差し替え
│   │   │   └── language_switch.js  # 言語タブの切替
│   │   ├── data/
│   │   │   ├── trends.json         # 全言語の年次トレンド
│   │   │   ├── pitfalls.json       # つまづきトピックトップN
│   │   │   └── networks/
│   │   │       ├── python.json
│   │   │       ├── javascript.json
│   │   │       ├── go.json
│   │   │       └── java.json
│   │   └── lib/
│   │       └── d3.v7.min.js        # CDNでも可、オフライン用にローカル配置も検討
│   └── assets/
│       └── images/                 # OG画像、サイトロゴ
│
├── tests/
│   ├── test_api.py
│   ├── test_preprocessing.py
│   ├── test_tokenizer.py
│   ├── test_analysis.py
│   └── test_network.py
│
└── scripts/
    ├── fetch_questions.py          # CLI: 質問データ取得
    ├── fetch_tags.py               # CLI: タグ統計取得
    ├── run_analysis.py             # CLI: 分析パイプライン実行
    └── build_site.py               # CLI: フロント用JSON生成
```

### 設計上の主なポイント

- **3層分析の責務分離**: マクロ（`analysis/trend.py`）、メゾ（`analysis/network.py`）、ミクロ（`analysis/pitfall.py`）を別モジュールにし、各ノートブックと1対1で対応
- **Stack Exchange APIのキャッシュ戦略**: 質問は数万件単位、タグは数千件。SQLite キャッシュは必須。再取得防止＆オフライン分析対応
- **言語別ネットワークJSONを分割**: 全言語を1ファイルに入れると重くなるため、`web/static/data/networks/` 配下に言語別で分割し、選択時に動的ロード
- **`config/target_languages.yml`** で対象言語を YAML 管理: 後から「Rust も追加したい」となった場合に YAML を編集するだけで分析パイプラインに反映
- **D3.js は CDN 推奨だがローカル配置オプションも**: `static/lib/` を用意することで、オフラインでも動作確認できる構造に

---

## 3. 必要ライブラリ

### 3.1 requirements.txt（推奨バージョン）

```
# === API・HTTP ===
requests>=2.31.0
python-dotenv>=1.0.0
tenacity>=8.2.0

# === データ処理 ===
pandas>=2.1.0
numpy>=1.26.0
pyarrow>=14.0.0
pyjanitor>=0.26.0
pyyaml>=6.0.1

# === テキスト処理・NLP ===
nltk>=3.8.1              # 英語のトークナイズ・ストップワード
spacy>=3.7.0             # 高度なNLP（依存解析、固有表現等）
beautifulsoup4>=4.12.0   # 質問本文のHTML除去
markdown>=3.5.0          # Markdown→プレーンテキスト変換

# === ネットワーク分析 ===
networkx>=3.2            # グラフ構造、中心性計算
pyvis>=0.3.2             # ネットワーク可視化（プロトタイプ用）
python-louvain>=0.16     # コミュニティ検出（Louvain法）

# === 機械学習・クラスタリング ===
scikit-learn>=1.3.0      # K-means、TF-IDF
sentence-transformers>=2.2.0  # 質問の意味的類似度（重ければ削除可）
hdbscan>=0.8.33          # 密度ベースクラスタリング

# === 可視化 ===
plotly>=5.17.0
kaleido>=0.2.1
matplotlib>=3.8.0
wordcloud>=1.9.2         # ワードクラウド（補助）

# === 開発ツール ===
jupyter>=1.0.0
ipywidgets>=8.1.0
black>=23.10.0
ruff>=0.1.5
pytest>=7.4.0
mypy>=1.6.0

# === ロギング ===
loguru>=0.7.2
```

### 3.2 ライブラリ選定の根拠（第1作・第2作との差分）

| カテゴリ | 採用ライブラリ | 理由 |
|---|---|---|
| 英語NLP基礎 | nltk | 軽量・定番、ストップワード辞書とトークナイザがすぐ使える |
| 高度NLP | spacy | 必要に応じて依存解析・固有表現抽出を追加できる拡張性 |
| HTML除去 | beautifulsoup4 | 質問本文がHTML形式で返るため、テキスト抽出に必須 |
| ネットワーク分析 | networkx | グラフ構造の標準ライブラリ。中心性指標が一通り揃う |
| ネットワーク可視化（プロト） | pyvis | networkx グラフから即座にHTML出力。プロトタイプに最適 |
| コミュニティ検出 | python-louvain | タグの「学習領域」を自動グルーピング |
| 密度ベースクラスタ | hdbscan | K-means と異なりクラスタ数を自動決定。質問のトピッククラスタリングに有効 |
| 意味的類似度 | sentence-transformers | 質問本文の意味的なクラスタリングに。重ければ TF-IDF で代替可 |

### 3.3 別途必要なもの

- **Stack Exchange API キー**: [https://stackapps.com/apps/oauth/register](https://stackapps.com/apps/oauth/register) で登録（無料、即時発行）。キーがあれば 10,000 req/日まで利用可
- **Stack Overflow Developer Survey データ**: [https://insights.stackoverflow.com/survey](https://insights.stackoverflow.com/survey) から最新2〜3年分のCSVをダウンロード
- **NLTK データ**: 初回実行時に `nltk.download('stopwords', 'punkt', 'wordnet')` が必要
- **spacy モデル**: `python -m spacy download en_core_web_sm` で英語小モデルをダウンロード
- **Python バージョン**: 3.11 以上を推奨

### 3.4 Stack Exchange API利用上の留意事項

- レート制限: 認証あり10,000req/日、認証なし300req/日
- 1リクエストで取得可能なアイテム数は最大100件、ページネーション必須
- バックオフ処理: API側から `backoff` パラメータが返る場合があり、その秒数だけ待機する必要がある
- フィルター機能で取得フィールドを絞ると効率的（不要なボディを取得しない設定）
- データ利用は[Stack Exchange Network のクリエイティブコモンズ](https://stackoverflow.com/legal/terms-of-service/public)に基づく。出典明記が必要

---

## 4. 週次マイルストーン

実働13日（中央値）を 3〜4週間に分割。1日3〜4時間想定。

### Week 1（Day 1〜4）: データ取得基盤の構築

**ゴール**: 対象言語（Python・JavaScript・Java・Go）の質問・タグデータが SQLite に格納されている状態

| Day | 主タスク | 成果物 |
|---|---|---|
| 1 | プロジェクト初期化／Stack Exchange API キー取得／GitHubリポジトリ作成／ディレクトリ構造構築／`.gitignore`・`requirements.txt`・`pyproject.toml` 整備／NLTK・spacy データダウンロード | リポジトリの初期コミット |
| 2 | Stack Exchange APIクライアント（`src/api/stackex_client.py`）の実装／レート制限・バックオフ対応／フィルター機能の実装／1言語・100件のテスト取得 | API クライアント＋ユニットテスト |
| 3 | 全対象言語・過去5〜10年分の質問データ一括取得／タグ統計の取得／SQLite キャッシュへの保存／`scripts/fetch_questions.py`・`fetch_tags.py` 完成 | `data/raw/stackex_cache.sqlite`（数百MB想定） |
| 4 | EDA ノートブック（`01_data_exploration.ipynb`）／テキスト前処理（HTML除去、トークナイズ、ストップワード除去）／`02_text_preprocessing.ipynb` で前処理過程を可視化 | `data/processed/questions.parquet` |

**Week 1 の完了判定**:
- 4言語×過去5年分の質問データが parquet で保存されている
- 質問本文がHTML除去・トークナイズ済みの状態でアクセスできる
- 同じスクリプトを再実行しても結果が再現される

---

### Week 2（Day 5〜8）: 3層分析の実装

**ゴール**: マクロ・メゾ・ミクロの3層分析が完成し、フロント用JSONが書き出されている状態

| Day | 主タスク | 成果物 |
|---|---|---|
| 5 | **マクロ分析**: 言語別質問数の時系列推移（`src/analysis/trend.py`、`03_trend_analysis.ipynb`）／Developer Survey との突合 | `data/analysis/trends.parquet` |
| 6 | **メゾ分析**: タグ共起ネットワーク構築（`src/analysis/network.py`、`04_cooccurrence_network.ipynb`）／中心性指標計算／Louvain法によるコミュニティ検出 | 言語別ネットワークJSON |
| 7 | **ミクロ分析**: 質問本文のトピッククラスタリング（`src/analysis/pitfall.py`、`05_pitfall_clustering.ipynb`）／TF-IDF + HDBSCAN／つまづきパターントップ20の抽出 | `data/analysis/pitfalls.parquet` |
| 8 | フロント用JSON生成（`scripts/build_site.py`）／集計・軽量化／ネットワーク図のノード数を見やすい範囲に絞り込み（上位50ノード等） | `web/static/data/*.json` |

**Week 2 の完了判定**:
- 3層の分析結果がそれぞれノートブックでストーリー化されている
- Pyvis で言語別ネットワーク図がHTML生成され、目視で「クラスタが意味のある領域に分かれている」ことを確認
- 「Pythonでつまづくトピックトップ20」のような具体的リストが作成されている

---

### Week 3（Day 9〜12 + 予備2日）: スクロールテリング型フロントエンド

**ゴール**: 一般の閲覧者がスクロールするだけでストーリーが展開されるサイトが公開されている状態

| Day | 主タスク | 成果物 |
|---|---|---|
| 9 | スクロールテリングのHTML骨組み（`web/index.html`）／IntersectionObserver による章切替（`scroll.js`）／第1幕「言語の地殻変動」の折れ線グラフ実装 | 第1幕動作版 |
| 10 | 第2幕「言語別つまづきマップ」／D3.js force-directed graph（`network.js`）／言語タブによるネットワーク差し替え（`language_switch.js`） | ネットワーク図動作版 |
| 11 | 第3幕「Pythonの罠トップ20」（横棒グラフ）／第4幕「学習ロードマップへの示唆」（提言セクション）／文章コンテンツの執筆 | 全章揃った動作版 |
| 12 | スタイリング（`scrollytelling.css`、`responsive.css`）／スマホ対応／`about.html` 作成／README整備／GitHub Pages 公開 | 公開URL |
| 予備 13-14 | バグ修正、パフォーマンスチューニング、解説記事の執筆、LinkedIn投稿準備 | 完成品 |

**Week 3 の完了判定**:
- 公開URLにアクセスしてスクロールするとストーリーが展開する
- D3.js のネットワーク図でノードをドラッグ・ホバーできる
- 言語タブで Python・JS・Go・Java を切り替えられる
- スマホでも縦スクロールで読める

---

## 5. リスクと対策

| リスク | 影響度 | 対策 |
|---|---|---|
| Stack Exchange API のレート制限超過 | 中 | tenacity で自動バックオフ、SQLite キャッシュで再取得防止、夜間バッチで分散取得 |
| データ量が大きく分析が重い | 中 | parquet による列志向ストレージ、必要列のみロード、サンプリングオプションも用意 |
| D3.js の学習コスト | 高 | 既存サンプルコード（[Observable](https://observablehq.com/) 等）から派生する形で実装、自作は最小限に |
| ネットワーク図のノードが多すぎて見づらい | 中 | 中心性指標で上位N個に絞る、コミュニティで色分け、ホバーで詳細表示 |
| 英語テキスト分析の精度 | 中 | sentence-transformers が重ければ TF-IDF に切替、ドメイン固有ストップワードを `stopwords.py` で管理 |
| 13日で終わらない | 中 | 予備2日を Week 3 に確保。最低限の優先順位は「マクロ分析→ネットワーク→スクロール骨組み」 |

---

## 6. 完成の定義（Definition of Done）

公開時点で次の全項目が満たされていること。

- 公開URL（GitHub Pages）が存在し、リンクをクリックして閲覧できる
- スクロールにより最低4章のストーリーが展開する
- D3.js のネットワーク図が動作し、ノードをホバーすると詳細が表示される
- 言語タブで Python・JavaScript・Java・Go の4言語を切り替えられる
- About ページにデータソース（Stack Exchange API、Developer Survey）、手法、CC-BY-SA ライセンス遵守の明記がある
- README に「セットアップ手順・データ取得コマンド・NLTK/spacy モデルダウンロード手順」が書かれている
- リポジトリが Public で、`.env`（APIキー）はコミットされていない
- LinkedIn または個人ポートフォリオから当サイトへのリンクが設置されている

---

## 7. 第1作・第2作からの流用ポイント

| 流用対象 | 活用方法 |
|---|---|
| API クライアントの設計パターン | requests + tenacity + SQLite キャッシュの構造を踏襲（第1・2作と同じ） |
| 環境変数管理 | `.env`、`config/settings.py` の構造を再利用 |
| 可視化基盤 | Plotly のラッパー関数、CSS の基本テーマ（フォント・色） |
| GitHub Pages デプロイ手順 | そのまま再利用 |
| README テンプレート | 構成を踏襲 |
| YAML設定ファイル | 第2作の `category_mapping.yml` のパターンを `target_languages.yml` に応用 |

第1作・第2作で構築した資産により、データ取得とインフラ部分の実装期間を **3〜4割短縮** できる見込み。本作の固有負担は「テキストマイニング」と「D3.js 実装」に集中する。

---

## 8. 次のアクション

着手にあたっての最初の3ステップ。

1. **Stack Exchange API キーの取得**（[https://stackapps.com/apps/oauth/register](https://stackapps.com/apps/oauth/register)、所要15分）
2. **Stack Overflow Developer Survey CSVのダウンロード**（最新2〜3年分）
3. **GitHub リポジトリの作成**（推奨名: `stackoverflow-learner-pitfalls`、Public）

---

*本計画書は実装の進捗に応じて随時更新する。*
