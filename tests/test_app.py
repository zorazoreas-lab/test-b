from fastapi.testclient import TestClient
from app.main import app,parse_public_url,platform_of,MetaParser
from fastapi import HTTPException
import pytest
client=TestClient(app)

def test_home():
    r=client.get('/');assert r.status_code==200 and 'SearchBoost Pro' in r.text

def test_health():assert client.get('/health').json()=={'ok':True}

@pytest.mark.parametrize('url',["http://shopee.com.my/a", "https://127.0.0.1/", "https://localhost/private", "https://example.com/", "https://shopee.com.my:8443/item", "https://user:pass@shopee.com.my/p"])
def test_rejected(url):
    r=client.post('/api/inspect',json={'url':url});assert r.status_code==400

def test_classify():
    assert platform_of('shopee.com.my')=='Shopee'
    assert platform_of('www.tiktok.com')=='TikTok Video'


def test_metadata_parser():
    p=MetaParser();p.feed('<title>Judul Asal</title><meta name="description" content="Penerangan Produk"><meta property="og:title" content="Tajuk OG">')
    assert p.og_title=='Tajuk OG' and p.description=='Penerangan Produk'
