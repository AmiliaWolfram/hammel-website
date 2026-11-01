(() => {
    'use strict';
    // Entries transcribed from HAMMEL's public international directory (October 2026).
    // Coordinates represent the named city/municipality, not independently verified rooftop geocodes.
    const regions = [['all', 'ALLE'], ['e', 'EUROPA'], ['a', 'ASIEN'], ['f', 'AFRIKA'], ['n', 'NORDAMERIKA'], ['s', 'SÜDAMERIKA'], ['o', 'OZEANIEN']];
    let partners = [];
    // Django is the single source of truth. Failed API requests show an empty list.
    const partnerDataReady = fetch('/api/partner/', {credentials:'same-origin'})
        .then(r => {if(!r.ok) throw Error('Partner API'); return r.json()})
        .then(rows => { partners = rows.map((p,id) => ({...p,id})); })
        .catch(error => { console.error("Partnerdaten konnten nicht geladen werden", error); partners = []; });
    partnerDataReady.then(() => {
    const $ = id => document.getElementById(id), svg = $('atlas-viewport')?.querySelector('svg');
    if (!svg)
        return;
    const NS = 'http://www.w3.org/2000/svg', pins = $('partner-map-pins'), routes = $('partner-map-routes');
    const state = { region: 'all', query: '', selected: null, view: [0, 0, 1200, 590] };
    // MapLibre + OpenFreeMap: no CARTO API key, no paid basemap request quota.
    // Provider may change availability/terms. OSM attribution remains mandatory.
    const street = $('atlas-street');
    let streetPartner = null, streetZoom = 1.45, streetMap = null, streetMarker = null;
    const maplibreReady = new Promise((resolve, reject) => {
        const link = document.createElement('link');
        link.rel = 'stylesheet';
        link.href = 'https://unpkg.com/maplibre-gl@4.7.1/dist/maplibre-gl.css';
        document.head.appendChild(link);
        const script = document.createElement('script');
        script.src = 'https://unpkg.com/maplibre-gl@4.7.1/dist/maplibre-gl.js';
        script.onload = () => resolve(window.maplibregl);
        script.onerror = () => reject(Error('MapLibre unavailable'));
        document.head.appendChild(script);
    });
    // Geographic camera presets, independent of partner office locations.
    // Some representatives have offices outside the countries they serve.
    const continentBounds = {
        e: [[-13, 34], [37, 72]],
        a: [[28, -12], [150, 63]],
        f: [[-20, -36], [52, 38]],
        n: [[-170, 7], [-50, 75]],
        s: [[-83, -57], [-32, 14]],
        o: [[108, -48], [180, 0]]
    };
    const idlePartnerMarkup = '<div class="atlas-idle-panel" role="status"><div class="atlas-idle-panel__copy"><span class="atlas-idle-panel__eyebrow">PARTNER AUSWÄHLEN</span><h3>ENTDECKEN SIE UNSERE PARTNER</h3><p>Wählen Sie einen Standort auf der Weltkarte oder ein Unternehmen aus der Partnerliste, um weitere Informationen und Kontaktdaten anzuzeigen.</p><a class="atlas-idle-panel__hint atlas-idle-panel__button cinematic-link" href="#international" aria-label="Zur interaktiven Partnerkarte scrollen"><span class="cinematic-link__icon" aria-hidden="true"><svg viewBox="0 0 24 24"><path d="M5 19 19 5M8 5h11v11"/></svg></span><span class="cinematic-link__label">STANDORT ODER UNTERNEHMEN AUSWÄHLEN</span></a></div></div>';
    function flyToRegion(region) {
        if (!streetMap)
            return;
        const opts = { duration: 1650, essential: true, bearing: 0, pitch: 0 };
        if (region === 'all')
            streetMap.flyTo({ ...opts, center: [12, 19], zoom: 1.45 });
        else if (continentBounds[region])
            streetMap.fitBounds(continentBounds[region], { ...opts, padding: { top: 65, bottom: 65, left: 65, right: 65 }, maxZoom: 5.1 });
    }
    const homeCoordinates = [10.23, 50.81]; // Approximate Bad Salzungen city centre; not a surveyed rooftop location.
    const mapDots = [];
    let pinFeatures = () => [];
    let routeSourceReady = false;
    function networkFeatures() {
        const seen = new Set();
        return partners.filter(p => {
            const k = p.lat.toFixed(3) + ',' + p.lon.toFixed(3);
            if (seen.has(k) || (p.name === 'HAMMEL Recyclingtechnik GmbH' && p.country === 'Deutschland' && Math.abs(p.lat - homeCoordinates[1]) < .001 && Math.abs(p.lon - homeCoordinates[0]) < .001))
                return false;
            seen.add(k);
            return true;
        }).map(p => ({ type: 'Feature', properties: { id: p.id, selected: state.selected === p.id ? 1 : 0 }, geometry: { type: 'LineString', coordinates: (() => {
                    const pts = [];
                    const steps = 44;
                    for (let i = 0; i <= steps; i++) {
                        const t = i / steps;
                        const lon = homeCoordinates[0] + (p.lon - homeCoordinates[0]) * t;
                        const lat = homeCoordinates[1] + (p.lat - homeCoordinates[1]) * t;
                        const arch = Math.sin(Math.PI * t) * Math.min(12, Math.abs(p.lon - homeCoordinates[0]) * .085 + Math.abs(p.lat - homeCoordinates[1]) * .05);
                        pts.push([lon, Math.max(-84, Math.min(84, lat + arch))]);
                    }
                    return pts;
                })() } }));
    }
    function updateNetwork() {
        if (routeSourceReady && streetMap.getSource('hammel-partner-pins')) {
            streetMap.getSource('hammel-partner-pins').setData({ type: 'FeatureCollection', features: pinFeatures() });
        }
        if (routeSourceReady)
            streetMap.getSource('hammel-network')?.setData({ type: 'FeatureCollection', features: networkFeatures() });
    }
    function showStreet(p, zoom = 11.5) {
        streetPartner = p;
        streetZoom = zoom;
        if (!streetMap)
            return;
        streetMap.flyTo({ center: [p.lon, p.lat], zoom: zoom, duration: 1700, essential: true });
    }
    function hideStreet() { streetPartner = null; if (streetMarker) {
        streetMarker.remove();
        streetMarker = null;
    } }
    maplibreReady.then(gl => {
        street.classList.add('is-visible');
        street.setAttribute('aria-hidden', 'false');
        streetMap = new gl.Map({ container: 'atlas-street-map', style: 'https://tiles.openfreemap.org/styles/dark', center: [12, 19], zoom: 1.45, minZoom: 1, maxZoom: 19, renderWorldCopies: false, attributionControl: false });
        streetMap.addControl(new gl.AttributionControl({ compact: true }), 'bottom-right');
        streetMap.on('load', () => {
            streetMap.addSource('hammel-network', { type: 'geojson', data: { type: 'FeatureCollection', features: networkFeatures() } });
            streetMap.addLayer({ id: 'hammel-network-lines', type: 'line', source: 'hammel-network', paint: { 'line-color': ['case', ['==', ['get', 'selected'], 1], '#ef1425', '#a31723'], 'line-width': ['case', ['==', ['get', 'selected'], 1], 2.1, 0.8], 'line-opacity': ['case', ['==', ['get', 'selected'], 1], 0.95, 0.26] } });
            streetMap.addSource('hammel-partner-pins', { type: 'geojson', data: { type: 'FeatureCollection', features: pinFeatures() } });
            streetMap.addLayer({ id: 'hammel-pin-halo', type: 'circle', source: 'hammel-partner-pins', paint: { 'circle-radius': ['case', ['==', ['get', 'home'], 1], 15, ['==', ['get', 'active'], 1], 12, 8], 'circle-color': ['case', ['==', ['get', 'home'], 1], '#F2B705', '#e30613'], 'circle-opacity': ['case', ['==', ['get', 'home'], 1], .28, ['==', ['get', 'active'], 1], .20, .10], 'circle-blur': .65 } });
            streetMap.addLayer({ id: 'hammel-pin-core', type: 'circle', source: 'hammel-partner-pins', paint: { 'circle-radius': ['case', ['==', ['get', 'home'], 1], 6, ['==', ['get', 'active'], 1], 5, 3.8], 'circle-color': ['case', ['==', ['get', 'home'], 1], '#F2B705', '#d74452'], 'circle-stroke-color': ['case', ['==', ['get', 'home'], 1], '#FFF3B0', '#a66a72'], 'circle-stroke-width': ['case', ['==', ['get', 'home'], 1], 2, 1.4], 'circle-opacity': ['case', ['==', ['get', 'dimmed'], 1], .45, 1] } });
            streetMap.on('click', 'hammel-pin-core', e => { const f = e.features?.[0]; if (f)
                select(f.properties.id); });
            streetMap.on('mouseenter', 'hammel-pin-core', () => streetMap.getCanvas().style.cursor = 'pointer');
            streetMap.on('mouseleave', 'hammel-pin-core', () => streetMap.getCanvas().style.cursor = '');
            routeSourceReady = true;
            updateNetwork();
            if (streetPartner)
                showStreet(streetPartner, streetZoom);
            else if (state.region !== 'all')
                flyToRegion(state.region);
        });
        streetMap.on('zoomend', () => { streetZoom = streetMap.getZoom(); });
        const groups = new Map();
        partners.forEach(p => { const key = p.lat.toFixed(3) + ',' + p.lon.toFixed(3); if (!groups.has(key))
            groups.set(key, []); groups.get(key).push(p); });
        pinFeatures = () => Array.from(groups.values()).map(ps => {
            const p = ps[0], home = (p.name === 'HAMMEL Recyclingtechnik GmbH' && p.country === 'Deutschland' && Math.abs(p.lat - homeCoordinates[1]) < .001 && Math.abs(p.lon - homeCoordinates[0]) < .001);
            return { type: 'Feature', properties: { id: home ? (partners.find(q => q.name === 'HAMMEL Recyclingtechnik GmbH' && q.country === 'Deutschland')?.id ?? p.id) : p.id, home: home ? 1 : 0, active: ps.some(q => q.id === state.selected) ? 1 : 0, dimmed: !home && state.selected !== null && !ps.some(q => q.id === state.selected) ? 1 : 0 }, geometry: { type: 'Point', coordinates: [p.lon, p.lat] } };
        });
        updateNetwork();
    }).catch(e => { console.warn('OpenFreeMap requires an internet connection', e); street.classList.remove('is-visible'); });
    const pos = p => ({ x: (p.lon + 180) * 1200 / 360, y: (90 - p.lat) * 590 / 180 });
    const esc = s => String(s || '').replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
    const elem = (tag, attrs) => { let e = document.createElementNS(NS, tag); Object.entries(attrs || {}).forEach(([k, v]) => e.setAttribute(k, v)); return e; };
    const origin = pos({ lat: 50.81, lon: 10.23 });
    const unique = new Map();
    partners.forEach(p => { const k = p.lat.toFixed(2) + '/' + p.lon.toFixed(2); if (!unique.has(k))
        unique.set(k, []); unique.get(k).push(p); });
    unique.forEach((ps, k) => { const p = ps[0], v = pos(p); if (Math.hypot(v.x - origin.x, v.y - origin.y) > 8) {
        let path = elem('path', { d: `M ${origin.x} ${origin.y} Q ${(origin.x + v.x) / 2} ${Math.min(origin.y, v.y) - Math.min(80, Math.abs(v.x - origin.x) * .1)} ${v.x} ${v.y}`, class: 'atlas-route' });
        routes.append(path);
    } const g = elem('g', { class: 'atlas-pin', tabindex: '0', role: 'button', 'aria-label': ps.map(x => x.name + ', ' + x.country).join('; '), transform: `translate(${v.x} ${v.y})` }); g.append(elem('circle', { r: 13, class: 'atlas-pin__halo' }), elem('circle', { r: 4.5, class: 'atlas-pin__core' })); g.addEventListener('click', () => select(ps[0].id)); g.addEventListener('keydown', e => { if (e.key === 'Enter' || e.key === ' ') {
        e.preventDefault();
        select(ps[0].id);
    } }); g.dataset.ids = ps.map(x => x.id).join(','); pins.append(g); });
    // Camera is animated in geographic SVG coordinates, allowing precise close-up zoom.
    const ASPECT = 1200 / 590, MIN_WIDTH = 160;
    let cameraFrame = 0;
    const clampView = (x, y, w) => { w = Math.max(MIN_WIDTH, Math.min(1200, w)); const h = w / ASPECT; return [Math.max(0, Math.min(1200 - w, x)), Math.max(0, Math.min(590 - h, y)), w, h]; };
    const renderView = v => {
        state.view = v;
        svg.setAttribute('viewBox', v.map(n => n.toFixed(4)).join(' '));
        // Markers stay elegant and small while the world artwork zooms.
        const factor = Math.max(.12, Math.min(1, v[2] / 1200));
        pins.querySelectorAll('.atlas-pin').forEach(g => { const core = g.querySelector('.atlas-pin__core'), halo = g.querySelector('.atlas-pin__halo'); if (core)
            core.setAttribute('r', (4.5 * factor).toFixed(3)); if (halo)
            halo.setAttribute('r', (13 * factor).toFixed(3)); });
    };
    const setView = (x, y, w, h, animate = false) => {
        const target = clampView(x, y, w);
        cancelAnimationFrame(cameraFrame);
        if (!animate || window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
            renderView(target);
            return;
        }
        const from = state.view.slice(), start = performance.now(), duration = 950;
        const step = now => {
            let t = Math.min(1, (now - start) / duration), ease = t < .5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2;
            // interpolate the logarithm of zoom for a fluid, cinematic camera movement
            let w = Math.exp(Math.log(from[2]) + (Math.log(target[2]) - Math.log(from[2])) * ease);
            let cx = (from[0] + from[2] / 2) * (1 - ease) + (target[0] + target[2] / 2) * ease;
            let cy = (from[1] + from[3] / 2) * (1 - ease) + (target[1] + target[3] / 2) * ease;
            renderView(clampView(cx - w / 2, cy - w / ASPECT / 2, w));
            if (t < 1)
                cameraFrame = requestAnimationFrame(step);
        };
        cameraFrame = requestAnimationFrame(step);
    };
    const focus = (p, scale = 185) => { const v = pos(p); setView(v.x - scale / 2, v.y - scale / ASPECT / 2, scale, scale / ASPECT, true); };
    function closestToView() { const v = state.view, cx = v[0] + v[2] / 2, cy = v[1] + v[3] / 2; return partners.reduce((best, p) => { const pt = pos(p), d = Math.hypot((pt.x - cx) * .75, pt.y - cy); return !best || d < best.d ? { p, d } : best; }, null)?.p; }
    function transitionToStreets() { const p = state.selected !== null ? partners[state.selected] : closestToView(); if (p) {
        showStreet(p, 12);
    } }
    const available = () => partners.filter(p => (state.region === 'all' || p.region === state.region) && [p.name, p.country, p.city, p.address].join(' ').toLocaleLowerCase('de').includes(state.query));
    function drawList() { const data = available(); $('atlas-count').textContent = data.length + ' PARTNER / VERTRETUNGEN'; $('atlas-partner-list').innerHTML = data.map(p => `<button class="atlas-list-item ${p.id === state.selected ? 'is-selected' : ''}" data-id="${p.id}" type="button"><span class="atlas-list-item__country">${esc(p.country)}</span><strong>${esc(p.name)}</strong><small>${esc(p.city)} <span>↗</span></small></button>`).join('') || '<p class="atlas-empty">Keine Partner gefunden.</p>'; $('atlas-partner-list').querySelectorAll('[data-id]').forEach(b => b.addEventListener('click', () => select(+b.dataset.id))); pins.querySelectorAll('.atlas-pin').forEach(g => { let ids = g.dataset.ids.split(',').map(Number); g.classList.toggle('is-hidden', !ids.some(id => data.some(p => p.id === id))); g.classList.toggle('is-selected', ids.includes(state.selected)); }); }
    function select(id) {
        const p = partners[id];
        if (!p)
            return;
        state.selected = id;
        showStreet(p, 11.5);
        drawList();
        updateNetwork();
        $('atlas-profile-area')?.classList.add('has-selection');
        const url = p.domain ? 'https://' + p.domain : '';
        const regionName = ({ e: 'EUROPA', a: 'ASIEN', f: 'AFRIKA', n: 'NORDAMERIKA', s: 'SÜDAMERIKA', o: 'OZEANIEN' })[p.region] || 'WELTWEIT';
        const content = p;
        const partnerLogo = p.logo || '';
        const verifiedLogo = typeof partnerLogo === 'string' && (/^https:\/\//.test(partnerLogo) || /^\/(?!\/)/.test(partnerLogo));
        const brand = verifiedLogo ? `<div class="atlas-light-logo-box"><img class="atlas-light-logo" src="${esc(partnerLogo)}" alt="Logo ${esc(p.name)}" loading="lazy" onerror="this.closest('.atlas-light-logo-box').remove()"></div>` : '';
        const theme = ['tecmaco', 'hammel', 'inrema'].includes(content.theme) ? content.theme : 'neutral';
        const heroImage = typeof content.heroImage === 'string' && /^https:\/\//.test(content.heroImage) ? content.heroImage : '';
        const officialLogo = typeof content.officialLogo === 'string' && /^https:\/\//.test(content.officialLogo) ? content.officialLogo : '';
        const brandHeader = content.tagline ? `<div class="atlas-brand-hero atlas-brand-hero--${theme}" ${heroImage ? `style="--partner-photo:url('${esc(heroImage)}')"` : ''}><div class="atlas-brand-hero__shade"></div><div class="atlas-brand-hero__body">${officialLogo ? `<img class="atlas-brand-hero__logo" src="${esc(officialLogo)}" alt="${esc(p.name)}" loading="lazy" onerror="this.hidden=true">` : ''}<span class="atlas-brand-hero__overline">HAMMEL PARTNERNETZWERK · ${esc(p.country)}</span><strong>${esc(content.tagline)}</strong><span class="atlas-brand-hero__signature">${esc(p.name)}</span></div></div>` : '';
        const about = typeof content.description === 'string' && content.description.trim() ? `<div class="atlas-company-editorial">${content.eyebrow ? `<span class="atlas-company-eyebrow">${esc(content.eyebrow)}</span>` : ''}<p class="atlas-company-summary">${esc(content.description)}</p></div>` : '';
        $('atlas-details').innerHTML = `<div class="atlas-light-profile atlas-light-profile--${theme}" style="--partner-accent:${/^#[0-9a-fA-F]{6}$/.test(content.brandColor || '') ? content.brandColor : '#e30613'}"><div class="atlas-light-topline"><button id="atlas-close" class="atlas-light-close" aria-label="Profil schließen" type="button">×</button></div>${brandHeader}<div class="atlas-light-main"><div class="atlas-light-identity"><div class="atlas-light-intro"><span class="atlas-light-country">${esc(p.country)}</span><h3>${esc(p.name)}</h3>${about}</div></div><div class="atlas-light-contact">${brand}<div class="atlas-light-field"><span>STANDORT</span><p>${esc(p.address).replace(/\n/g, '<br>')}</p></div>${p.phone ? `<div class="atlas-light-field"><span>TELEFON</span><a href="tel:${esc(p.phone.replace(/[^+\d]/g, ''))}">${esc(p.phone)}</a></div>` : ''}${url ? `<a class="atlas-light-website cinematic-link cinematic-link--section cinematic-link--dark" href="${esc(url)}" target="_blank" rel="noopener noreferrer"><span class="cinematic-link__icon atlas-light-arrow" aria-hidden="true"><svg viewBox="0 0 24 24"><path d="M5 19 19 5M7 5h12v12"/></svg></span><span class="cinematic-link__label">WEBSITE BESUCHEN</span></a>` : ''}</div></div></div>`;
        $('atlas-close').onclick = () => { hideStreet(); state.selected = null; $('atlas-profile-area')?.classList.remove('has-selection'); updateNetwork(); streetMap?.flyTo({ center: [12, 19], zoom: 1.45, duration: 1200 }); $('atlas-details').innerHTML = idlePartnerMarkup; drawList(); };
    }
    $('atlas-regions').innerHTML = regions.map(([id, label]) => `<button type="button" data-region="${id}" class="atlas-region ${id === 'all' ? 'is-active' : ''}">${label}</button>`).join('');
    $('atlas-regions').querySelectorAll('button').forEach(b => b.addEventListener('click', () => { state.region = b.dataset.region; state.selected = null; $('atlas-profile-area')?.classList.remove('has-selection'); hideStreet(); updateNetwork(); flyToRegion(state.region); $('atlas-regions').querySelectorAll('button').forEach(x => x.classList.toggle('is-active', x === b)); drawList(); let ps = available(); if (ps.length) {
        let v = ps.map(pos), minx = Math.min(...v.map(x => x.x)), maxx = Math.max(...v.map(x => x.x)), miny = Math.min(...v.map(x => x.y)), maxy = Math.max(...v.map(x => x.y));
        let w = Math.max(290, (maxx - minx) * 1.45, (maxy - miny) * 2.5);
        setView((minx + maxx - w) / 2, (miny + maxy - w / (1200 / 590)) / 2, w, w / (1200 / 590), true);
    }
    else
        setView(0, 0, 1200, 590, true); $('atlas-map-status').textContent = b.textContent + ' · ' + ps.length + ' PARTNER'; }));
    $('atlas-search').addEventListener('input', e => { state.query = e.target.value.trim().toLocaleLowerCase('de'); drawList(); });
    $('atlas-zoom-in').onclick = () => streetMap?.zoomIn({ duration: 650 });
    $('atlas-zoom-out').onclick = () => streetMap?.zoomOut({ duration: 650 });
    $('atlas-reset').onclick = () => { hideStreet(); state.selected = null; $('atlas-profile-area')?.classList.remove('has-selection'); updateNetwork(); drawList(); streetMap?.flyTo({ center: [12, 19], zoom: 1.45, duration: 1400, essential: true }); $('atlas-map-status').textContent = 'WELTWEIT VERNETZT'; };
    $('cosmic-enter')?.addEventListener('click', () => { $('international')?.scrollIntoView({ behavior: 'smooth', block: 'start' }); });
    drawList();
    });
})();
