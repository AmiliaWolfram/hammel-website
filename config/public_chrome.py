"""One canonical Home header/footer for every public HTTP HTML response.

Public static HTML uses markers; Django templates are normalized at response time.
Internal staff/admin pages are deliberately excluded.
"""
import re
from pathlib import Path
from django.conf import settings

HEADER_MARK = "<!-- PUBLIC_SHARED_HEADER -->"
FOOTER_MARK = "<!-- PUBLIC_SHARED_FOOTER -->"
HEADER_RE = re.compile(r"<header\b[^>]*>.*?</header>", re.I | re.S)
FOOTER_RE = re.compile(r"<footer\b[^>]*>.*?</footer>", re.I | re.S)
CSS = '<link rel="stylesheet" href="/assets/css/style.css"><link rel="stylesheet" href="/assets/css/navigation-2026.css"><link rel="stylesheet" href="/assets/css/footer-unified.css?v=shared-live-20261027">'

class PublicChromeMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.base = Path(settings.BASE_DIR) / "website" / "shared"

    def __call__(self, request):
        response = self.get_response(request)
        path = request.path
        if (path.startswith(("/staff/", "/admin/", "/api/", "/static/", "/assets/", "/media/"))
                or response.status_code != 200 or getattr(response, "streaming", False)
                or "text/html" not in response.get("Content-Type", "")):
            return response
        try:
            html = response.content.decode(response.charset or "utf-8")
            header = (self.base / "header.html").read_text(encoding="utf-8")
            footer = (self.base / "footer.html").read_text(encoding="utf-8")
        except (UnicodeError, OSError):
            return response
        if HEADER_MARK in html:
            html = html.replace(HEADER_MARK, header, 1)
        elif HEADER_RE.search(html):
            html = HEADER_RE.sub(lambda m: header, html, count=1)
        else:
            html = re.sub(r"<body\b[^>]*>", lambda m: m.group(0)+header, html, count=1, flags=re.I)
        if FOOTER_MARK in html:
            html = html.replace(FOOTER_MARK, footer, 1)
        elif FOOTER_RE.search(html):
            # Only replace the last footer, to avoid any footer inside article/card.
            matches = list(FOOTER_RE.finditer(html))
            match = matches[-1]
            html = html[:match.start()] + footer + html[match.end():]
        else:
            html = re.sub(r"</body>", footer + "</body>", html, count=1, flags=re.I)
        # Canonical CSS is always loaded last, after every page-specific stylesheet.
        # Existing footer-unified.css alone is not sufficient to isolate legacy page CSS.
        chrome_css = '<link rel="stylesheet" href="/assets/css/public-chrome-canonical.css?v=20261030-home-aligned">'
        html = re.sub(r'<link\b[^>]*public-chrome-canonical\.css[^>]*>', '', html, flags=re.I)
        html = re.sub(r'</head>', chrome_css + '</head>', html, count=1, flags=re.I)
        html = re.sub(r"</body>", '<script src="/assets/js/public-header-scroll.js?v=20261027-4"></script></body>', html, count=1, flags=re.I)
        response.content = html.encode("utf-8")
        response["Content-Length"] = str(len(response.content))
        if "ETag" in response:
            del response["ETag"]
        return response
