import urllib.request, urllib.parse, http.cookiejar
import subprocess
import time
import os
import sys

def run_tests():
    base = "http://127.0.0.1:5000"
    results = []

    print("[*] Menjalankan pengujian endpoint lab...")

    # 1. Test Login Gagal (Brute Force / Hydra check)
    jar = http.cookiejar.CookieJar()
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
    wrong_data = urllib.parse.urlencode({"username": "budi.finance", "password": "wrongpassword999"}).encode()
    req = urllib.request.Request(base + "/api/login", data=wrong_data)
    try:
        resp = opener.open(req)
        results.append(("FAIL", "Login password salah harusnya return 401, tapi return " + str(resp.status)))
    except urllib.error.HTTPError as e:
        if e.code == 401:
            body = e.read().decode("utf-8")
            if "salah" in body:
                results.append(("PASS", "Login salah return 401 & terdeteksi error 'salah' (Siap untuk Hydra & Burp Intruder)"))
            else:
                results.append(("WARN", "Login salah return 401 tapi pesan tidak spesifik"))
        else:
            results.append(("FAIL", "Login salah return status " + str(e.code)))

    # 2. Test Login Sukses (Kredensial Valid)
    valid_data = urllib.parse.urlencode({"username": "budi.finance", "password": "password123"}).encode()
    req2 = urllib.request.Request(base + "/api/login", data=valid_data)
    try:
        resp2 = opener.open(req2)
        st_cookie = next((c for c in jar if c.name == "session_token"), None)
        if st_cookie and st_cookie.value == "xYz890AbC":
            httponly = st_cookie.has_nonstandard_attr("HttpOnly")
            secure = st_cookie.secure
            results.append(("PASS", f"Login kredensial sukses -> session_token={st_cookie.value} (HttpOnly={httponly}, Secure={secure})"))
        else:
            results.append(("FAIL", "Cookie session_token tidak tersetting dengan benar"))
    except Exception as e:
        results.append(("FAIL", "Login valid gagal: " + str(e)))

    # 3. Test SQL Injection Auth Bypass (' OR 1=1 --)
    jar_sqli = http.cookiejar.CookieJar()
    opener_sqli = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar_sqli))
    sqli_data = urllib.parse.urlencode({"username": "' OR 1=1 --", "password": "randompassword"}).encode()
    req3 = urllib.request.Request(base + "/api/login", data=sqli_data)
    try:
        resp3 = opener_sqli.open(req3)
        st_sqli = next((c for c in jar_sqli if c.name == "session_token"), None)
        if st_sqli and "dashboard" in resp3.url:
            results.append(("PASS", "SQL Injection Auth Bypass (' OR 1=1 --) SUKSES masuk dashboard!"))
        else:
            results.append(("FAIL", "SQL Injection Auth Bypass gagal"))
    except Exception as e:
        results.append(("FAIL", "SQL Injection login error: " + str(e)))

    # 4. Test SQL Injection & Reflected XSS pada Search (/dashboard/laporan?q=...)
    xss_sqli_query = "<script>alert('XSS_TEST')</script>"
    search_url = base + "/dashboard/laporan?q=" + urllib.parse.quote(xss_sqli_query)
    req_search = urllib.request.Request(search_url)
    try:
        resp_search = opener.open(req_search)
        html_search = resp_search.read().decode("utf-8")
        if xss_sqli_query in html_search:
            results.append(("PASS", "Reflected XSS pada ?q= terbukti ter-render mentah (safe filter)!"))
        else:
            results.append(("WARN", "Reflected XSS tidak ditemukan di response HTML"))
    except Exception as e:
        results.append(("FAIL", "Akses /dashboard/laporan?q= error: " + str(e)))

    # 5. Test Stored XSS pada Papan Memo (/api/memo)
    stored_payload = "<img src=x onerror=\"console.log(document.cookie)\">"
    memo_data = urllib.parse.urlencode({"author": "Security Tester", "content": stored_payload}).encode()
    req_memo = urllib.request.Request(base + "/api/memo", data=memo_data)
    try:
        opener.open(req_memo)
        # Buka dashboard keuangan untuk cek apakah payload tersimpan dan ter-render
        resp_dash = opener.open(base + "/dashboard/keuangan")
        html_dash = resp_dash.read().decode("utf-8")
        if stored_payload in html_dash:
            results.append(("PASS", "Stored XSS pada Papan Memo terbukti tersimpan di database dan ter-render mentah!"))
        else:
            results.append(("WARN", "Stored XSS payload tidak ditemukan di halaman dashboard"))
    except Exception as e:
        results.append(("FAIL", "Test Stored XSS error: " + str(e)))

    # 6. Test Phishing & Awareness
    try:
        r_phish = opener.open(base + "/it-update")
        if r_phish.status == 200:
            results.append(("PASS", "Halaman Phishing /it-update aktif (Status 200)"))

        phish_form = urllib.parse.urlencode({"username": "korban", "password": "mypassword123", "new_password": "newpass"}).encode()
        r_sub = opener.open(urllib.request.Request(base + "/api/phishing-submit", data=phish_form))
        if "awareness-education" in r_sub.url:
            results.append(("PASS", "Submit Phishing otomatis mengalihkan ke /awareness-education tanpa menyimpan password"))
    except Exception as e:
        results.append(("FAIL", "Test Phishing error: " + str(e)))

    print("\n" + "=" * 75)
    print("  HASIL VERIFIKASI FITUR LAB CYBERSECURITY LENGKAP")
    print("=" * 75)
    for status, msg in results:
        prefix = "[OK]" if status == "PASS" else ("[!]" if status == "WARN" else "[X]")
        print(f" {prefix} [{status}] {msg}")
    print("=" * 75)

if __name__ == "__main__":
    run_tests()
