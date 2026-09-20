import sqlite3
import os

DB_FILE = "tas_finance.db"

def get_db_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Tabel Users
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        full_name TEXT NOT NULL,
        role TEXT NOT NULL,
        balance TEXT NOT NULL
    );
    """)

    # Tabel Transactions
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ref_number TEXT NOT NULL,
        tx_date TEXT NOT NULL,
        description TEXT NOT NULL,
        account TEXT NOT NULL,
        debit TEXT NOT NULL,
        credit TEXT NOT NULL,
        status TEXT NOT NULL
    );
    """)

    # Tabel Memos (untuk Papan Pengumuman Internal & Lab XSS)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS memos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        author TEXT NOT NULL,
        timestamp TEXT NOT NULL,
        content TEXT NOT NULL
    );
    """)

    # Tabel Metrik Kampanye Phishing & Awareness
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS phishing_events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        event_type TEXT NOT NULL, -- 'view', 'submit', 'reported', 'completed_awareness'
        ip_address TEXT NOT NULL,
        user_agent TEXT NOT NULL,
        timestamp TEXT NOT NULL
    );
    """)

    # Cek apakah users sudah ada
    cursor.execute("SELECT COUNT(*) FROM users")
    if cursor.fetchone()[0] == 0:
        users = [
            ("admin", "Admin@TAS2024", "Administrator Keuangan", "Super Admin", "Rp 120.000.000.000"),
            ("budi.finance", "password123", "Budi Santoso", "CFO Division", "Rp 47.850.000.000"),
            ("siti.akuntansi", "qwerty", "Siti Rahmawati", "Staff Akuntansi", "Rp 15.200.000.000"),
            ("andi.audit", "12345678", "Andi Pratama", "Internal Auditor", "Rp 5.500.000.000"),
            ("direktur", "rahasia123", "Ir. Bambang Tri", "Direktur Utama", "Rp 500.000.000.000")
        ]
        cursor.executemany(
            "INSERT INTO users (username, password, full_name, role, balance) VALUES (?, ?, ?, ?, ?)",
            users
        )

    # Cek apakah transactions sudah ada
    cursor.execute("SELECT COUNT(*) FROM transactions")
    if cursor.fetchone()[0] == 0:
        txs = [
            ("TRF-0924-001", "19 Sep", "Transfer Vendor A (Perangkat Keras)", "•••• 4521", "Rp 250.000.000", "—", "Sukses"),
            ("RCV-0924-012", "18 Sep", "Pembayaran Klien B (Kontrak Tahunan)", "•••• 7823", "—", "Rp 1.200.000.000", "Sukses"),
            ("TRF-0924-003", "17 Sep", "Penggajian Karyawan Periode September", "•••• 4521", "Rp 850.000.000", "—", "Sukses"),
            ("TRF-0924-007", "15 Sep", "Tagihan Infrastruktur Cloud & IT", "•••• 4521", "Rp 45.500.000", "—", "Pending"),
            ("RCV-0924-009", "12 Sep", "Royalti Lisensi Software Enterprise", "•••• 7823", "—", "Rp 320.000.000", "Gagal"),
            ("TRF-0924-010", "10 Sep", "Biaya Digital Marketing Q3", "•••• 4521", "Rp 180.000.000", "—", "Sukses"),
            ("RCV-0924-015", "08 Sep", "Invoice Proyek Delta Keamanan Siber", "•••• 7823", "—", "Rp 2.500.000.000", "Sukses"),
            ("TRF-0924-018", "05 Sep", "Sewa Gedung Kantor Jakarta Pusat", "•••• 4521", "Rp 125.000.000", "—", "Sukses"),
            ("TRF-0924-022", "02 Sep", "Pengadaan Lisensi Antivirus Korporat", "•••• 4521", "Rp 35.000.000", "—", "Sukses"),
            ("RCV-0924-025", "01 Sep", "Pelunasan Termin 2 Proyek Bank Mitra", "•••• 7823", "—", "Rp 800.000.000", "Sukses")
        ]
        cursor.executemany(
            "INSERT INTO transactions (ref_number, tx_date, description, account, debit, credit, status) VALUES (?, ?, ?, ?, ?, ?, ?)",
            txs
        )

    # Cek apakah memos sudah ada
    cursor.execute("SELECT COUNT(*) FROM memos")
    if cursor.fetchone()[0] == 0:
        sample_memos = [
            ("Budi Santoso (CFO)", "19 Sep 2024, 09:15", "Pengingat: Batas akhir penutupan buku kas Q3 adalah tanggal 25 bulan ini. Harap semua divisi segera menyelesaikan laporan."),
            ("Siti Rahmawati", "18 Sep 2024, 14:30", "Semua pengajuan reimbursement di atas Rp 10.000.000 wajib dilampirkan tanda tangan Kepala Departemen."),
            ("IT Support", "15 Sep 2024, 11:00", "Pemeliharaan berkala server finansial akan dilaksanakan hari Sabtu pukul 22.00 - 24.00 WIB.")
        ]
        cursor.executemany(
            "INSERT INTO memos (author, timestamp, content) VALUES (?, ?, ?)",
            sample_memos
        )

    # Cek apakah phishing_events sudah ada
    cursor.execute("SELECT COUNT(*) FROM phishing_events")
    if cursor.fetchone()[0] == 0:
        sample_events = [
            ("view", "192.168.1.102", "Mozilla/5.0 (Windows NT 10.0; Win64; x64)", "19 Sep 2024, 08:30:12"),
            ("submit", "192.168.1.102", "Mozilla/5.0 (Windows NT 10.0; Win64; x64)", "19 Sep 2024, 08:31:05"),
            ("completed_awareness", "192.168.1.102", "Mozilla/5.0 (Windows NT 10.0; Win64; x64)", "19 Sep 2024, 08:34:20"),
            ("view", "192.168.1.115", "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)", "19 Sep 2024, 09:10:00"),
            ("reported", "192.168.1.115", "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)", "19 Sep 2024, 09:12:15"),
            ("view", "192.168.1.140", "Mozilla/5.0 (Windows NT 10.0; Win64; x64)", "19 Sep 2024, 10:05:44"),
            ("submit", "192.168.1.140", "Mozilla/5.0 (Windows NT 10.0; Win64; x64)", "19 Sep 2024, 10:06:12"),
            ("view", "192.168.1.188", "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X)", "19 Sep 2024, 11:45:30"),
            ("reported", "192.168.1.188", "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X)", "19 Sep 2024, 11:46:02")
        ]
        cursor.executemany(
            "INSERT INTO phishing_events (event_type, ip_address, user_agent, timestamp) VALUES (?, ?, ?, ?)",
            sample_events
        )

    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
    print("Database tas_finance.db initialized successfully.")

