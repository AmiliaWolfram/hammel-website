/* Public event list. Events are published only by the authenticated server.
   Static preview: events.json. Production: same-origin /api/messen/ endpoint. */
(() => {
  "use strict";
  const root = document.getElementById("messe-list");
  if (!root) return;
  const filters = [...document.querySelectorAll(".messe-filter")];
  const counter = document.querySelector(".messe-count");
  let entries = [];
  let filter = "upcoming";
  const today = new Date().toISOString().slice(0, 10);
  const safeUrl = (value) => {
    if (typeof value !== "string") return null;
    try {
      const url = new URL(value, window.location.href);
      return ["https:", "http:"].includes(url.protocol) ? url.href : null;
    } catch { return null; }
  };
  function render() {
    root.replaceChildren();
    const visible = entries.filter(e => {
      const ended = e.end_date < today;
      return filter === "past" ? ended : !ended;
    }).sort((a,b) => filter === "past"
      ? b.start_date.localeCompare(a.start_date)
      : a.start_date.localeCompare(b.start_date));
    counter.textContent = `${visible.length} ${visible.length === 1 ? "TERMIN" : "TERMINE"}`;
    if (!visible.length) {
      const empty = document.createElement("div");
      empty.className = "messe-empty";
      empty.textContent = filter === "past"
        ? "Derzeit sind keine vergangenen Messetermine veröffentlicht."
        : "Unsere nächsten Messetermine werden in Kürze veröffentlicht.";
      root.append(empty);
      return;
    }
    for (const e of visible) {
      const item = document.createElement("article");
      item.className = "messe-item";
      const date = document.createElement("div");
      date.className = "messe-item__date";
      const fmt = value => new Intl.DateTimeFormat("de-DE", {day:"2-digit",month:"short",year:"numeric",timeZone:"UTC"}).format(new Date(value+"T12:00:00Z"));
      date.textContent = e.start_date === e.end_date ? fmt(e.start_date) : `${fmt(e.start_date)} – ${fmt(e.end_date)}`;
      const info = document.createElement("div");
      const title = document.createElement("h3");
      title.className = "messe-item__title";
      title.textContent = e.title;
      const meta = document.createElement("p");
      meta.className = "messe-item__meta";
      meta.textContent = [e.city, e.country, e.booth ? `STAND ${e.booth}` : ""].filter(Boolean).join(" · ");
      info.append(title,meta);
      if (e.description) {
        const description = document.createElement("p");
        description.className = "messe-item__desc";
        description.textContent = e.description;
        info.append(description);
      }
      if (e.image && typeof e.image === "string" && e.image.startsWith("/media/messen/")) {
        const picture = document.createElement("img");
        picture.className = "messe-item__image";
        picture.src = e.image;
        picture.alt = "";
        picture.loading = "lazy";
        info.append(picture);
      }
      item.append(date,info);
      const href = safeUrl(e.url);
      if (href) {
        const link = document.createElement("a");
        link.className = "messe-item__link";
        link.href = href;
        link.target = "_blank";
        link.rel = "noopener noreferrer";
        link.textContent = "MESSE ENTDECKEN ↗";
        item.append(link);
      }
      root.append(item);
    }
  }
  filters.forEach(button => button.addEventListener("click", () => {
    filter = button.dataset.filter;
    filters.forEach(b => {
      const active = b === button;
      b.classList.toggle("is-active", active);
      b.setAttribute("aria-pressed", String(active));
    });
    render();
  }));
  async function load() {
    try {
      const response = await fetch('/api/messen/', {credentials:'same-origin'});
      if (!response.ok) throw new Error('Messen API unavailable');
      const data = await response.json();
      if (!Array.isArray(data)) throw new Error('Invalid Messen API response');
      entries = data.filter(e => e && typeof e.title === 'string' &&
        /^\d{4}-\d{2}-\d{2}$/.test(e.start_date) &&
        /^\d{4}-\d{2}-\d{2}$/.test(e.end_date));
    } catch (error) {
      console.error('Messetermine konnten nicht geladen werden', error);
      entries = [];
    }
    render();
  }
  load();
})();
