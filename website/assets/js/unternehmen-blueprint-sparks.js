(() => {
    'use strict';
    const NS = 'http://www.w3.org/2000/svg';
    const clamp = x => Math.max(0, Math.min(1, x));
    const el = (tag, attrs = {}) => { const n = document.createElementNS(NS, tag); for (const [k, v] of Object.entries(attrs))
        n.setAttribute(k, v); return n; };
    /* Illustrative outlines based on HAMMEL story imagery, not dimensional CAD drawings. */
    const designs = {
        workshop: { label: '1996 / WERKSTATT', lines: ['M 82 295 V 148 L 305 82 L 545 146 V 295', 'M 108 295 V 162 L 305 106 L 520 162 V 295', 'M 82 148 H 545', 'M 155 295 V 197 H 254 V 295', 'M 332 295 V 192 H 455 V 295', 'M 352 214 H 435', 'M 395 192 V 295', 'M 82 295 H 545'], tracks: ['M 82 295 V 148 L 305 82 L 545 146', 'M 108 295 V 162 L 305 106 L 520 162'] },
        bridge: { label: 'BRUECKE / BAD SALZUNGEN', lines: ['M 44 315 H 596', 'M 90 315 V 188 H 192 V 315', 'M 455 315 V 130 H 557 V 315', 'M 192 245 H 455', 'M 192 264 H 455', 'M 193 245 Q 322 10 455 245', 'M 202 245 Q 322 40 446 245', 'M 225 245 V 206', 'M 262 245 V 157', 'M 302 245 V 138', 'M 342 245 V 142', 'M 382 245 V 162', 'M 420 245 V 204', 'M 105 220 H 177', 'M 470 172 H 542'], tracks: ['M 193 245 Q 322 10 455 245', 'M 192 245 H 455', 'M 455 245 V 130 H 557'] },
        vb750: { label: 'VB 750 / ZWEIWELLENZERKLEINERER', lines: ['M 74 265 H 470 L 505 242 H 560 V 315 H 74 Z', 'M 95 195 H 435 L 470 265', 'M 110 195 V 155 H 408 V 195', 'M 125 155 L 152 128 H 385 L 408 155', 'M 140 265 H 420', 'M 155 287 H 450', 'M 455 265 L 540 190 L 568 204', 'M 540 190 L 586 144', 'M 470 315 H 560', 'M 130 315 H 450', 'M 74 315 H 470'], tracks: ['M 125 155 L 152 128 H 385 L 408 155 L 470 265', 'M 455 265 L 540 190 L 586 144', 'M 74 315 H 470 L 505 242'] },
        twin: { label: 'ZWEI-WELLEN / TECHNIK', lines: ['M 105 115 H 535 V 305 H 105 Z', 'M 140 145 H 500 V 275 H 140 Z', 'M 160 210 H 480', 'M 160 245 H 480', 'M 105 305 H 535', 'M 165 115 V 88 H 475 V 115', 'M 535 185 H 585 V 265 H 535'], circles: [[255, 210, 52], [385, 210, 52], [255, 210, 22], [385, 210, 22]], tracks: ['M 105 115 H 535 V 305 H 105', 'M 140 145 H 500 V 275 H 140', 'M 165 115 V 88 H 475'] },
        metal: { label: 'METALLAUFBEREITUNG / ANLAGE', lines: ['M 40 305 H 610', 'M 95 280 H 340 V 305 H 95 Z', 'M 115 240 H 310 V 280 H 115 Z', 'M 275 240 L 480 115 L 497 132 L 310 270', 'M 480 115 L 560 82 L 570 101 L 497 132', 'M 337 260 L 472 170', 'M 365 275 H 535 V 305 H 365 Z', 'M 415 305 V 220', 'M 520 305 V 176', 'M 55 305 L 90 280'], tracks: ['M 115 240 H 310 L 480 115 L 560 82', 'M 275 240 L 480 115 L 497 132 L 310 270', 'M 40 305 H 610'] },
        giant: { label: 'RED GIANT / VB 950 DK', lines: ['M 65 250 H 465 L 505 225 H 585 V 315 H 65 Z', 'M 80 180 H 455 V 250 H 80 Z', 'M 105 180 V 135 H 418 V 180', 'M 118 135 L 143 105 H 395 L 418 135', 'M 80 270 H 465', 'M 105 315 H 465', 'M 465 250 L 548 165 L 585 183', 'M 548 165 L 610 100', 'M 500 315 H 585'], tracks: ['M 118 135 L 143 105 H 395 L 418 135 L 455 250', 'M 465 250 L 548 165 L 610 100', 'M 65 315 H 465 L 505 225'] },
        office: { label: 'HAMMEL / STANDORT', lines: ['M 35 315 H 605', 'M 60 315 V 182 H 205 V 315', 'M 435 315 V 100 H 592 V 315', 'M 205 235 H 435', 'M 205 257 H 435', 'M 205 235 Q 320 25 435 235', 'M 215 235 Q 320 55 425 235', 'M 235 235 V 195', 'M 265 235 V 150', 'M 300 235 V 128', 'M 335 235 V 128', 'M 375 235 V 155', 'M 410 235 V 195', 'M 462 140 H 570', 'M 462 182 H 570', 'M 462 224 H 570', 'M 85 218 H 175', 'M 85 263 H 175'], tracks: ['M 205 235 Q 320 25 435 235', 'M 205 235 H 435', 'M 435 235 V 100 H 592'] }
    };
    function create(item, design) {
        const svg = el('svg', { class: 'story__schematic', viewBox: '0 0 640 420', preserveAspectRatio: 'xMidYMid meet', 'aria-hidden': 'true' });
        for (const d of design.lines)
            svg.append(el('path', { d, class: 'schematic__geometry' }));
        for (const [x, y, r] of design.circles || [])
            svg.append(el('circle', { cx: x, cy: y, r, class: 'schematic__geometry' }));
        for (const d of ['M 40 58 H 600', 'M 40 52 V 65', 'M 600 52 V 65', 'M 36 80 V 340', 'M 31 80 H 43', 'M 31 340 H 43'])
            svg.append(el('path', { d, class: 'schematic__dimension' }));
        const text = el('text', { x: 48, y: 48, class: 'schematic__label' });
        text.textContent = design.label;
        svg.append(text);
        const sparks = [];
        design.tracks.forEach((d, i) => { const path = el('path', { d, class: 'schematic__spark' }), core = el('circle', { r: '2.8', class: 'schematic__core' }), glint = el('path', { d: 'M -5 0 H 5 M 0 -5 V 5', class: 'schematic__glint' }); svg.append(path, core, glint); sparks.push({ path, core, glint, phase: i * .24 }); });
        item.append(svg);
        for (const sp of sparks) {
            sp.length = sp.path.getTotalLength();
            sp.path.style.strokeDasharray = `13 ${sp.length + 30}`;
        }
        return { svg, sparks };
    }
    function init() {
        const root = document.querySelector('.story');
        if (!root || matchMedia('(prefers-reduced-motion: reduce)').matches)
            return;
        const items = [];
        const kinds = ['workshop', 'bridge', 'vb750', 'twin', 'metal', 'giant'];
        root.querySelectorAll('.story__chapter').forEach((section, index) => { if (section.querySelector('.story__association-grid'))
            return; const art = section.querySelector('.story__art'); if (!art)
            return; const design = designs[kinds[index] || 'twin']; items.push({ section, ...create(art, design) }); });
        const end = root.querySelector('.story__end');
        if (end) {
            const art = end.querySelector('.story__wrap>div:last-child');
            if (art) {
                art.style.position = 'relative';
                art.style.isolation = 'isolate';
                items.push({ section: end, ...create(art, designs.office) });
            }
        }
        let scheduled = false;
        function paint() {
            scheduled = false;
            const vh = innerHeight || 800;
            for (const item of items) {
                const r = item.section.getBoundingClientRect();
                const center = r.top + r.height * .5;
                // visible during approach, fully gone once the chapter reaches viewport midpoint
                /* The position of the chapter, not the scroll direction, determines the frame.
                   Scrolling upwards therefore reverses the exact same animation. The artwork
                   fades out at the viewport midpoint and returns on reverse scroll. */
                const entry = clamp((vh * .96 - center) / (vh * .44));
                const fade = clamp((center - vh * .51) / (vh * .24));
                const opacity = Math.min(clamp(entry * 1.8), fade);
                item.svg.style.opacity = String(opacity * .92);
                const t = clamp(entry);
                for (const s of item.sparks) {
                    const p = clamp(t * .88 + s.phase * .10);
                    s.path.style.strokeDashoffset = String(-p * s.length);
                    const pt = s.path.getPointAtLength(p * s.length);
                    s.core.setAttribute('cx', pt.x);
                    s.core.setAttribute('cy', pt.y);
                    s.glint.setAttribute('transform', `translate(${pt.x} ${pt.y})`);
                    s.core.style.opacity = String(opacity);
                    s.glint.style.opacity = String(opacity);
                }
            }
        }
        function request() { if (!scheduled) {
            scheduled = true;
            requestAnimationFrame(paint);
        } }
        addEventListener('scroll', request, { passive: true });
        addEventListener('resize', request, { passive: true });
        paint();
    }
    if (document.readyState === 'loading')
        document.addEventListener('DOMContentLoaded', init, { once: true });
    else
        init();
})();
