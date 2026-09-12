# ChatGPT GTK

Aplikasi desktop Linux mandiri untuk web ChatGPT (`chatgpt.com`), dibuat menggunakan **GTK4**, **Libadwaita**, dan **WebKitGTK 6.0**.

Didesain khusus untuk lingkungan desktop GNOME:
- **100% Native GNOME CSD**: Tombol window (`close,minimize,maximize:`) patuh di sebelah kiri, mengikuti tema sistem (`MacTahoe-Dark`).
- **System Tray (StatusNotifierItem & Dbusmenu)**: Terintegrasi dengan GNOME top bar (`appindicatorsupport`). Close window langsung me-minimize ke tray tanpa mematikan sesi background.
- **Hemat Resource**: Zero Electron, langsung memanfaatkan runtime shared library GTK4 & WebKitGTK sistem (~350–450 MB RAM vs 1.2+ GB Electron).
- **Persistent Session & 2FA Ready**: Login akun ChatGPT resmi (Free/Plus/Team) tersimpan permanen di `~/.local/share/chatgpt-gtk`. Dilengkapi penyesuaian User-Agent & Cookie Policy agar lolos verifikasi Cloudflare Turnstile dan 2FA/MFA.
- **OAuth Popup Support**: Mendukung popup autentikasi Google / Apple Login.
- **Keyboard Shortcuts**:
  - `Ctrl + +` / `Ctrl + =`: Zoom In
  - `Ctrl + -`: Zoom Out
  - `Ctrl + 0`: Reset Zoom
  - `Ctrl + R`: Reload halaman
  - `Alt + Left`: Kembali (Back)
  - `Alt + Right`: Maju (Forward)
  - `Ctrl + W`: Sembunyikan ke System Tray
  - `F11`: Toggle Fullscreen
  - `F12`: Web Inspector / DevTools
  - `Ctrl + Q`: Keluar aplikasi

## Cara Menjalankan

Langsung jalankan via script:
```bash
./run.sh
```

Atau pasang ke GNOME Application Launcher:
```bash
./install.sh
```
Setelah di-install, aplikasi akan muncul di daftar aplikasi GNOME dengan nama **ChatGPT**.

## Struktur Direktori

- `bin/chatgpt-gtk`: Executable launcher (dengan symlink auto-resolver)
- `chatgpt_gtk/app.py`: Window utama Libadwaita + WebKitGTK 6.0
- `chatgpt_gtk/tray.py`: Integrasi system tray StatusNotifierItem via D-Bus
- `assets/`: Asset icon resmi
- `chatgpt-gtk.desktop`: Desktop launcher untuk GNOME
- `install.sh`: Script instalasi ke `~/.local`
