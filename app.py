"""
=============================================================================
  PT Teknologi Aman Sejahtera – Cybersecurity Lab Live Server
  Modul Lengkap:
  1. SQL Injection (SQLMap / Manual) pada Login & Filter Laporan
  2. Credential Brute-Forcing (Hydra / Burp Intruder) pada /api/login
  3. Stored & Reflected XSS (Papan Memo & Query Pencarian)
  4. Session Hijacking (Cookie session_token tanpa HttpOnly / Secure)
  5. Phishing Simulator (/it-update -> /awareness-education)
=============================================================================
  PERINGATAN: Aplikasi ini dibuat KHUSUS untuk tujuan edukasi lab universitas.
=============================================================================
"""

from flask import (
    Flask, render_template, request, redirect,
    url_for, make_response, jsonify
)
from datetime import datetime
import os
from database import get_db_connection, init_db

app = Flask(__name__)
app.secret_key = "lab-cybersec-tas-2024"

LOG_FILE = "web_access.log"
SESSION_TOKEN_VALUE = "xYz890AbC"
HTTPONLY_ENABLED = False  # Dapat di-toggle untuk demonstrasi mitigasi HttpOnly

# ---------------------------------------------------------------------------
# Custom Access Logger Middleware
# ---------------------------------------------------------------------------

@app.after_request
def access_logger(response):
    """
    Mencatat setiap request ke web_access.log dengan format persis sesuai spesifikasi:
      [YYYY-MM-DD HH:MM:SS] IP: <ip> | <METHOD> <PATH> | Status: <status> |
        Cookie: session_token=<val>; User-Agent: <ua>
    Khusus POST /api/login:
      ...| User: Budi_Finance | Set-Cookie: session_token=xYz890AbC;
    """
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ip = request.remote_addr or "unknown"
    method = request.method
    path = request.path
    status = response.status_code
    ua = request.headers.get("User-Agent", "unknown")

    if path == "/api/login" and method == "POST":
        cookie_info = "User: Budi_Finance | Set-Cookie: session_token=xYz890AbC;"
    else:
        session_token = request.cookies.get("session_token", "")
        cookie_info = f"Cookie: session_token={session_token}; User-Agent: {ua}"

    log_line = (
        f"[{now}] IP: {ip} | {method} {path} | Status: {status} | {cookie_info}\n"
    )

    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(log_line)
    except Exception:
        pass

    print(log_line, end="")
    return response


# ---------------------------------------------------------------------------
# Helper Otentikasi
# ---------------------------------------------------------------------------

def is_authenticated():
    return request.cookies.get("session_token") == SESSION_TOKEN_VALUE


# ===========================================================================
#  PORTAL FINANSIAL & VULNERABILITY LAB ENDPOINTS
# ===========================================================================

@app.route("/")
def index():
    if is_authenticated():
        return redirect(url_for("dashboard_keuangan"))
    return redirect(url_for("login"))


@app.route("/login", methods=["GET"])
def login():
    error = request.args.get("error")
    return render_template("login.html", error=error)


@app.route("/api/login", methods=["POST"])
def api_login():
    """
    Endpoint Login:
    - Mendukung Brute-Force testing (Hydra / Burp Intruder).
    - Sengaja rentan terhadap SQL Injection concatenation (' OR 1=1 --).
    - Bila sukses, menyetel session_token TANPA flag HttpOnly dan Secure.
    """
    username = request.form.get("username", "").strip()
    password = request.form.get("password", "").strip()

    conn = get_db_connection()
    cursor = conn.cursor()

    # VULNERABLE SQL QUERY (Concatenation string formatting):
    # Mahasiswa dapat menguji SQLi Auth Bypass: ' OR 1=1 --
    # Atau menguji Credential Brute-Forcing via Hydra / Burp
    query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
    user = None
    try:
        cursor.execute(query)
        user = cursor.fetchone()
    except Exception:
        user = None
    finally:
        conn.close()

    if user:
        resp = make_response(redirect(url_for("dashboard_keuangan")))
        # CRITICAL LAB FEATURE: HttpOnly=False & Secure=False
        resp.set_cookie(
            "session_token",
            value=SESSION_TOKEN_VALUE,
            httponly=HTTPONLY_ENABLED,
            secure=False,
            samesite="Lax",
            max_age=3600
        )
        resp.set_cookie("logged_user", value=user["username"], httponly=False, secure=False)
        return resp
    else:
        # Mengembalikan HTTP 401 agar Hydra / Burp Intruder dapat mendeteksi kegagalan
        return render_template(
            "login.html",
            error="Username atau password salah. Silakan periksa kembali kredensial Anda."
        ), 401


@app.route("/dashboard/keuangan")
def dashboard_keuangan():
    if not is_authenticated():
        return redirect(url_for("login"))

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM transactions ORDER BY id DESC LIMIT 5")
    transactions = cursor.fetchall()
    cursor.execute("SELECT * FROM memos ORDER BY id DESC LIMIT 6")
    memos = cursor.fetchall()
    conn.close()

    return render_template("dashboard_keuangan.html", transactions=transactions, memos=memos)


@app.route("/api/memo", methods=["POST"])
def api_memo():
    """
    Endpoint Tambah Memo (Stored XSS):
    Input disimpan ke database dan di-render mentah (safe filter) di dashboard.
    Mahasiswa dapat menyisipkan skrip untuk mencuri session_token via XSS.
    """
    if not is_authenticated():
        return redirect(url_for("login"))

    author = request.form.get("author", "Staff Divisi Keuangan").strip()
    content = request.form.get("content", "").strip()

    if content:
        now_str = datetime.now().strftime("%d %b %Y, %H:%M")
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO memos (author, timestamp, content) VALUES (?, ?, ?)",
            (author, now_str, content)
        )
        conn.commit()
        conn.close()

    return redirect(url_for("dashboard_keuangan"))


@app.route("/dashboard/laporan")
def dashboard_laporan():
    """
    Endpoint Laporan Keuangan:
    - Mendukung parameter ?q= yang sengaja rentan terhadap SQL Injection (target SQLMap).
    - Query parameter juga direfleksikan mentah untuk latihan Reflected XSS.
    """
    if not is_authenticated():
        return redirect(url_for("login"))

    q = request.args.get("q", "").strip()
    conn = get_db_connection()
    cursor = conn.cursor()

    if q:
        # VULNERABLE SQL QUERY (Untuk pengujian SQLMap & manual UNION/Error-based SQLi):
        sql = f"SELECT * FROM transactions WHERE description LIKE '%{q}%' OR ref_number LIKE '%{q}%' OR account LIKE '%{q}%'"
        try:
            cursor.execute(sql)
            transactions = cursor.fetchall()
        except Exception:
            transactions = []
    else:
        cursor.execute("SELECT * FROM transactions ORDER BY id DESC")
        transactions = cursor.fetchall()

    conn.close()
    return render_template("dashboard_laporan.html", transactions=transactions, query=q)


@app.route("/dashboard/transfer_dana")
def dashboard_transfer_dana():
    if not is_authenticated():
        return redirect(url_for("login"))
    return render_template("dashboard_transfer_dana.html")


@app.route("/api/transfer", methods=["POST"])
def api_transfer():
    if not is_authenticated():
        return jsonify({"status": "error", "message": "Unauthorized"}), 401

    data = request.get_json(silent=True) or {}
    amount_raw = data.get("amount", 1000000)
    try:
        amount_val = int(amount_raw)
        amount_formatted = f"Rp {amount_val:,.0f}".replace(",", ".")
    except Exception:
        amount_formatted = "Rp 1.000.000"

    now_date = datetime.now().strftime("%d %b")
    ref_number = f"TRF-{datetime.now().strftime('%m%y')}-{os.urandom(2).hex().upper()}"

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO transactions (ref_number, tx_date, description, account, debit, credit, status) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (ref_number, now_date, "Transfer Keluar via Web Portal", "•••• 4521", amount_formatted, "—", "Sukses")
    )
    conn.commit()
    conn.close()

    return jsonify({
        "status": "success",
        "message": "Transfer berhasil diproses (simulasi).",
        "ref_number": ref_number
    })


@app.route("/logout")
def logout():
    resp = make_response(redirect(url_for("login")))
    resp.delete_cookie("session_token")
    resp.delete_cookie("logged_user")
    return resp


# ===========================================================================
#  MODUL 2 – PHISHING SIMULATOR & SECURITY AWARENESS TELEMETRY
# ===========================================================================

@app.route("/it-update", methods=["GET"])
def phishing_page():
    # Catat event telemetri 'view'
    try:
        conn = get_db_connection()
        conn.cursor().execute(
            "INSERT INTO phishing_events (event_type, ip_address, user_agent, timestamp) VALUES (?, ?, ?, ?)",
            ("view", request.remote_addr or "unknown", request.headers.get("User-Agent", "unknown"), datetime.now().strftime("%d %b %Y, %H:%M:%S"))
        )
        conn.commit()
        conn.close()
    except Exception:
        pass
    return render_template("phishing.html")


@app.route("/api/phishing-submit", methods=["POST"])
def phishing_submit():
    # Catat event telemetri 'submit' (karyawan terjebak / rentan)
    # Demi etika & keamanan lab: password TIDAK disimpan, langsung dialihkan
    try:
        conn = get_db_connection()
        conn.cursor().execute(
            "INSERT INTO phishing_events (event_type, ip_address, user_agent, timestamp) VALUES (?, ?, ?, ?)",
            ("submit", request.remote_addr or "unknown", request.headers.get("User-Agent", "unknown"), datetime.now().strftime("%d %b %Y, %H:%M:%S"))
        )
        conn.commit()
        conn.close()
    except Exception:
        pass
    return redirect(url_for("awareness_education"))


@app.route("/awareness-education", methods=["GET"])
def awareness_education():
    # Catat event 'completed_awareness'
    try:
        conn = get_db_connection()
        conn.cursor().execute(
            "INSERT INTO phishing_events (event_type, ip_address, user_agent, timestamp) VALUES (?, ?, ?, ?)",
            ("completed_awareness", request.remote_addr or "unknown", request.headers.get("User-Agent", "unknown"), datetime.now().strftime("%d %b %Y, %H:%M:%S"))
        )
        conn.commit()
        conn.close()
    except Exception:
        pass
    return render_template("awareness.html")


@app.route("/api/phishing-report", methods=["POST"])
def phishing_report():
    # Saluran pelaporan insiden oleh karyawan teladan
    try:
        conn = get_db_connection()
        conn.cursor().execute(
            "INSERT INTO phishing_events (event_type, ip_address, user_agent, timestamp) VALUES (?, ?, ?, ?)",
            ("reported", request.remote_addr or "unknown", request.headers.get("User-Agent", "unknown"), datetime.now().strftime("%d %b %Y, %H:%M:%S"))
        )
        conn.commit()
        conn.close()
    except Exception:
        pass
    return jsonify({
        "status": "success",
        "message": "Terima kasih! Laporan Anda telah dicatat oleh Tim SOC Keamanan Siber TAS Corporation."
    })


# ===========================================================================
#  MODUL 3 – SOC DEFENSIVE DASHBOARDS & LAB KONTROL
# ===========================================================================

@app.route("/security/campaign-dashboard")
def campaign_dashboard():
    """Dashboard Analitik Kampanye Phishing & Kesadaran Keamanan (Defensive View)"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT event_type, COUNT(*) as count FROM phishing_events GROUP BY event_type")
    rows = cursor.fetchall()
    counts = {r["event_type"]: r["count"] for r in rows}

    total_views = counts.get("view", 0)
    total_submits = counts.get("submit", 0)
    total_reported = counts.get("reported", 0)
    total_completed = counts.get("completed_awareness", 0)

    compromise_rate = round((total_submits / total_views * 100), 1) if total_views > 0 else 0
    report_rate = round((total_reported / total_views * 100), 1) if total_views > 0 else 0
    training_rate = round((total_completed / total_submits * 100), 1) if total_submits > 0 else 0

    cursor.execute("SELECT * FROM phishing_events ORDER BY id DESC LIMIT 15")
    recent_events = cursor.fetchall()
    conn.close()

    return render_template(
        "campaign_dashboard.html",
        total_views=total_views,
        total_submits=total_submits,
        total_reported=total_reported,
        total_completed=total_completed,
        compromise_rate=compromise_rate,
        report_rate=report_rate,
        training_rate=training_rate,
        recent_events=recent_events
    )


@app.route("/security/session-audit")
def session_audit():
    """Dashboard Forensik Deteksi Session Abuse dari Log Akses"""
    from analyze_logs import analyze_session_abuse
    report = analyze_session_abuse()
    return render_template("session_audit.html", report=report, httponly_status=HTTPONLY_ENABLED)


@app.route("/api/security/toggle-httponly", methods=["POST"])
def toggle_httponly():
    """Endpoint eksperimen mahasiswa untuk menguji dampak mitigasi flag HttpOnly"""
    global HTTPONLY_ENABLED
    HTTPONLY_ENABLED = not HTTPONLY_ENABLED
    status_text = "Aktif (Aman dari XSS Session Theft)" if HTTPONLY_ENABLED else "Nonaktif (Rentan terhadap Session Theft)"
    return jsonify({
        "status": "success",
        "httponly": HTTPONLY_ENABLED,
        "message": f"Konfigurasi cookie diubah: HttpOnly sekarang {status_text}."
    })


# ===========================================================================
#  Entry Point (Live Server Deployment dengan Waitress)
# ===========================================================================

if __name__ == "__main__":
    init_db()
    if not os.path.exists(LOG_FILE):
        open(LOG_FILE, "w", encoding="utf-8").close()

    print("=" * 72)
    print("  PT TEKNOLOGI AMAN SEJAHTERA – CYBERSECURITY PENETRATION TESTING LAB")
    print("  Status: Server Aktif & Siap Diakses")
    print("  Alamat Lokal: http://127.0.0.1:5000")
    port = int(os.environ.get("PORT", 5000))
    print(f"  Port: {port}")
    print("=" * 72)

    from waitress import serve
    serve(app, host="0.0.0.0", port=port, threads=16)
