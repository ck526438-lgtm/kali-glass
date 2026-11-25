# Changelog

Toutes les évolutions notables de Kali Glass. Format inspiré de [Keep a Changelog](https://keepachangelog.com/fr/1.1.0/), versions selon [SemVer](https://semver.org/lang/fr/).

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

[1.1.0]: https://github.com/ck526438-lgtm/kali-glass/compare/v1.0.0...v1.1.0
[1.0.0]: https://github.com/ck526438-lgtm/kali-glass/releases/tag/v1.0.0
