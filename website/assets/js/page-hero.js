/**
 * HAMMEL page HERO video configuration.
 * To replace a video later, put the new MP4 under website/assets/video/
 * and update only the corresponding value below.
 * Paths are relative to the website root (not to the page URL).
 */
(() => {
  "use strict";
  const videos = {
    unternehmen: "assets/video/hammel-hero.mp4",
    maschinen: "assets/video/hammel-hero.mp4",
    loesungen: "assets/video/hammel-hero.mp4",
    weltweit: "assets/video/weltweit-night-earth.mp4",
    service: "assets/video/hammel-hero.mp4",
    karriere: "assets/video/hammel-hero.mp4",
    kontakt: "assets/video/hammel-hero.mp4",
    aktuelles: "assets/video/hammel-hero.mp4",
  };
  const hero = document.querySelector(".hammel-page-hero[data-page]");
  if (!hero) return;
  const source = hero.querySelector("video source");
  if (!source) return;
  const page = hero.dataset.page;
  if (!Object.prototype.hasOwnProperty.call(videos, page)) return;
  const path = videos[page];
  const url = new URL(`../${path}`, document.baseURI);
  if (source.getAttribute("src") !== url.pathname) {
    source.src = url.href;
    const video = hero.querySelector("video");
    if (video) video.load();
  }
})();
