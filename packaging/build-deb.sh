#!/usr/bin/env bash
# Construit dist/kali-glass_<version>_all.deb
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VERSION="$(grep -m1 '^VERSION' "$ROOT/bin/kali-glass" | cut -d'"' -f2)"
PKG="$ROOT/build/kali-glass_${VERSION}_all"
rm -rf "$PKG"; mkdir -p "$PKG/DEBIAN" "$ROOT/dist"

install -d "$PKG/usr/share/kali-glass"
cp -r "$ROOT/wallpapers" "$ROOT/config" "$PKG/usr/share/kali-glass/"
install -Dm755 "$ROOT/bin/kali-glass"                       "$PKG/usr/bin/kali-glass"
install -Dm755 "$ROOT/apps/glass-center/glass-center"       "$PKG/usr/bin/glass-center"
install -Dm644 "$ROOT/apps/glass-center/glass-center.desktop" "$PKG/usr/share/applications/glass-center.desktop"
install -Dm644 "$ROOT/apps/glass-center/glass-center.svg"   "$PKG/usr/share/icons/hicolor/scalable/apps/glass-center.svg"
install -d "$PKG/usr/share/backgrounds/kali-glass"
cp "$ROOT"/wallpapers/*.jpg "$PKG/usr/share/backgrounds/kali-glass/"
install -Dm644 "$ROOT/README.md" "$PKG/usr/share/doc/kali-glass/README.md"
install -Dm644 "$ROOT/LICENSE"   "$PKG/usr/share/doc/kali-glass/copyright"

SIZE=$(du -sk "$PKG/usr" | cut -f1)
cat > "$PKG/DEBIAN/control" <<EOF
Package: kali-glass
Version: $VERSION
Section: x11
Priority: optional
Architecture: all
Installed-Size: $SIZE
Depends: python3, python3-gi, gir1.2-gtk-3.0, xfconf, picom, git, x11-xserver-utils
Recommends: plank | xfce4-docklike-plugin, fonts-inter, sassc, libglib2.0-dev-bin, libxml2-utils
Maintainer: ck526438-lgtm <ck526438-lgtm@users.noreply.github.com>
Homepage: https://github.com/ck526438-lgtm/kali-glass
Description: Bureau verre (glassmorphism) façon macOS pour Kali Linux
 Fonds d'écran en verre dépoli, flou en temps réel (picom dual_kawase),
 thème WhiteSur, barre du haut translucide, dock Plank avec effet loupe
 et l'application de réglages Glass Center.
EOF

cat > "$PKG/DEBIAN/postinst" <<'EOF'
#!/bin/sh
set -e
gtk-update-icon-cache -q /usr/share/icons/hicolor 2>/dev/null || true
update-desktop-database -q 2>/dev/null || true
echo ""
echo "  Kali Glass installé. Pour l'activer (sans sudo) :  kali-glass apply"
echo "  ou ouvre « Glass Center » depuis le menu."
echo ""
EOF
chmod 755 "$PKG/DEBIAN/postinst"

dpkg-deb --root-owner-group --build "$PKG" "$ROOT/dist/kali-glass_${VERSION}_all.deb"
echo "✓ dist/kali-glass_${VERSION}_all.deb"
