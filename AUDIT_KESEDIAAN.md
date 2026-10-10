# Audit SearchBoost Pro 11 Oktober 2026

## LULUS penilaian kod setempat (bergantung ujian)
- Manual listing audit, scoring dalaman, rekod localStorage, import/eksport dan pengiraan prestasi.
- URL metadata inspector: domain allowlist, HTTPS, request limit, no redirect, no bypass.
- Docker build path dan localhost-only port binding.

## BELUM SIAP
- API rasmi Shopee/TikTok Shop/Google Search Console OAuth.
- Keyword search volume, ranking live, sunting listing automatik.
- Single Sign On, users/roles, tenant isolation, MFA; PostgreSQL dan server-side backup.
- Pemeriksaan keselamatan bebas, pengujian beban, compliance pelanggan dan pengesahan polisi scraping.

## GO / NO-GO
- GO: ujian persendirian di VPS Lemehost di belakang kata laluan, akaun sendiri, data tidak sensitif.
- NO-GO: menjual produk sebagai auto-rank booster / produk SaaS multiuser, menggunakan scraping yang dilarang atau memberikan jaminan #1.

## Ujian berkualiti
1. Endpoint kesihatan HTTP 200.
2. Browser form manual diaudit dan disimpan.
3. URL HTTPS Shopee/TikTok yang dibenarkan, status metadata atau fallback diterima dengan betul.
4. URL localhost/IP/private/HTTP/redirect ditolak atau diberi status terhad.
5. CSV dan JSON eksport serta pulihkan tanpa ralat; audit tidak menyisip HTML daripada input tidak dipercayai.
6. Data ranking tidak dipaparkan seolah-olah rasmi.
