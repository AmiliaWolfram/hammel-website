/* Scroll position controls every frame: stop scrolling = stop pulse; scroll backwards = rewind. */
(() => {
    'use strict';
    function init() {
        const root = document.querySelector('.story');
        if (!root || matchMedia('(prefers-reduced-motion: reduce)').matches)
            return;
        const sections = [...root.querySelectorAll('.story__chapter'), root.querySelector('.story__end')].filter(Boolean);
        const tracks = [];
        const svgNS = 'http://www.w3.org/2000/svg';
        function svgEl(tag, attrs) { const el = document.createElementNS(svgNS, tag); for (const [k, v] of Object.entries(attrs || {}))
            el.setAttribute(k, v); return el; }
        sections.forEach((section, i) => {
            const art = section.querySelector('.story__art') || section.querySelector('.story__hq');
            if (!art)
                return;
            const isHQ = section.classList.contains('story__end');
            const isProduct = !!art.querySelector('.story__photo--product');
            const svg = svgEl('svg', { class: 'story__pulse', viewBox: '0 0 600 380', preserveAspectRatio: 'none', 'aria-hidden': 'true' });
            const paths = [
                'M 25 310 C 105 305 100 220 175 215 S 270 290 335 210 S 475 135 575 65',
                'M 20 305 L 140 255 L 185 255 L 230 120 L 315 120 L 365 220 L 575 90',
                'M 25 270 L 130 270 L 185 210 L 260 210 L 305 160 L 430 160 L 565 85',
                'M 25 290 L 145 290 L 220 170 L 365 170 L 420 120 L 575 120',
                'M 25 275 L 160 275 L 220 205 L 350 205 L 405 105 L 575 105',
                'M 30 315 L 125 315 L 205 175 L 300 175 L 410 95 L 570 95',
                'M 20 290 C 125 290 145 215 255 215 S 420 120 575 120'
            ];
            const d = isHQ ? 'M 20 300 L 95 300 Q 170 95 255 125 Q 330 170 390 300 L 575 300' : paths[i % paths.length];
            const track = svgEl('path', { d, class: 'story__pulse-track' }), glow = svgEl('path', { d, class: 'story__pulse-glow' }), head = svgEl('path', { d, class: 'story__pulse-head' }), dot = svgEl('circle', { r: '6', class: 'story__pulse-dot' });
            svg.append(track, glow, head, dot);
            art.append(svg);
            let blueprint = null;
            if (isProduct && !isHQ) {
                blueprint = svgEl('svg', { class: 'story__blueprint', viewBox: '0 0 600 380', preserveAspectRatio: 'none', 'aria-hidden': 'true' });
                blueprint.append(svgEl('path', { d: 'M 65 258 L 65 166 L 120 145 L 375 145 L 475 192 L 530 192 L 530 258 Z' }));
                blueprint.append(svgEl('path', { d: 'M 120 145 L 120 115 L 400 115 L 400 145 M 155 258 L 155 292 L 415 292 L 415 258' }));
                for (const x of [170, 400])
                    blueprint.append(svgEl('circle', { cx: String(x), cy: '258', r: '26' }));
                art.append(blueprint);
            }
            const length = head.getTotalLength();
            for (const el of [head, glow]) {
                el.style.strokeDasharray = String(length);
                el.style.strokeDashoffset = String(length);
            }
            tracks.push({ section, head, glow, dot, length, blueprint });
        });
        if (!tracks.length)
            return;
        let queued = false;
        function clamp(x) { return Math.max(0, Math.min(1, x)); }
        function draw() {
            queued = false;
            const vh = window.innerHeight || 800;
            for (const t of tracks) {
                const r = t.section.getBoundingClientRect();
                if (r.bottom < -vh * .4 || r.top > vh * 1.4)
                    continue;
                /* 0 as section enters from bottom, 1 as it exits top */
                const progress = clamp((vh * .88 - r.top) / (vh * .88 + r.height * .78));
                const pulse = clamp((progress - .12) / .72);
                const remaining = t.length * (1 - pulse);
                t.head.style.strokeDashoffset = String(remaining);
                t.glow.style.strokeDashoffset = String(remaining);
                const point = t.head.getPointAtLength(t.length * pulse);
                t.dot.setAttribute('cx', point.x);
                t.dot.setAttribute('cy', point.y);
                t.dot.style.opacity = pulse > .01 && pulse < .99 ? '.95' : '0';
                if (t.blueprint) {
                    const reveal = clamp((progress - .12) / .33);
                    t.blueprint.style.opacity = String(Math.sin(reveal * Math.PI) * .34);
                    t.blueprint.style.transform = `translateY(${(1 - reveal) * 7}px)`;
                }
            }
        }
        function request() { if (!queued) {
            queued = true;
            requestAnimationFrame(draw);
        } }
        root.classList.add('story--pulse-ready');
        window.addEventListener('scroll', request, { passive: true });
        window.addEventListener('resize', request, { passive: true });
        draw();
    }
    if (document.readyState === 'loading')
        document.addEventListener('DOMContentLoaded', init, { once: true });
    else
        init();
})();
