/**
 * IntersectionObserver でスクロール位置を監視し、
 * .act 要素が画面に入ったときに .visible クラスを付与してアニメーションを起動する。
 */
(function () {
  const acts = document.querySelectorAll('.act');
  if (!acts.length) return;

  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add('visible');
        }
      });
    },
    { threshold: 0.15 }
  );

  acts.forEach((act) => observer.observe(act));
})();
