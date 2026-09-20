# 🎓 UJIAN TENGAH SEMESTER (UTS) PRAKTIKUM KEAMANAN SIBER
## MODUL: SOCIAL ENGINEERING & SESSION HIJACKING (DEFENSIVE & AWARENESS VIEW)
**Program Studi:** Teknik Informatika / Sistem Informasi / Keamanan Siber  
**Bobot Nilai:** 100 Poin  
**Sifat Ujian:** Praktikum Berbasis Lab Mandiri / Kelompok Terbimbing  
**Target Sistem:** Portal Finansial PT Teknologi Aman Sejahtera (`http://<IP_SERVER>:5000`)

---

## 📋 CAPAIAN PEMBELAJARAN (LEARNING OUTCOMES)
1. **Human Layer Security:** Memahami taktik manipulasi psikologis manusia (*pretexting, urgency, typosquatting*) serta cara merancang program *security awareness* dan simulasi phishing korporat yang etis.
2. **Session Architecture:** Menguasai konsep siklus hidup sesi web (*session lifecycle*), token sesi, atribut cookie keamanan (`HttpOnly`, `Secure`, `SameSite`), serta mekanisme ancaman *Session Fixation* dan *Session Hijacking*.
3. **Forensic Log Telemetry:** Mampu melakukan investigasi dan analisis data log akses web untuk mendeteksi anomali perilaku sesi (*session abuse detection*).
4. **Defensive Engineering:** Mampu merumuskan arsitektur mitigasi teknis dan kebijakan tata kelola keamanan korporat.

---

## 🏢 SKENARIO STUDI KASUS KORPORAT
Anda bertindak sebagai **Junior Cyber Security Analyst & Awareness Officer** di **PT Teknologi Aman Sejahtera (TAS)**. Manajemen meminta tim Anda melakukan evaluasi menyeluruh terhadap:
1. Ketahanan karyawan divisi keuangan terhadap ancaman *Social Engineering*.
2. Keamanan arsitektur manajemen sesi pada aplikasi web finansial internal.
3. Kemampuan tim SOC mendeteksi indikasi pembajakan sesi aktif dari catatan log akses server.

---

## 📝 LEMBAR TUGAS PRAKTIKUM MAHASISWA

### 📍 BAGIAN 1: Analisis & Desain Kampanye Phishing Etis (Bobot: 25 Poin)
Akses endpoint simulasi internal: `http://<IP_SERVER>:5000/it-update`

1. **Bedah 3 Indikator Kejanggalan (Red Flags):**
   - Lakukan inspeksi elemen dan analisis visual pada halaman `/it-update`.
   - Dokumentasikan bukti tangkapan layar (*screenshot*) dan jelaskan analisis Anda mengenai:
     1. **Red Flag 1 (Domain Anomali / Suspicious Asset URL):** Periksa atribut `src` pada elemen logo perusahaan. Mengapa ini mencurigakan?
     2. **Red Flag 2 (Manipulasi Psikologis Urgensi & Intimidasi):** Jelaskan teknik *pretexting* dan manipulasi *scarcity/fear* yang digunakan pada teks peringatan dan timer hitung mundur.
     3. **Red Flag 3 (Typosquatting Ejaan Korporat):** Temukan kesalahan penulisan nama entitas pada footer halaman. Jelaskan risiko teknik ini dalam skenario serangan dunia nyata.
2. **Desain Alur Program Awareness Korporat yang Etis:**
   - Jelaskan mengapa halaman `/it-update` langsung mengalihkan pengguna ke `/awareness-education` dan sama sekali tidak menyimpan password karyawan.
   - Buka dashboard metrik SOC di `/security/campaign-dashboard`. Jelaskan metrik apa saja yang wajib dipantau (*Click Rate, Compromise Rate, Report Rate*) serta bagaimana cara mengedukasi karyawan tanpa menimbulkan efek saling menyalahkan (*no-blame culture*).

---

### 📍 BAGIAN 2: Eksperimen Arsitektur Session Management & Cookie Flags (Bobot: 25 Poin)
Akses portal resmi: `http://<IP_SERVER>:5000/login`

1. **Inspeksi Cookie dan Token Sesi:**
   - Login ke portal keuangan menggunakan akun `budi.finance` (Password: `password123`) atau akun lain yang sah.
   - Buka Developer Tools (F12) -> Tab **Application** (Chrome/Edge) atau **Storage** (Firefox) -> **Cookies**.
   - Dokumentasikan atribut cookie `session_token`:
     - *Name:* `session_token`
     - *Value:* `xYz890AbC`
     - *HttpOnly:* `False` (Tidak dicentang)
     - *Secure:* `False`
     - *SameSite:* `Lax`
2. **Eksperimen Kerentanan Pembajakan Sesi (Session Hijacking):**
   - **Langkah A (Pembuktian Pembacaan Sesi via Script):**  
     Buka tab **Console** di DevTools, ketik perintah:
     ```javascript
     document.cookie
     ```
     Jelaskan mengapa token sesi Anda dapat terbaca secara terbuka oleh skrip sisi-klien (*client-side JavaScript*). Apa bahayanya jika aplikasi memiliki celah *Cross-Site Scripting (XSS)*?
   - **Langkah B (Eksperimen Replikasi Sesi di Browser/Perangkat Lain):**  
     Buka jendela *Incognito* / browser lain di Kali Linux. Salin nilai cookie tersebut secara manual. Buktikan apakah Anda dapat mengakses `/dashboard/keuangan` secara langsung tanpa harus melakukan proses otentikasi login kembali. Jelaskan konsep ini secara teoritis.
3. **Uji Coba Mitigasi Flag `HttpOnly`:**
   - Buka dashboard audit di: `http://<IP_SERVER>:5000/security/session-audit`.
   - Klik tombol **"Terapkan Mitigasi (HttpOnly=True)"**.
   - Lakukan login ulang, lalu coba kembali perintah `document.cookie` di Console.
   - Jelaskan perbedaan hasilnya dan bagaimana flag `HttpOnly` memitigasi pencurian sesi.

---

### 📍 BAGIAN 3: Forensik & Analisis Log untuk Deteksi Session Abuse (Bobot: 30 Poin)
Buka file rekaman aktivitas akses: `web_access.log` pada root folder server (atau melalui script analisis `analyze_logs.py`).

1. **Pemahaman Format Log Server:**
   - Perhatikan format log yang dicatat:
     ```text
     [YYYY-MM-DD HH:MM:SS] IP: <ip> | <METHOD> <PATH> | Status: <status> | Cookie: session_token=<val>; User-Agent: <ua>
     ```
   - Jelaskan peranan field **IP Address**, **session_token**, dan **User-Agent** dalam mendeteksi anomali sesi!
2. **Eksekusi Script Forensik Sesi:**
   - Jalankan tool forensik otomatis di terminal:
     ```bash
     python analyze_logs.py
     ```
     *(Atau buka visualisasinya di browser: `http://<IP_SERVER>:5000/security/session-audit`)*
3. **Analisis Indikasi Kejahatan Sesi (Session Abuse Findings):**
   - Berdasarkan hasil eksekusi, jawab pertanyaan berikut:
     1. Apakah terdeteksi sebuah token sesi yang digunakan oleh **lebih dari 1 alamat IP berbeda** dalam rentang waktu berdekatan? Jika ya, lampirkan bukti baris log-nya!
     2. Apakah terdeteksi perubahan **User-Agent** mendadak (misal: sesi yang semula berasal dari Browser Windows tiba-tiba membuat request menggunakan `Python-urllib`, `cURL`, atau sistem Kali Linux)?
     3. Mengapa perubahan User-Agent atau IP pada satu token aktif merupakan indikator kuat (*strong indicator*) telah terjadinya **Session Hijacking**?

---

### 📍 BAGIAN 4: Perancangan Dokumen Mitigasi Keamanan Korporat (Bobot: 20 Poin)
Sebagai seorang Security Engineer, susun rekomendasi teknis dan prosedural untuk manajemen PT Teknologi Aman Sejahtera yang mencakup:

1. **Mitigasi Teknis Sisi Web & Server (Session Hardening):**
   - Implementasi atribut `HttpOnly`, `Secure`, dan `SameSite=Strict`.
   - Konsep **Session Regeneration** (mencegah *Session Fixation* saat transisi otentikasi).
   - Konsep **Session Binding / Fingerprinting** (mengikat token sesi dengan IP dan karakteristik perangkat pengguna).
2. **Mitigasi Prosedural & Human Layer (Awareness Program):**
   - SOP ketika karyawan menerima email mendesak yang mengatasnamakan Tim IT.
   - Kebijakan pelaporan insiden (*Incident Reporting Workflow*) dan pemanfaatan tombol pelaporan phishing.

---

## 📊 RUBRIK PENILAIAN UTS PRAKTIKUM

| Komponen Penilaian | Indikator Penilaian | Skor Maksimal |
| :--- | :--- | :---: |
| **Bagian 1: Social Engineering & Phishing** | Ketepatan identifikasi 3 Red Flags, kejelasan analisis manipulasi psikologis, dan pemahaman etika simulasi phishing. | **25 Poin** |
| **Bagian 2: Session Management & Flags** | Kelengkapan bukti inspeksi cookie, pembuktian risiko ketiadaan flag HttpOnly, dan analisis dampak setelah flag diaktifkan. | **25 Poin** |
| **Bagian 3: Forensik Log & Deteksi Abuse** | Ketajaman analisis baris log `web_access.log`, pemahaman indikator anomali IP & User-Agent, dan penggunaan tool forensik `analyze_logs.py`. | **30 Poin** |
| **Bagian 4: Rekomendasi & Mitigasi** | Kelayakan, kedalaman teknis, dan kepraktisan usulan mitigasi keamanan bagi korporat. | **20 Poin** |
| **Total Nilai** | | **100 Poin** |

---

## 📦 FORMAT & PENGUMPULAN TUGAS
1. Tugas disusun dalam bentuk **Laporan Praktikum PDF** dengan format penamaan:  
   `UTS_CYBERSEC_[NIM]_[NAMA_LENGKAP].pdf`
2. Wajib menyertakan tangkapan layar (*screenshot*) bukti pengerjaan setiap tahapan beserta NIM/nama mahasiswa yang tertera pada layar.
3. Lampirkan cuplikan baris log dari `web_access.log` yang menjadi barang bukti temuan Anda.

