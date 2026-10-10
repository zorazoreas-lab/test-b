from __future__ import annotations
import os, re, time
from collections import defaultdict, deque
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse
from urllib.robotparser import RobotFileParser
import httpx
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel, Field

APP_DIR=Path(__file__).resolve().parent
app=FastAPI(title="SearchBoost Pro Prototype", docs_url=None, redoc_url=None, openapi_url=None)
BASE_HOSTS={"shopee.com.my", "www.shopee.com.my", "shopee.sg", "www.shopee.sg", "tiktok.com", "www.tiktok.com", "shop.tiktok.com", "vt.tiktok.com", "vm.tiktok.com", "seller-my.tiktok.com"}
EXTRA_HOSTS={h.strip().lower() for h in os.getenv("VERIFY_SITE_HOSTS", "").split(",") if h.strip()}
ALLOWED=BASE_HOSTS|EXTRA_HOSTS
HITS=defaultdict(deque)
class LinkInput(BaseModel):
    url: str = Field(min_length=12,max_length=1500)
class MetaParser(HTMLParser):
    def __init__(self):
        super().__init__();self.title="";self.description="";self.og_title="";self.og_description="";self.in_title=False
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if tag=='title':self.in_title=True
        if tag=='meta':
            k=(a.get('property') or a.get('name') or '').lower(); val=a.get('content','').strip()
            if k=='description' and not self.description:self.description=val
            if k=='og:title' and not self.og_title:self.og_title=val
            if k=='og:description' and not self.og_description:self.og_description=val
    def handle_endtag(self,tag):
        if tag=='title':self.in_title=False
    def handle_data(self,data):
        if self.in_title:self.title+=data

def parse_public_url(link: str):
    try:u=urlparse(link)
    except ValueError:raise HTTPException(400,'URL tidak sah.')
    try:
        parsed_port=u.port
    except ValueError:
        raise HTTPException(400,'Nombor port URL tidak sah.')
    if u.scheme!='https' or not u.hostname or u.hostname.lower() not in ALLOWED or u.username or u.password or parsed_port not in (None,443):
        raise HTTPException(400,'URL tidak dibenarkan. Hanya HTTPS pada domain platform yang disenaraikan atau domain laman milik anda dalam VERIFY_SITE_HOSTS.')
    if any(c in link for c in '\n\r\t') or not u.path.startswith('/'):
        raise HTTPException(400,'URL tidak sah.')
    return u

def platform_of(host:str)->str:
    if 'shopee.' in host:return 'Shopee'
    if 'tiktok.com' in host:
        return 'TikTok Shop' if host.startswith('shop.') or host.startswith('seller-') or '/product/' in host else 'TikTok Video'
    return 'Google / Website'

@app.get('/')
def index():return FileResponse(APP_DIR/'index.html',headers={'Cache-Control':'no-store','X-Content-Type-Options':'nosniff','Referrer-Policy':'no-referrer','X-Frame-Options':'DENY','Content-Security-Policy':"default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; base-uri 'none'; form-action 'self'"})

@app.get('/health')
def health():return {'ok':True}

@app.post('/api/inspect')
async def inspect(body: LinkInput, request: Request):
    u=parse_public_url(body.url.strip())
    ip=request.client.host if request.client else 'unknown'
    now=time.monotonic();q=HITS[ip]
    while q and q[0]<now-60:q.popleft()
    if len(q)>=10:raise HTTPException(429,'Had 10 semakan seminit bagi setiap IP. Cuba kemudian.')
    q.append(now)
    host=u.hostname.lower();kind=platform_of(host)
    if kind=='TikTok Video' and '/product/' in u.path:kind='TikTok Shop'
    base={'platform':kind,'url':body.url,'source':'metadata HTML awam','title':'','description':'','status':'limited'}
    # No redirects, cookies, user credentials, login, javascript or captcha bypass.
    # The hostname is limited to an explicit fixed allowlist to avoid arbitrary SSRF.
    try:
        async with httpx.AsyncClient(follow_redirects=False,trust_env=False,timeout=httpx.Timeout(7.0),verify=True,headers={'User-Agent':'SearchBoostProPublicMetaInspector/0.2 (consent required)'}) as client:
            robots=await client.get(f'https://{host}/robots.txt')
            if robots.status_code==200:
                rp=RobotFileParser();rp.parse(robots.text.splitlines())
                if not rp.can_fetch('SearchBoostProPublicMetaInspector',body.url):
                    base['notes']='Robots.txt tidak membenarkan pembacaan URL ini. Gunakan audit manual atau API rasmi.'
                    return base
            elif robots.status_code!=404:
                base['notes']='Polisi robot tidak dapat disahkan. Tidak melakukan pembacaan automatik; gunakan audit manual.'
                return base
            async with client.stream('GET',body.url) as resp:
                if resp.is_redirect:
                    base['notes']='Pautan ini redirect (mungkin link pendek). Kami tidak mengikuti redirect automatik atas faktor keselamatan. Gunakan URL penuh produk.'
                    return base
                if resp.status_code in (401,403,429):
                    base['notes']='Halaman menyekat akses automatik atau memerlukan login. Sila salin maklumat produk melalui borang manual.'
                    return base
                if resp.status_code!=200:
                    base['notes']='Halaman tidak memulangkan HTTP 200; status '+str(resp.status_code)+'.'
                    return base
                if 'text/html' not in resp.headers.get('content-type','').lower():
                    base['notes']='Halaman tidak memberikan HTML awam.'
                    return base
                buf=bytearray()
                async for piece in resp.aiter_bytes():
                    buf.extend(piece)
                    if len(buf)>384000:
                        break
        parser=MetaParser();parser.feed(bytes(buf).decode('utf-8','replace'))
        clean=lambda s:re.sub(r'\s+',' ',s or '').strip()[:500]
        base['title']=clean(parser.og_title or parser.title)
        base['description']=clean(parser.og_description or parser.description)
        if not base['title'] and not base['description']:
            base['notes']='HTML boleh dicapai tetapi metadata tidak tersedia. Isi listing sebenar secara manual.'
            return base
        base['status']='ok'
        base['notes']='Ini metadata HTML awam, bukan pengesahan listing penuh, ranking atau jualan. Sahkan fakta dengan Seller Centre.'
        return base
    except (httpx.HTTPError,UnicodeError,ValueError) as exc:
        base['notes']='Gagal mengambil metadata awam; boleh disebabkan rangkaian, had akses atau polisi laman. Isi data manual.'
        return base
