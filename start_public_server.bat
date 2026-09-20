@echo off
title CyberLab - PT Teknologi Aman Sejahtera (Public Server)
echo ======================================================================
echo   PT TEKNOLOGI AMAN SEJAHTERA - LIVE CYBERSECURITY LAB (PUBLIC)
echo ======================================================================
echo.
echo [1/2] Memastikan dependensi Python terpasang...
pip install -r requirements.txt -q

echo.
echo [2/2] Menjalankan Server Web Waitress dan Terowongan Cloudflare (HTTPS)...
echo.
echo Server lokal aktif di port 5000.
echo Cloudflare Tunnel sedang membuat URL Publik HTTPS resmi...
echo.
echo ======================================================================
echo BAGIKAN URL DENGAN AKHIRAN .trycloudflare.com DI BAWAH INI KE MAHASISWA:
echo ======================================================================
echo.

start /b python app.py
timeout /t 2 >nul
cloudflared tunnel --url http://127.0.0.1:5000
pause

