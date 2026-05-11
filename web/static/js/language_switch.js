/**
 * 言語タブのクリックイベントを処理し、ネットワーク図とチャートを切り替える。
 */
(function () {
  const tabContainers = document.querySelectorAll('.language-tabs');
  if (!tabContainers.length) return;

  tabContainers.forEach((container) => {
    container.addEventListener('click', (e) => {
      const tab = e.target.closest('.tab');
      if (!tab) return;

      const lang = tab.dataset.lang;

      document.querySelectorAll('.tab').forEach((t) => t.classList.remove('active'));
      document.querySelectorAll(`.tab[data-lang="${lang}"]`).forEach((t) =>
        t.classList.add('active')
      );

      if (typeof NetworkChart !== 'undefined') {
        NetworkChart.switchLanguage(lang);
      }
    });
  });
})();
