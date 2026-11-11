/* HAMMEL: native, uninterrupted navigation.
   Do not intercept clicks or create curtains. Unsupported browsers navigate
   instantly; no visible artificial transition is preferable to a loading flash. */
(() => {
  document.documentElement.classList.remove('ht-nav-leaving','ht-nav-entering');
  try { sessionStorage.removeItem('ht-nav-subtle'); sessionStorage.removeItem('ht-navigation'); } catch (_) {}
})();
