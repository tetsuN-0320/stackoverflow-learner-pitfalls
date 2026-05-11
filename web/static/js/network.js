/**
 * D3.js v7 force-directed graph でタグ共起ネットワークを描画する。
 * データは web/static/data/networks/{lang}.json から動的にロードする。
 *
 * Week 3 Day 10 で本実装。現時点はローダーのみ。
 */

const NetworkChart = (() => {
  const DATA_BASE = 'static/data/networks/';
  let currentLang = 'python';

  async function loadData(lang) {
    const res = await fetch(`${DATA_BASE}${lang}.json`);
    if (!res.ok) throw new Error(`ネットワークデータが見つかりません: ${lang}`);
    return res.json();
  }

  function render(containerId, data) {
    const container = document.getElementById(containerId);
    if (!container || typeof d3 === 'undefined') return;
    container.innerHTML = '';
    // Day 10 で D3.js force-directed graph を実装
  }

  async function switchLanguage(lang) {
    currentLang = lang;
    try {
      const data = await loadData(lang);
      render('chart-network', data);
      render('network-container', data);
    } catch (e) {
      console.warn(e.message);
    }
  }

  return { switchLanguage, loadData, render };
})();
