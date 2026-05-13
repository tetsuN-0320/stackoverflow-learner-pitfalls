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

  // ─── 第3幕: つまづきパターン横棒グラフ ───────────────────────
  function renderPitfalls(containerId, data, lang = 'python') {
    if (!data || typeof Plotly === 'undefined') return;
    const el = document.getElementById(containerId);
    if (!el) return;

    const clusters = (data[lang] || []).slice(0, 20);
    if (!clusters.length) return;

    // サイズ降順で並んでいるので上位20件をそのまま使う（表示は下から大きい順）
    const labels = clusters.map(c => c.label.split(' / ')[0]);
    const sizes  = clusters.map(c => c.size);
    const rates  = clusters.map(c => Math.round(c.answer_rate * 100));

    const LANG_COLORS = {
      python: '#3776AB', javascript: '#F7DF1E', java: '#ED8B00', go: '#00ADD8',
    };
    const barColor = LANG_COLORS[lang] || '#4f8ef7';

    const traces = [{
      type: 'bar',
      orientation: 'h',
      x: sizes,
      y: labels,
      marker: {
        color: sizes.map((_, i) => i === 0 ? barColor : barColor + 'aa'),
        line: { width: 0 },
      },
      text: rates.map(r => `${r}% 回答`),
      textposition: 'outside',
      textfont: { color: '#8b8fa8', size: 11 },
      hovertemplate: '<b>%{y}</b><br>件数: %{x}<extra></extra>',
    }];

    const layout = Object.assign({}, DARK, {
      title: {
        text: `${lang.charAt(0).toUpperCase() + lang.slice(1)} 学習者のつまづきトップ20`,
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
      margin: { t: 50, b: 50, l: 220, r: 80 },
      height: Math.max(400, clusters.length * 26 + 100),
    });

    Plotly.newPlot(el, traces, layout, PLOTLY_CONFIG);
  }

  // ─── 公開インターフェース ─────────────────────────────────────
  return { loadTrends, loadPitfalls, renderTrend, renderPitfalls };
})();

// ─── DOMContentLoaded: 第1幕チャート初期化 ──────────────────────
document.addEventListener('DOMContentLoaded', async () => {

  // 第1幕: トレンドチャート
  const trendsData = await Charts.loadTrends();
  if (trendsData) {
    Charts.renderTrend('chart-trend', trendsData);
  }

  // トグルボタン（Developer Survey ↔ 回答率トレンド）
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

      // display 変更後にリサイズを通知して Plotly を再描画させる
      window.dispatchEvent(new Event('resize'));
    });
  });

});
