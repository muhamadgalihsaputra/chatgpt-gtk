#!/usr/bin/env bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BIN_DIR="$HOME/.local/bin"
APP_DIR="$HOME/.local/share/applications"
ICON_DIR="$HOME/.local/share/icons/hicolor/scalable/apps"

echo "==> Installing ChatGPT GTK into user environment..."

mkdir -p "$BIN_DIR"
mkdir -p "$APP_DIR"
mkdir -p "$ICON_DIR"

# Link launcher script into ~/.local/bin
ln -sf "$SCRIPT_DIR/bin/chatgpt-gtk" "$BIN_DIR/chatgpt-gtk"

# Install icon
cp "$SCRIPT_DIR/assets/chatgpt-gtk.svg" "$ICON_DIR/chatgpt-gtk.svg"

# Install desktop file (pointing to ~/.local/bin/chatgpt-gtk)
sed "s|Exec=.*|Exec=$BIN_DIR/chatgpt-gtk %u|g" "$SCRIPT_DIR/chatgpt-gtk.desktop" > "$APP_DIR/chatgpt-gtk.desktop"

# Update desktop and icon caches
if command -v update-desktop-database >/dev/null 2>&1; then
    update-desktop-database "$APP_DIR" || true
fi
if command -v gtk-update-icon-cache >/dev/null 2>&1; then
    gtk-update-icon-cache -f -t "$HOME/.local/share/icons/hicolor" 2>/dev/null || true
fi

echo "==> Selesai! Aplikasi 'ChatGPT' sekarang sudah terpasang di GNOME App Launcher."
echo "    Lu bisa langsung cari 'ChatGPT' di menu aplikasi atau ketik 'chatgpt-gtk' di terminal."
