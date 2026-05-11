/**
 * Plotly.js を使ってトレンド折れ線グラフとつまづき横棒グラフを描画する。
 * データは web/static/data/trends.json・pitfalls.json から取得する。
 *
 * Week 3 Day 9・11 で本実装。現時点はローダーのみ。
 */

const Charts = (() => {
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

  function renderTrend(containerId, data) {
    if (!data || typeof Plotly === 'undefined') return;
    // Day 9 で Plotly 折れ線グラフを実装
  }

  function renderPitfalls(containerId, data, lang) {
    if (!data || typeof Plotly === 'undefined') return;
    // Day 11 で Plotly 横棒グラフを実装
  }

  return { loadTrends, loadPitfalls, renderTrend, renderPitfalls };
})();
