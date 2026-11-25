# Contribuer à Kali Glass

Merci de ton intérêt ! Les contributions sont les bienvenues : correctifs, nouveaux fonds d'écran, traductions, compatibilité avec d'autres bureaux.

## Préparer l'environnement

```bash
git clone https://github.com/ck526438-lgtm/kali-glass.git
cd kali-glass
pip install --user pytest ruff      # ou : sudo apt install python3-pytest
sudo apt install shellcheck
make test                            # lint + tests
```

Les tests n'ont pas besoin d'un bureau : `xfconf-query` est simulé (`tests/mock/`).

## Tester sur un vrai bureau

Depuis le dépôt, sans rien installer :

```bash
./bin/kali-glass -v apply --no-themes
./apps/glass-center/glass-center
./bin/kali-glass restore
```

## Règles

- Une modification de réglage passe toujours par `xf_set` / `xf_set_array` : la valeur d'origine est ainsi sauvegardée et `restore` reste exact.
- Chaque nouvelle commande a un test dans `tests/test_cli.py` et une entrée dans la page man et l'autocomplétion.
- Messages utilisateur en français, clairs, avec la solution quand quelque chose manque.
- `make test` doit passer avant d'ouvrir une pull request.
- Ajoute une ligne dans `CHANGELOG.md`, section « Non publié ».

## Publier une version (mainteneurs)

1. Change `VERSION` dans `bin/kali-glass`.
2. Mets à jour `CHANGELOG.md`, la page man et le fichier AppStream.
3. Pousse sur `main` : la CI teste, construit le .deb et publie la release `vX.Y.Z`.
