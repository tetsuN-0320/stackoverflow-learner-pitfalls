/**
 * network.js — D3.js v7 force-directed graph でタグ共起ネットワークを描画する。
 *
 * Day 10: 本実装
 *   - コミュニティ別の色分け（Louvain 法の結果）
 *   - ノード半径 = 質問数（frequency）の平方根に比例
 *   - リンク太さ = 共起回数（weight）に比例
 *   - ホバー: ツールチップ表示 + 隣接ノードのみ強調
 *   - ドラッグ: 個別ノードを移動可能
 *   - ズーム/パン: SVG 全体をスクロールで拡大縮小
 */

const NetworkChart = (() => {

  const DATA_BASE = 'static/data/networks/';

  // コミュニティ配色（ダークテーマ対応。最大 6 コミュニティ分）
  const COMM_COLORS = [
    '#4f8ef7',  // blue   — コミュニティ 0
    '#f97316',  // orange — コミュニティ 1
    '#22c55e',  // green  — コミュニティ 2
    '#a855f7',  // purple — コミュニティ 3
    '#ef4444',  // red    — コミュニティ 4
    '#14b8a6',  // teal   — コミュニティ 5
  ];

  // 言語ごとのコミュニティ和名ラベル（見やすいツールチップ用）
  const COMM_LABELS = {
    python: ['コア/汎用', 'Web スクレイピング', 'データ分析', 'pandas/CSV', 'ML/数値計算', 'その他'],
    javascript: ['コア/汎用', 'フロントエンド', 'Node.js', 'UI フレームワーク', 'データ可視化', 'その他'],
    java: ['コア/汎用', 'Android', 'Spring/Web', 'デスクトップ', 'その他', 'その他'],
    go:   ['コア/汎用', 'HTTP/ネット', 'データ処理', 'ツール/CLI', 'クラウド', 'データベース'],
  };

  let simulation = null;
  let currentLang = 'python';
  let tooltip = null;

  // ─── データローダー ───────────────────────────────────────────
  async function loadData(lang) {
    const res = await fetch(`${DATA_BASE}${lang}.json`);
    if (!res.ok) throw new Error(`ネットワークデータが見つかりません: ${lang}`);
    return res.json();
  }

  // ─── メイン描画関数 ───────────────────────────────────────────
  function render(containerId, data, lang) {
    const container = document.getElementById(containerId);
    if (!container || typeof d3 === 'undefined') return;

    // 前のシミュレーションを停止し、コンテナをクリア
    if (simulation) { simulation.stop(); simulation = null; }
    container.innerHTML = '';

    const width  = container.clientWidth  || 750;
    const height = Math.max(container.clientHeight || 500, 480);

    // ─ スケール定義 ─
    const maxFreq = d3.max(data.nodes, d => d.frequency);
    const rScale = d3.scaleSqrt()
      .domain([1, maxFreq])
      .range([5, 30])
      .clamp(true);

    const maxWeight = d3.max(data.links, d => d.weight) || 1;
    const strokeW = d3.scaleLinear()
      .domain([1, maxWeight])
      .range([0.5, 4]);

    const allComms = [...new Set(data.nodes.map(d => d.community))].sort();
    const colorScale = d3.scaleOrdinal()
      .domain(allComms)
      .range(COMM_COLORS);

    // ─ ツールチップ（body 直下に1個だけ） ─
    tooltip = d3.select('body')
      .selectAll('.network-tooltip')
      .data([0])
      .join('div')
      .attr('class', 'network-tooltip')
      .style('display', 'none');

    // ─ ノード・リンクのディープコピー（シミュレーションが書き換えるため） ─
    const nodes = data.nodes.map(d => ({ ...d }));
    const links = data.links.map(d => ({ ...d }));

    // ─ SVG 構築 ─
    const svg = d3.select(container)
      .append('svg')
      .attr('width', '100%')
      .attr('height', height)
      .style('display', 'block')
      .style('overflow', 'hidden');

    // ズーム/パン
    const g = svg.append('g');
    svg.call(
      d3.zoom()
        .scaleExtent([0.2, 6])
        .on('zoom', event => g.attr('transform', event.transform))
    );

    // ─ リンク ─
    const linkEl = g.append('g').attr('class', 'links')
      .selectAll('line')
      .data(links)
      .join('line')
      .attr('stroke', '#2a2d3e')
      .attr('stroke-width', d => strokeW(d.weight))
      .attr('stroke-opacity', 0.55);

    // ─ ノードグループ ─
    const nodeEl = g.append('g').attr('class', 'nodes')
      .selectAll('g')
      .data(nodes)
      .join('g')
      .attr('class', 'node-g')
      .style('cursor', 'grab');

    nodeEl.append('circle')
      .attr('r', d => rScale(d.frequency))
      .attr('fill', d => colorScale(d.community))
      .attr('fill-opacity', 0.85)
      .attr('stroke', '#0f1117')
      .attr('stroke-width', 1.5);

    // ラベル（半径 9px 以上のノードのみ表示）
    nodeEl.append('text')
      .text(d => d.id)
      .attr('font-size', d => Math.min(11, Math.max(7, rScale(d.frequency) * 0.62)))
      .attr('text-anchor', 'middle')
      .attr('dy', '0.35em')
      .attr('fill', '#e8eaf0')
      .attr('fill-opacity', d => rScale(d.frequency) >= 9 ? 0.95 : 0)
      .attr('pointer-events', 'none');

    // ─ Force シミュレーション ─
    simulation = d3.forceSimulation(nodes)
      .force('link',
        d3.forceLink(links)
          .id(d => d.id)
          .distance(d => Math.max(55, 90 - d.weight * 1.5))
          .strength(0.45)
      )
      .force('charge',
        d3.forceManyBody()
          .strength(-160)
          .distanceMax(350)
      )
      .force('center', d3.forceCenter(width / 2, height / 2))
      .force('collide',
        d3.forceCollide().radius(d => rScale(d.frequency) + 5)
      );

    simulation.on('tick', () => {
      linkEl
        .attr('x1', d => d.source.x).attr('y1', d => d.source.y)
        .attr('x2', d => d.target.x).attr('y2', d => d.target.y);
      nodeEl.attr('transform', d => `translate(${d.x},${d.y})`);
    });

    // ─ ドラッグ ─
    nodeEl.call(
      d3.drag()
        .on('start', (event, d) => {
          if (!event.active) simulation.alphaTarget(0.3).restart();
          d.fx = d.x; d.fy = d.y;
        })
        .on('drag', (event, d) => { d.fx = event.x; d.fy = event.y; })
        .on('end', (event, d) => {
          if (!event.active) simulation.alphaTarget(0);
          d.fx = null; d.fy = null;
        })
    );

    // ─ ホバー: 隣接ノード強調 ─
    nodeEl
      .on('mouseover', (event, d) => {
        const commLabel = (COMM_LABELS[lang] || [])[d.community] || `コミュニティ ${d.community}`;
        tooltip
          .style('display', 'block')
          .html(
            `<strong>#${d.id}</strong>` +
            `質問数: <b>${d.frequency.toLocaleString()}</b><br>` +
            `媒介中心性: ${d.betweenness_centrality.toFixed(3)}<br>` +
            `グループ: ${commLabel}`
          );

        // 隣接ノードIDを収集（シミュレーション後は source/target がオブジェクト参照）
        const neighborIds = new Set();
        links.forEach(l => {
          const sid = (l.source.id !== undefined) ? l.source.id : l.source;
          const tid = (l.target.id !== undefined) ? l.target.id : l.target;
          if (sid === d.id) neighborIds.add(tid);
          if (tid === d.id) neighborIds.add(sid);
        });

        nodeEl.select('circle')
          .attr('fill-opacity', n => (n.id === d.id || neighborIds.has(n.id)) ? 1 : 0.08);
        nodeEl.select('text')
          .attr('fill-opacity', n => (n.id === d.id || neighborIds.has(n.id)) ? 1 : 0);
        linkEl.attr('stroke-opacity', l => {
          const sid = (l.source.id !== undefined) ? l.source.id : l.source;
          const tid = (l.target.id !== undefined) ? l.target.id : l.target;
          return (sid === d.id || tid === d.id) ? 0.9 : 0.04;
        });
      })
      .on('mousemove', event => {
        tooltip
          .style('left', (event.pageX + 14) + 'px')
          .style('top',  (event.pageY - 40) + 'px');
      })
      .on('mouseout', () => {
        tooltip.style('display', 'none');
        nodeEl.select('circle').attr('fill-opacity', 0.85);
        nodeEl.select('text').attr('fill-opacity',
          d => rScale(d.frequency) >= 9 ? 0.95 : 0);
        linkEl.attr('stroke-opacity', 0.55);
      });

    // ─ コミュニティ凡例 ─
    _renderLegend(container, allComms, colorScale, lang);
  }

  // ─── 凡例 HTML を描画 ────────────────────────────────────────
  function _renderLegend(container, comms, colorScale, lang) {
    const labels = COMM_LABELS[lang] || [];
    const legendDiv = document.createElement('div');
    legendDiv.className = 'network-legend';
    comms.forEach(c => {
      const item = document.createElement('div');
      item.className = 'legend-item';
      item.innerHTML =
        `<span class="legend-dot" style="background:${colorScale(c)}"></span>` +
        `<span>${labels[c] || 'コミュニティ ' + c}</span>`;
      legendDiv.appendChild(item);
    });
    container.appendChild(legendDiv);
  }

  // ─── 言語切替 ─────────────────────────────────────────────────
  async function switchLanguage(lang) {
    currentLang = lang;
    try {
      const data = await loadData(lang);
      // index.html の act2 と network.html の両方に描画
      ['chart-network', 'network-container'].forEach(id => {
        if (document.getElementById(id)) render(id, data, lang);
      });
    } catch (e) {
      console.warn(e.message);
    }
  }

  // ─── 公開インターフェース ─────────────────────────────────────
  return { switchLanguage, loadData, render };
})();

// ─── DOMContentLoaded: デフォルト言語（Python）でネットワーク初期化 ──
document.addEventListener('DOMContentLoaded', () => {
  NetworkChart.switchLanguage('python');
});
