# SearchBoost Pro — GitHub → Lemehost KVM (ujian persendirian)

## 1. Repository GitHub
- Pergi ke https://github.com/new, namakan `searchboost-pro`, pilih **Private**.
- Extract ZIP yang diterima pada telefon/komputer. **Jangan upload ZIP sebagai satu fail sahaja**; upload kandungan folder ini sebagai fail dan folder dalam root repository, termasuk folder `app/`, `tests/` dan `.github/`.
- Fail `docker-compose.yml`, `Dockerfile` dan `requirements.txt` mesti berada di root repository, bukannya dalam subfolder ZIP.
- Jangan upload `.env`, token, password, atau private SSH key. `.env.example` selamat sebagai contoh sahaja.
- Ujian GitHub Actions akan berjalan selepas push untuk memeriksa unit tests.

## 2. Lemehost VPS (Ubuntu Linux KVM)
- Pilih VPS KVM (disyorkan 4GB RAM) di lokasi Singapore jika ditawarkan.
- Gunakan akaun Linux pengguna deploy dengan sudo, bukannya password root untuk operasi harian.
- Pasang Git, Docker Engine, dan Compose plugin daripada repositori rasmi Docker. Konfigurasi firewall dan SSH key, serta kunci akses root/password mengikut amalan selamat.
- Pastikan `git --version` dan `docker compose version` berfungsi.

## 3. Sambungkan private repository dengan GitHub Deploy Key (read-only)
Jalankan perintah berikut dalam terminal VPS sebagai pengguna deploy. Jangan menimpa kunci yang sedia ada:

```bash
mkdir -p ~/.ssh && chmod 700 ~/.ssh
ssh-keygen -t ed25519 -f ~/.ssh/searchboost_deploy -N '' -C 'searchboost-lemehost-readonly'
cat ~/.ssh/searchboost_deploy.pub
```

**Salin hanya output `.pub`** ke GitHub repository → **Settings → Deploy keys → Add deploy key**. Pastikan `Allow write access` **tidak** dipilih. Jangan sekali-kali kongsi fail tanpa sambungan `.pub`.

```bash
cat >> ~/.ssh/config <<'EOF'
Host github-searchboost
  HostName github.com
  User git
  IdentityFile ~/.ssh/searchboost_deploy
  IdentitiesOnly yes
EOF
chmod 600 ~/.ssh/config
ssh -T git@github-searchboost
```

Pada kali pertama, sahkan fingerprint SSH dengan dokumentasi rasmi GitHub sebelum menjawab `yes`. Respons GitHub mungkin menyatakan berjaya diautentikasi tetapi tiada shell; itu normal.

## 4. Clone dan mula aplikasi
Gantikan `USERNAME` dengan nama akaun atau organisasi GitHub anda:

```bash
sudo apt-get update
sudo apt-get install -y git
git clone git@github-searchboost:USERNAME/searchboost-pro.git
cd searchboost-pro
cp .env.example .env
docker compose up -d --build
curl -f http://127.0.0.1:8080/health
```

Jika respons `/health` ialah `{"ok":true}`, aplikasi backend sudah hidup secara setempat. Server **tidak** serta-merta boleh diakses melalui internet kerana port 8080 terikat pada `127.0.0.1`.

## 5. HTTPS dan domain
- Arahkan A record domain/subdomain ke IP VPS.
- Pasang Caddy daripada repositori rasmi; gunakan `Caddyfile.example` sebagai templat.
- Tukar domain contoh dan gantikan `HASH_PASSWORD` dengan hash yang dijana melalui `caddy hash-password`.
- Kekalkan `basic_auth` untuk ujian persendirian.
- Hanya buka port 80/443 kepada orang awam, 22 SSH pada IP pentadbir jika boleh. Jangan buka 8080.
- Jangan letak kata laluan sebenar di GitHub. Simpan konfigurasi Caddy sebenar di server sahaja.

## 6. Kemas kini selepas mengedit GitHub
```bash
cd ~/searchboost-pro
git pull --ff-only origin main
docker compose up -d --build
docker compose ps
curl -f http://127.0.0.1:8080/health
```

Sistem tidak akan auto-deploy selepas push; anda mengawal bila kemas kini diterbitkan. Sebelum deployment komersial, tambah staging, backup, ujian keselamatan dan rollback.

## Had sebenar produk
- MVP ini hanya untuk **ujian persendirian**. Ia mempunyai URL metadata inspector terhad dan audit input produk manual.
- Belum ada akaun pengguna berasingan, database pelanggan, OAuth Google/Shopee/TikTok atau ranking sebenar.
- Tidak boleh menjamin ranking nombor satu; scraping mungkin tidak dibenarkan atau disekat.
- Jangan letakkan data kedai atau pelanggan sensitif sebelum keselamatan dipertingkat.

## Rujukan rasmi
- https://docs.github.com/en/authentication/connecting-to-github-with-ssh/managing-deploy-keys
- https://docs.docker.com/engine/install/ubuntu/
- https://docs.docker.com/compose/how-tos/production/
