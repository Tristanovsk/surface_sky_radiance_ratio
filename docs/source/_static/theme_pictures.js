// The README (included in the docs) uses <picture> elements whose dark image
// follows the OS preference (prefers-color-scheme). Make them follow the
// light/dark theme selected in the docs instead.
(function () {
  const QUERY = '(prefers-color-scheme: dark)';

  function update() {
    const dark = document.documentElement.dataset.theme === 'dark';
    document.querySelectorAll('picture source[data-theme-media]').forEach((source) => {
      source.media = dark ? 'all' : 'not all';
    });
  }

  document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('picture source').forEach((source) => {
      if (source.media === QUERY) {
        source.dataset.themeMedia = QUERY;
      }
    });
    update();
    new MutationObserver(update).observe(document.documentElement,
      { attributes: true, attributeFilter: ['data-theme'] });
  });
})();
