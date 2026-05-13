/**
 * charts.js — Plotly.js を使ってトレンド折れ線グラフとつまづき横棒グラフを描画する。
 *
 * Day 9: renderTrend (第1幕) 実装
 * Day 11: renderPitfalls (第3幕) 実装
 */

const Charts = (() => {

  // ─── Plotly 共通ダークテーマ ─────────────────────────────────
  const DARK = {
    paper_bgcolor: '#0f1117',
    plot_bgcolor:  '#1a1d27',
    font: {
      color: '#e8eaf0',
      family: '"Noto Sans JP", "Helvetica Neue", Arial, sans-serif',
      size: 12,
    },
    xaxis: {
      gridcolor: '#2a2d3e',
      linecolor: '#2a2d3e',
      tickcolor: '#2a2d3e',
      zerolinecolor: '#2a2d3e',
    },
    yaxis: {
      gridcolor: '#2a2d3e',
      linecolor: '#2a2d3e',
      tickcolor: '#2a2d3e',
      zerolinecolor: '#2a2d3e',
    },
    legend: {
      bgcolor: 'rgba(26,29,39,0.8)',
      bordercolor: '#2a2d3e',
      borderwidth: 1,
    },
    margin: { t: 50, b: 50, l: 55, r: 20 },
    hovermode: 'x unified',
    hoverlabel: {
      bgcolor: '#1a1d27',
      bordercolor: '#4f8ef7',
      font: { color: '#e8eaf0' },
    },
  };

  const PLOTLY_CONFIG = {
    responsive: true,
    displayModeBar: false,
    locale: 'ja',
  };

  // ─── データローダー ───────────────────────────────────────────
  async function loadTrends() {
    const res = await fetch('static/data/trends.json');
    if (!res.ok) return null;
    return res.json();
  }

  async function loadPitfalls() {
    const res = await fetch('static/data/pitfalls.json');
    if (!res.ok) return null;
    return res.json();
  }

  // ─── 第1幕: Developer Survey 使用率チャート ──────────────────
  function renderSurveyChart(elId, data) {
    const el = document.getElementById(elId);
    if (!el || !data) return;

    const langs = Object.keys(data.languages);

    // usage_pct: 実線、want_pct: 破線（同色）
    const traces = [];
    langs.forEach(lang => {
      const info = data.languages[lang];
      const color = info.color;

      traces.push({
        x: data.survey_years,
        y: info.survey.usage_pct,
        mode: 'lines+markers',
        name: info.display_name,
        legendgroup: lang,
        line: { color, width: 2.5 },
        marker: { size: 8, color },
        hovertemplate: `%{y:.1f}%<extra>${info.display_name} 使用率</extra>`,
      });

      traces.push({
        x: data.survey_years,
        y: info.survey.want_pct,
        mode: 'lines+markers',
        name: `${info.display_name} (希望)`,
        legendgroup: lang,
        showlegend: false,
        line: { color, width: 1.5, dash: 'dot' },
        marker: { size: 5, color },
        opacity: 0.6,
        hovertemplate: `%{y:.1f}%<extra>${info.display_name} 希望率</extra>`,
      });
    });

    const layout = Object.assign({}, DARK, {
      title: {
        text: 'Developer Survey: 言語使用率の推移（実線=使用率 / 点線=習得希望率）',
        font: { size: 13, color: '#8b8fa8' },
        x: 0.02,
        xanchor: 'left',
      },
      xaxis: Object.assign({}, DARK.xaxis, {
        tickvals: data.survey_years,
        ticktext: data.survey_years.map(String),
        dtick: 1,
      }),
      yaxis: Object.assign({}, DARK.yaxis, {
        title: { text: '割合（%）', standoff: 10 },
        ticksuffix: '%',
        range: [0, 75],
      }),
    });

    Plotly.newPlot(el, traces, layout, PLOTLY_CONFIG);
  }

  // ─── 第1幕: 回答率 10年推移チャート ─────────────────────────
  function renderComplexityChart(elId, data) {
    const el = document.getElementById(elId);
    if (!el || !data) return;

    const langs = Object.keys(data.languages);

    const traces = langs.map(lang => {
      const info = data.languages[lang];
      return {
        x: data.years,
        y: info.yearly.answer_rate.map(v => v !== null ? Math.round(v * 100) : null),
        mode: 'lines+markers',
        name: info.display_name,
        line: { color: info.color, width: 2.5 },
        marker: { size: 6, color: info.color },
        connectgaps: false,
        hovertemplate: `%{y}%<extra>${info.display_name}</extra>`,
      };
    });

    const layout = Object.assign({}, DARK, {
      title: {
        text: '質問の回答率 10年推移 — 年々難化する技術的問い',
        font: { size: 13, color: '#8b8fa8' },
        x: 0.02,
        xanchor: 'left',
      },
      xaxis: Object.assign({}, DARK.xaxis, {
        tickvals: data.years,
        ticktext: data.years.map(String),
        dtick: 1,
      }),
      yaxis: Object.assign({}, DARK.yaxis, {
        title: { text: '回答率（%）', standoff: 10 },
        ticksuffix: '%',
        range: [30, 100],
      }),
      annotations: [{
        x: data.years[data.years.length - 1],
        y: 62,
        text: '年々下降 →<br>質問の難度が上昇',
        showarrow: false,
        xanchor: 'right',
        font: { color: '#8b8fa8', size: 11 },
        align: 'right',
      }],
    });

    Plotly.newPlot(el, traces, layout, PLOTLY_CONFIG);
  }

  // ─── 第1幕エントリーポイント ─────────────────────────────────
  function renderTrend(containerId, data) {
    if (!data || typeof Plotly === 'undefined') return;
    renderSurveyChart('chart-survey-el', data);
    renderComplexityChart('chart-complexity-el', data);
  }

  // ─── ラベル整形ヘルパー ──────────────────────────────────────
  const LABEL_MAP = {
    django: 'Django', flask: 'Flask', numpy: 'NumPy', pandas: 'pandas',
    tensorflow: 'TensorFlow', keras: 'Keras', selenium: 'Selenium',
    tkinter: 'tkinter (GUI)', sqlalchemy: 'SQLAlchemy',
    python_3: 'Python 3 / ファイル操作', pip: 'pip / 環境構築',
    reactjs: 'React.js', ecmascript_6: 'ES6 / モジュール',
    html: 'HTML / DOM', node: 'Node.js / Express', css: 'CSS / スタイル',
    jquery: 'jQuery', angularjs: 'Angular', vue: 'Vue.js',
    android: 'Android', spring: 'Spring / Boot', swing: 'Swing (GUI)',
    maven: 'Maven / ビルド', javafx: 'JavaFX', firebase: 'Firebase',
    apache: 'Apache Spark / Kafka', multithreading: 'マルチスレッド',
    goroutine: 'goroutine / 並行処理', http: 'HTTP / ネットワーク',
    json: 'JSON / シリアライズ', slice: 'スライス / ループ',
    template: 'HTML テンプレート', mongodb: 'MongoDB', go_gorm: 'GORM (ORM)',
    docker: 'Docker / コンテナ', struct: '構造体 (struct)',
  };

  function _cleanLabel(raw) {
    const first = raw.split(' / ')[0].trim().toLowerCase();
    if (LABEL_MAP[first]) return LABEL_MAP[first];
    return first.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase());
  }

  // ─── 第3幕: つまづきパターン横棒グラフ ───────────────────────
  function renderPitfalls(containerId, data, lang = 'python') {
    if (!data || typeof Plotly === 'undefined') return;
    const el = document.getElementById(containerId);
    if (!el) return;

    // 降順ソート済みデータを取得し、Plotly の下→上描画に合わせて逆順にする
    const clusters = (data[lang] || []).slice(0, 15).reverse();
    if (!clusters.length) return;

    const LANG_COLORS = {
      python: '#3776AB', javascript: '#F7DF1E', java: '#ED8B00', go: '#00ADD8',
    };
    const baseColor = LANG_COLORS[lang] || '#4f8ef7';

    // 回答率が低いほど不透明（暗く）= 解決困難を視覚化
    const labels   = clusters.map(c => _cleanLabel(c.label));
    const sizes    = clusters.map(c => c.size);
    const rates    = clusters.map(c => c.answer_rate);
    // 回答率の逆数でアルファ値を計算（低回答率ほど色が濃い）
    const alphas   = rates.map(r => 0.45 + (1 - r) * 0.55);
    const colors   = alphas.map(a => {
      const hex = Math.round(a * 255).toString(16).padStart(2, '0');
      return baseColor + hex;
    });

    const traces = [{
      type: 'bar',
      orientation: 'h',
      x: sizes,
      y: labels,
      marker: { color: colors, line: { width: 0 } },
      text: rates.map(r => `回答率 ${Math.round(r * 100)}%`),
      textposition: 'outside',
      textfont: { color: '#8b8fa8', size: 10 },
      hovertemplate:
        '<b>%{y}</b><br>' +
        '質問数: %{x}件<br>' +
        '%{text}<extra></extra>',
    }];

    const LANG_NAMES = {
      python: 'Python', javascript: 'JavaScript', java: 'Java', go: 'Go',
    };

    const layout = Object.assign({}, DARK, {
      title: {
        text: `${LANG_NAMES[lang] || lang} 学習者のつまづきトップ ${clusters.length}`,
        font: { size: 13, color: '#8b8fa8' },
        x: 0.02,
        xanchor: 'left',
      },
      xaxis: Object.assign({}, DARK.xaxis, {
        title: { text: '質問数（クラスタサイズ）' },
      }),
      yaxis: Object.assign({}, DARK.yaxis, {
        automargin: true,
        tickfont: { size: 11 },
      }),
      margin: { t: 50, b: 60, l: 200, r: 100 },
      height: Math.max(420, clusters.length * 28 + 120),
      annotations: [{
        x: 0.99, y: -0.12,
        xref: 'paper', yref: 'paper',
        text: '棒の濃さ = 回答率の低さ（濃いほど解決困難）',
        showarrow: false,
        xanchor: 'right',
        font: { color: '#8b8fa8', size: 10 },
      }],
    });

    Plotly.newPlot(el, traces, layout, PLOTLY_CONFIG);

    // サマリー更新
    _updatePitfallSummary(lang, clusters);
  }

  function _updatePitfallSummary(lang, clusters) {
    const el = document.getElementById('pitfall-summary');
    if (!el || !clusters.length) return;
    const top = clusters[0];
    const hardest = [...clusters].sort((a, b) => a.answer_rate - b.answer_rate)[0];
    el.innerHTML =
      `<p class="summary-line">最多: <strong>${_cleanLabel(top.label)}</strong>（${top.size}件）</p>` +
      `<p class="summary-line">最難: <strong>${_cleanLabel(hardest.label)}</strong>` +
      `（回答率 ${Math.round(hardest.answer_rate * 100)}%）</p>`;
  }

  // ─── 公開インターフェース ─────────────────────────────────────
  return { loadTrends, loadPitfalls, renderTrend, renderPitfalls };
})();

// ─── DOMContentLoaded: 各幕チャート初期化 ───────────────────────
document.addEventListener('DOMContentLoaded', async () => {

  // 第1幕: トレンドチャート
  const trendsData = await Charts.loadTrends();
  if (trendsData) {
    Charts.renderTrend('chart-trend', trendsData);
  }

  // 第1幕: トグルボタン（Developer Survey ↔ 回答率トレンド）
  const toggleBtns = document.querySelectorAll('#trend-toggle .toggle-btn');
  toggleBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      toggleBtns.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      const view = btn.dataset.view;
      document.getElementById('chart-survey-el').style.display =
        view === 'survey' ? 'block' : 'none';
      document.getElementById('chart-complexity-el').style.display =
        view === 'complexity' ? 'block' : 'none';
      window.dispatchEvent(new Event('resize'));
    });
  });

  // 第3幕: つまづきランキング（初期 Python）
  const pitfallsData = await Charts.loadPitfalls();
  if (pitfallsData) {
    Charts.renderPitfalls('chart-pitfalls-el', pitfallsData, 'python');

    // 言語タブ切替
    document.querySelectorAll('#pitfall-tabs .tab').forEach(tab => {
      tab.addEventListener('click', () => {
        document.querySelectorAll('#pitfall-tabs .tab')
          .forEach(t => t.classList.remove('active'));
        tab.classList.add('active');
        Charts.renderPitfalls('chart-pitfalls-el', pitfallsData, tab.dataset.lang);
      });
    });
  }

});
