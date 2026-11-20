"""Minimal first-visit notice for the public HAMMEL website.

No optional cookies are activated by this middleware. Acknowledgement is
stored per browser tab in sessionStorage, not in a tracking cookie.
"""
import re
from django.utils.deprecation import MiddlewareMixin

STYLE = """
<style id="hml-cookie-notice-style">
.hml-cookie-shade{position:fixed;inset:0;z-index:2147483646;background:rgba(0,0,0,.57)}
.hml-cookie-dialog{position:fixed;z-index:2147483647;left:50%;top:50%;transform:translate(-50%,-50%);width:min(94vw,610px);box-sizing:border-box;padding:clamp(24px,4vw,44px);background:#fff;color:#171717;box-shadow:0 18px 70px #0004;font-family:Arial,Helvetica,sans-serif}
.hml-cookie-brand{color:#e30613;font-size:13px;font-weight:900;letter-spacing:.19em;margin-bottom:20px}
.hml-cookie-dialog h2{font-size:clamp(24px,4vw,34px);line-height:1.16;font-weight:900;margin:0 0 18px;color:#171717}
.hml-cookie-dialog p{font-size:16px;line-height:1.65;margin:0 0 22px;color:#4c4c4c}
.hml-cookie-dialog .hml-cookie-essential{background:#f3f3f3;padding:16px 18px;margin:0 0 22px;font-size:15px;font-weight:700}
.hml-cookie-dialog button{display:block;width:100%;border:0;background:#e30613;color:#fff;cursor:pointer;min-height:54px;padding:12px;font-size:15px;font-weight:900;letter-spacing:.02em}
.hml-cookie-dialog button:hover{background:#b9000b}
.hml-cookie-dialog a{display:inline-block;margin-top:17px;color:#171717;text-decoration:underline;font-size:14px}
.hml-cookie-dialog button:focus-visible,.hml-cookie-dialog a:focus-visible{outline:3px solid #111;outline-offset:3px}
body.hml-cookie-locked{overflow:hidden!important}
</style>
"""
HTML = """
<div id="hml-cookie-notice" hidden>
 <div class="hml-cookie-shade" aria-hidden="true"></div>
 <section class="hml-cookie-dialog" role="dialog" aria-modal="true" aria-labelledby="hml-cookie-title" aria-describedby="hml-cookie-description">
  <div class="hml-cookie-brand">HAMMEL</div>
  <h2 id="hml-cookie-title">Datenschutzhinweis</h2>
  <p id="hml-cookie-description">Wir verwenden ausschließlich technisch notwendige Cookies, um die Sicherheit und grundlegenden Funktionen unserer Website zu gewährleisten. Es werden derzeit keine optionalen Analyse- oder Marketing-Cookies über diesen Hinweis aktiviert.</p>
  <div class="hml-cookie-essential">✓ Notwendige Cookies – immer aktiv</div>
  <button type="button" id="hml-cookie-acknowledge">VERSTANDEN</button>
  <a href="/datenschutz/">Datenschutzerklärung</a>
 </section>
</div>
<script id="hml-cookie-notice-script">
(function(){
 var key='hammel_cookie_notice_tab_ack_v2';
 var notice=document.getElementById('hml-cookie-notice');
 if(!notice)return;
 var acknowledged=false;
 try{acknowledged=sessionStorage.getItem(key)==='yes';}catch(e){}
 if(acknowledged)return;
 notice.hidden=false;
 document.body.classList.add('hml-cookie-locked');
 var button=document.getElementById('hml-cookie-acknowledge');
 button.focus();
 button.addEventListener('click',function(){
   try{sessionStorage.setItem(key,'yes');}catch(e){}
   notice.hidden=true;
   document.body.classList.remove('hml-cookie-locked');
 });
})();
</script>
"""

class PublicCookieNoticeMiddleware(MiddlewareMixin):
    def process_response(self, request, response):
        path = request.path.lower()
        if (path.startswith(('/staff/', '/admin/', '/api/', '/assets/', '/static/', '/media/'))
                or request.method != 'GET'
                or response.status_code != 200
                or response.get('Content-Encoding')
                or not response.get('Content-Type', '').lower().startswith('text/html')
                or getattr(response, 'streaming', False)):
            return response
        try:
            body = response.content.decode(response.charset or 'utf-8')
        except (UnicodeError, AttributeError):
            return response
        if 'id="hml-cookie-notice"' in body or '</body>' not in body.lower():
            return response
        body, count = re.subn(r'</head\s*>', STYLE + '</head>', body, count=1, flags=re.I)
        if not count:
            return response
        body = re.sub(r'</body\s*>', HTML + '</body>', body, count=1, flags=re.I)
        response.content = body.encode(response.charset or 'utf-8')
        if response.has_header('Content-Length'):
            response['Content-Length'] = str(len(response.content))
        return response
