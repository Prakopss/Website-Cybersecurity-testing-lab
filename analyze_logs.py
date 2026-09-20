"""
=============================================================================
  PT Teknologi Aman Sejahtera – SOC Log Forensics Engine
  Modul Praktikum: Analisis Log untuk Deteksi Session Abuse & Hijacking
=============================================================================
  Tujuan:
  Menganalisis file web_access.log untuk menemukan indikasi Session Hijacking:
  1. Anomali Perubahan Alamat IP (Multiple IPs sharing same session_token)
  2. Anomali Perubahan User-Agent (Misal: Dari Browser ke cURL / Kali Linux)
  3. Aktivitas akses tidak wajar / pengambilalihan sesi aktif
=============================================================================
"""

import re
import os
import sys
from collections import defaultdict
from datetime import datetime

LOG_FILE = "web_access.log"

def parse_access_logs(log_path=LOG_FILE):
    if not os.path.exists(log_path):
        return []

    # Regex untuk log format umum:
    # [YYYY-MM-DD HH:MM:SS] IP: <ip> | <METHOD> <PATH> | Status: <status> | Cookie: session_token=<val>; User-Agent: <ua>
    pattern = re.compile(
        r"\[(?P<timestamp>[\d\- :]+)\]\s+IP:\s+(?P<ip>[\w\.\:]+)\s+\|\s+(?P<method>\w+)\s+(?P<path>\S+)\s+\|\s+Status:\s+(?P<status>\d+)\s+\|\s+(?P<details>.*)"
    )

    records = []
    with open(log_path, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            m = pattern.match(line)
            if not m:
                continue

            data = m.groupdict()
            details = data["details"]

            # Ekstraksi session_token & User-Agent
            token = ""
            user_agent = "unknown"

            if "Set-Cookie: session_token=" in details:
                # Format baris login
                token_match = re.search(r"session_token=([a-zA-Z0-9_\-]+)", details)
                if token_match:
                    token = token_match.group(1)
            elif "Cookie: session_token=" in details:
                # Format baris reguler
                token_match = re.search(r"session_token=([a-zA-Z0-9_\-]*)", details)
                if token_match:
                    token = token_match.group(1)

                ua_match = re.search(r"User-Agent:\s*(.*)$", details)
                if ua_match:
                    user_agent = ua_match.group(1).strip()

            records.append({
                "timestamp": data["timestamp"],
                "ip": data["ip"],
                "method": data["method"],
                "path": data["path"],
                "status": data["status"],
                "session_token": token,
                "user_agent": user_agent,
                "raw": line
            })

    return records


def analyze_session_abuse(records=None):
    if records is None:
        records = parse_access_logs()

    sessions = defaultdict(lambda: {
        "ips": set(),
        "user_agents": set(),
        "requests": [],
        "first_seen": "",
        "last_seen": ""
    })

    for r in records:
        token = r["session_token"]
        if not token:
            continue

        s = sessions[token]
        s["ips"].add(r["ip"])
        if r["user_agent"] != "unknown":
            s["user_agents"].add(r["user_agent"])
        s["requests"].append(r)
        if not s["first_seen"]:
            s["first_seen"] = r["timestamp"]
        s["last_seen"] = r["timestamp"]

    incidents = []

    for token, s in sessions.items():
        ip_count = len(s["ips"])
        ua_count = len(s["user_agents"])

        # Indikator 1: Satu token diakses dari > 1 alamat IP
        is_ip_anomaly = ip_count > 1
        # Indikator 2: Satu token diakses dari > 1 User-Agent (misal Browser beralih ke script/Kali)
        is_ua_anomaly = ua_count > 1

        if is_ip_anomaly or is_ua_anomaly:
            severity = "CRITICAL" if (is_ip_anomaly and is_ua_anomaly) else "HIGH"
            reasons = []
            if is_ip_anomaly:
                reasons.append(f"Terdeteksi {ip_count} Alamat IP berbeda menggunakan token yang sama: {list(s['ips'])}")
            if is_ua_anomaly:
                reasons.append(f"Terdeteksi {ua_count} User-Agent berbeda pada sesi yang sama: {list(s['user_agents'])}")

            incidents.append({
                "token": token,
                "severity": severity,
                "reasons": reasons,
                "ips": list(s["ips"]),
                "user_agents": list(s["user_agents"]),
                "total_requests": len(s["requests"]),
                "first_seen": s["first_seen"],
                "last_seen": s["last_seen"],
                "sample_evidence": s["requests"][:6]
            })

    return {
        "total_log_entries": len(records),
        "total_active_sessions": len(sessions),
        "total_compromised_sessions": len(incidents),
        "incidents": incidents
    }


def print_forensic_report():
    report = analyze_session_abuse()

    print("=" * 78)
    print("  PT TEKNOLOGI AMAN SEJAHTERA – SOC SESSION FORENSIC REPORT")
    print(f"  Waktu Analisis : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  Total Baris Log : {report['total_log_entries']}")
    print(f"  Total Token Sesi: {report['total_active_sessions']}")
    print(f"  Indikasi Pembajakan Sesi (Abuse): {report['total_compromised_sessions']}")
    print("=" * 78)

    if not report["incidents"]:
        print("\n[OK] Tidak terdeteksi anomali pada session_token (Semua sesi konsisten).")
    else:
        for idx, inc in enumerate(report["incidents"], 1):
            print(f"\n[ALERT #{idx}] Tingkat Bahaya : [{inc['severity']}]")
            print(f"  Token Sesi        : {inc['token']}")
            print(f"  Rentang Waktu     : {inc['first_seen']} s/d {inc['last_seen']}")
            print(f"  Total Permintaan  : {inc['total_requests']} requests")
            print("  Indikator Ancaman :")
            for r in inc["reasons"]:
                print(f"    - {r}")

            print("  Bukti Jejak Akses (Forensic Evidence):")
            for ev in inc["sample_evidence"]:
                print(f"    [{ev['timestamp']}] IP: {ev['ip']} | {ev['method']} {ev['path']} | UA: {ev['user_agent'][:45]}...")

    print("\n" + "=" * 78)
    print("  Rekomendasi Mitigasi Teknis:")
    print("  1. Aktifkan flag HttpOnly pada Set-Cookie untuk mencegah eksfiltrasi via XSS.")
    print("  2. Terapkan mekanisme Session Binding (Ikat token sesi ke IP / User-Agent hash).")
    print("  3. Lakukan Session Invalidation (Revoke token) saat terjadi perubahan IP drastis.")
    print("=" * 78)

if __name__ == "__main__":
    print_forensic_report()

