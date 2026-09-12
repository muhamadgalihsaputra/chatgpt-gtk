#!/usr/bin/env bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BIN_DIR="$HOME/.local/bin"
APP_DIR="$HOME/.local/share/applications"
ICON_BASE="$HOME/.local/share/icons/hicolor"

echo "==> Installing ChatGPT GTK into user environment..."

mkdir -p "$BIN_DIR"
mkdir -p "$APP_DIR"
mkdir -p "$ICON_BASE/32x32/apps"
mkdir -p "$ICON_BASE/128x128/apps"
mkdir -p "$ICON_BASE/256x256/apps"

# Clean up any old duplicate entries or old SVG overrides
rm -f "$ICON_BASE/scalable/apps/chatgpt-gtk.svg"
rm -f "$APP_DIR/io.github.chatgpt_gtk.desktop.desktop"

# Link launcher script into ~/.local/bin
ln -sf "$SCRIPT_DIR/bin/chatgpt-gtk" "$BIN_DIR/chatgpt-gtk"

# Install PNG icons from assets
if [ -f "$SCRIPT_DIR/assets/icon.png" ]; then
    cp "$SCRIPT_DIR/assets/icon.png" "$ICON_BASE/32x32/apps/chatgpt-gtk.png"
fi
if [ -f "$SCRIPT_DIR/assets/chatgpt-gtk-128.png" ]; then
    cp "$SCRIPT_DIR/assets/chatgpt-gtk-128.png" "$ICON_BASE/128x128/apps/chatgpt-gtk.png"
fi
if [ -f "$SCRIPT_DIR/assets/chatgpt-gtk-256.png" ]; then
    cp "$SCRIPT_DIR/assets/chatgpt-gtk-256.png" "$ICON_BASE/256x256/apps/chatgpt-gtk.png"
fi

# Fix local hicolor index.theme if incomplete
if [ -f /usr/share/icons/hicolor/index.theme ]; then
    cp /usr/share/icons/hicolor/index.theme "$ICON_BASE/index.theme"
fi

# Install desktop file (single entry)
sed "s|Exec=.*|Exec=$BIN_DIR/chatgpt-gtk %U|g" "$SCRIPT_DIR/chatgpt-gtk.desktop" > "$APP_DIR/chatgpt-gtk.desktop"

# Update desktop and icon caches
if command -v update-desktop-database >/dev/null 2>&1; then
    update-desktop-database "$APP_DIR" || true
fi
if command -v gtk-update-icon-cache >/dev/null 2>&1; then
    gtk-update-icon-cache -f -t "$ICON_BASE" 2>/dev/null || true
fi

echo "==> Selesai! Icon dan desktop entry ChatGPT sudah terpasang rapi di GNOME."
