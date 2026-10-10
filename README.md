# SearchBoost Pro V0.2 — Paket Lemehost KVM (UJIAN PERSENDIRIAN)

Fungsi yang telah dibina:
1. UI manual V0.1: audit input produk, cadangan tajuk/penerangan, simpan localStorage, CSV/JSON, perbandingan data.
2. Pemeriksaan URL HTML awam pada domain Shopee/TikTok tertentu dan domain website milik anda yang dibenarkan secara konfigurasi.
3. Status terhad apabila laman sekat scraping/login/redirect; TIDAK bypass sekatan dan TIADA ranking rasmi.
4. Backend FastAPI + docker-compose VPS. `/health` untuk monitor.

## Cara pasang pada Lemehost KVM (Ubuntu 24.04 LTS)
1. Tempah **Linux VPS KVM 4GB / 2 vCPU**, lokasi Singapore di https://lemehost.com/hosting/354/kvm . Jangan ambil Minecraft/Game hosting.
2. Sambung SSH dengan kunci SSH. Pada VPS baharu: kemas kini Ubuntu, pasang Docker Engine + compose plugin daripada repositori rasmi Docker; aktifkan firewall 22/80/443 dan fail2ban. SSH gunakan key, larang login root dengan kata laluan.
3. Upload ZIP ini ke VPS dan extract di direktori milik pengguna deploy.
4. Salin `.env.example` kepada `.env`. Untuk audit domain website sendiri, tambah nama host yang tepat dalam VERIFY_SITE_HOSTS; jangan masukkan domain dalaman/IP.
5. Jalankan `docker compose up -d --build`. Semak dengan `curl -f http://127.0.0.1:8080/health` (hanya daripada VPS).
6. Untuk website awam, beli domain sendiri, tunjukkan A record ke IP VPS. Pasang Caddy daripada repositori rasmi. Salin `Caddyfile.example` dan ganti domain serta bcrypt hash kata laluan; pastikan Caddy berjaya mendapat HTTPS. Hanya port 80/443 dibuka ke umum; API port 8080 kekal 127.0.0.1. Jangan buang `basic_auth` semasa percubaan.
7. Cuba 1 URL HTTPS penuh produk melalui interface. Jika sekatan, gunakan Audit Produk manual. Semak browser DevTools dan Docker logs jika ralat.
8. Backup: rekod dalam browser wajib dieksport JSON berkala. Snapshot VPS BUKAN backup data browser. Database pengguna, OAuth dan billing BELUM ada.

## Keselamatan / had
- Akses URL: senarai domain dibenarkan secara tepat, HTTPS sahaja, port 443, tanpa redirect automatik, tiada akses arbitari IP dalaman.
- Had 10 semakan/minit/alamat IP, limit HTML 384KB, request timeout 7 saat.
- URL awam tidak menunjukkan statistik tertutup, kedudukan carian, jualan atau keyword volume.
- Halaman platform mungkin tidak membenarkan pembacaan metadata. Sistem semak robots.txt dahulu dan tidak membaca URL yang dilarang. Tidak bypass CAPTCHA, login atau API.
- Tidak mempunyai akaun pengguna, MFA multiuser, data terasing antara pelanggan, sesi komersial atau audit keselamatan bebas. Jangan jual akses akaun kepada peniaga lain lagi.
- Sebarang scraping tertakluk kepada polisi laman; jika dilarang, nonaktifkan pemeriksaan dan gunakan input manual/API rasmi.
- `VERIFY_SITE_HOSTS` hanya untuk domain yang anda miliki dan dipercayai. Jangan tambah domain yang dikawal pihak asing tanpa perlindungan SSRF tambahan.

## Ujian
`python -m pytest -q` setelah install `pytest` dalam env ujian.
