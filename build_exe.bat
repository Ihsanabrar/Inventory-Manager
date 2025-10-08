@echo off
title 🚀 Build Aplikasi Inventaris Manager

echo ============================================
echo  📦 Membuat file EXE dari project Python kamu
echo ============================================

REM Hapus folder build dan dist lama biar bersih
rmdir /s /q build
rmdir /s /q dist

REM Jalankan pyinstaller
pyinstaller --noconsole --onefile --icon=assets/icons/app.ico --add-data "db;db" --add-data "assets;assets" main.py

echo.
echo ✅ Build selesai! File EXE ada di folder dist
echo Tekan apa saja untuk keluar...
pause >nul
