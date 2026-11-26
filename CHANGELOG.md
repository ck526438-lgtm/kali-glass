# Changelog

Toutes les évolutions notables de Kali Glass. Format inspiré de [Keep a Changelog](https://keepachangelog.com/fr/1.1.0/), versions selon [SemVer](https://semver.org/lang/fr/).

## [1.2.0] — 2026-11-26

### Ajouté
- **Fonds d'écran animés** : n'importe quelle vidéo (MP4, WebM, MKV, MOV, AVI, GIF), jusqu'en 4K, jouée en boucle derrière les fenêtres sur tous les écrans (`kali-glass live set`).
- **Pack officiel de 4 fonds animés « verre »** (Aurora, Ocean, Sunset, Midnight) en 4K et 1080p, boucles de 20 s sans coupure, générés par `tools/generate_live.py` et publiés avec chaque release (`kali-glass live download`, qualité choisie selon l'écran).
- Lecteur `kali-glass-live` (mpv incrusté dans une fenêtre bureau), décodage matériel si disponible, repli logiciel automatique.
- Pause automatique quand une fenêtre est en plein écran ou agrandie, et sur batterie (désactivables).
- Clic droit sur le fond animé : Glass Center, terminal, pause, arrêt.
- Options son, vitesse (0.1 à 4), bibliothèque perso (`live add`), lecture depuis une URL.
- Page **Fonds animés** dans Glass Center : galerie avec miniatures, ajout de vidéo, téléchargement du pack, options.
- `doctor` vérifie mpv, ffmpeg et xprop.
- Aperçu animé dans le README.

### Modifié
- Choisir un fond fixe ou lancer `restore` arrête le fond animé et rallume le bureau XFCE.
- La CI rend les vidéos 4K en parallèle (une machine par vidéo) uniquement lors d'une release.
- Dépendances : `mpv` et `x11-utils` ajoutés, `ffmpeg` recommandé.

## [1.1.0] — 2026-11-25

### Ajouté
- `kali-glass doctor` : diagnostic complet (session, picom, accélération 3D, dock, thèmes, polices) avec la solution à chaque problème.
- Page **Diagnostic** dans Glass Center.
- Journal des opérations dans `~/.cache/kali-glass/kali-glass.log` (rotation automatique).
- Option `-v/--verbose` pour afficher chaque commande exécutée.
- Pages man `kali-glass(1)` et `glass-center(1)`, autocomplétion bash.
- Métadonnées AppStream (Glass Center visible dans les logithèques).
- `Makefile` (`make test`, `make deb`, `make install`).
- Suite de tests (pytest, xfconf simulé) et lint (ruff, shellcheck) en CI.
- `SHA256SUMS` publié avec chaque release.
- Variable `KALI_GLASS_DOCK` (`auto`, `plank`, `xfce`) pour choisir le moteur du dock.
- README en anglais, guide de contribution, politique de sécurité, modèles d'issues.

### Modifié
- Valeurs hors limites refusées (`blur` 0–20, `panel-opacity` 0–100).
- Couleurs désactivées hors terminal ou avec `NO_COLOR`.
- Le paquet .deb et `install.sh` passent par `make install` (une seule liste de fichiers).

### Corrigé
- Restauration des tableaux d'entiers xfconf (liste des panneaux) avec le bon type.

## [1.0.0] — 2026-11-25

### Ajouté
- 6 fonds d'écran 4K en verre dépoli.
- Flou picom `dual_kawase`, coins arrondis, ombres.
- Thème WhiteSur, boutons façon macOS, barre du haut translucide.
- Dock Plank « KaliGlass », dock XFCE de secours si Plank est absent.
- CLI `kali-glass` et appli GTK Glass Center.
- Fond dynamique selon l'heure, fond de l'écran de connexion, restauration exacte.
- Paquet .deb et release automatique.

[1.2.0]: https://github.com/ck526438-lgtm/kali-glass/compare/v1.1.0...v1.2.0
[1.1.0]: https://github.com/ck526438-lgtm/kali-glass/compare/v1.0.0...v1.1.0
[1.0.0]: https://github.com/ck526438-lgtm/kali-glass/releases/tag/v1.0.0
