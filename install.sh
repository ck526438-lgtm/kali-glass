#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────
#  Kali Glass — installation en une commande
#  git clone https://github.com/ck526438-lgtm/kali-glass && cd kali-glass && ./install.sh
# ─────────────────────────────────────────────────────────
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PREFIX="/usr/share/kali-glass"
LIGHT=""
NO_APPLY=""

for arg in "$@"; do
  case "$arg" in
    --light) LIGHT="--light" ;;
    --no-apply) NO_APPLY=1 ;;
    -h|--help)
      echo "Usage : ./install.sh [--light] [--no-apply]"
      echo "  --light     démarre en mode clair"
      echo "  --no-apply  installe sans appliquer le thème"
      exit 0 ;;
  esac
done

c() { printf "\033[1;36m›\033[0m %s\n" "$*"; }
okk() { printf "\033[1;32m✓\033[0m %s\n" "$*"; }

if [[ $EUID -eq 0 ]]; then
  echo "Lance ce script en tant qu'utilisateur normal (il demandera sudo quand il faut)."
  exit 1
fi

cat <<'BANNER'

   ██╗  ██╗ █████╗ ██╗     ██╗     ██████╗ ██╗      █████╗ ███████╗███████╗
   ██║ ██╔╝██╔══██╗██║     ██║    ██╔════╝ ██║     ██╔══██╗██╔════╝██╔════╝
   █████╔╝ ███████║██║     ██║    ██║  ███╗██║     ███████║███████╗███████╗
   ██╔═██╗ ██╔══██║██║     ██║    ██║   ██║██║     ██╔══██║╚════██║╚════██║
   ██║  ██╗██║  ██║███████╗██║    ╚██████╔╝███████╗██║  ██║███████║███████║
   ╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝╚═╝     ╚═════╝ ╚══════╝╚═╝  ╚═╝╚══════╝╚══════╝
                    bureau verre façon macOS pour Kali Linux

BANNER

if [[ "${XDG_CURRENT_DESKTOP:-}" != *XFCE* ]]; then
  echo "⚠  Bureau détecté : ${XDG_CURRENT_DESKTOP:-inconnu}. Kali Glass est conçu pour XFCE (bureau par défaut de Kali)."
  read -rp "   Continuer quand même ? [o/N] " r; [[ "$r" =~ ^[oOyY]$ ]] || exit 1
fi

c "Installation des dépendances (sudo)…"
sudo apt-get update -qq
sudo apt-get install -y make picom git sassc libglib2.0-dev-bin libxml2-utils \
  python3-gi gir1.2-gtk-3.0 xfconf x11-xserver-utils x11-utils mpv ffmpeg
# plank a quitté Debian testing en 2026 : s'il manque, Kali Glass crée un dock avec un panneau XFCE
sudo apt-get install -y plank 2>/dev/null || sudo apt-get install -y xfce4-docklike-plugin 2>/dev/null || \
  echo "  (plank indisponible : dock XFCE de secours)"
sudo apt-get install -y fonts-inter 2>/dev/null || echo "  (police Inter indisponible, on garde la police actuelle)"
okk "Dépendances installées"

c "Copie des fichiers dans $PREFIX…"
sudo make -C "$HERE" install PREFIX=/usr >/dev/null
sudo gtk-update-icon-cache -q /usr/share/icons/hicolor 2>/dev/null || true
okk "Fichiers installés"

if [[ -z "$NO_APPLY" ]]; then
  kali-glass apply $LIGHT
  read -rp "Télécharger le pack de fonds d'écran ANIMÉS (vidéos, ~150 Mo en 4K) ? [o/N] " r
  if [[ "$r" =~ ^[oOyY]$ ]]; then kali-glass live download && kali-glass live set aurora; fi
  read -rp "Mettre aussi le fond Glass sur l'écran de connexion ? [o/N] " r
  if [[ "$r" =~ ^[oOyY]$ ]]; then sudo kali-glass login --wallpaper aurora; fi
fi

echo
okk "Kali Glass est installé !"
echo "   • Réglages graphiques : menu → « Glass Center »  (ou commande : glass-center)"
echo "   • Ligne de commande   : kali-glass --help"
echo "   • Fond animé          : kali-glass live set ~/Vidéos/ma-video.mp4"
echo "   • Tout annuler        : ./uninstall.sh"
echo
