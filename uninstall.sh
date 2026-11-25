#!/usr/bin/env bash
# Kali Glass — désinstallation (restaure le bureau d'origine)
set -uo pipefail

if [[ $EUID -eq 0 ]]; then
  echo "Lance ce script en tant qu'utilisateur normal."
  exit 1
fi

if command -v kali-glass >/dev/null; then
  kali-glass restore
fi

if dpkg -s kali-glass >/dev/null 2>&1; then
  sudo apt-get remove -y kali-glass
else
  sudo rm -rf /usr/share/kali-glass /usr/share/backgrounds/kali-glass
  sudo rm -f /usr/bin/kali-glass /usr/bin/glass-center \
    /usr/share/applications/glass-center.desktop \
    /usr/share/icons/hicolor/scalable/apps/glass-center.svg
fi

if [[ -f /etc/lightdm/lightdm-gtk-greeter.conf.kali-glass.bak ]]; then
  sudo mv /etc/lightdm/lightdm-gtk-greeter.conf.kali-glass.bak /etc/lightdm/lightdm-gtk-greeter.conf
fi

rm -rf ~/.local/share/plank/themes/KaliGlass ~/.config/picom/kali-glass.conf ~/.config/gtk-3.0/kali-glass.css

echo "✓ Kali Glass désinstallé. Les thèmes WhiteSur restent dans ~/.themes (supprime-les si tu veux)."
echo "  Déconnecte-toi puis reconnecte-toi pour finir."
