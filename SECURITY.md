# Sécurité

## Versions prises en charge

| Version | Prise en charge |
|---|---|
| 1.1.x | ✅ |
| < 1.1 | ❌ |

## Signaler une vulnérabilité

Ne publie pas d'issue publique. Utilise **Security → Report a vulnerability** sur le dépôt GitHub (signalement privé).
Réponse sous 7 jours.

## Ce que fait Kali Glass

- Aucune collecte de données, aucune connexion réseau hors `kali-glass install-themes`, qui clone les dépôts WhiteSur de github.com/vinceliuice.
- Seule `kali-glass login` demande les droits root, pour écrire le fond de LightDM. Une copie de `lightdm-gtk-greeter.conf` est gardée en `.kali-glass.bak`.
- Les paquets publiés sont accompagnés d'un fichier `SHA256SUMS` :

```bash
sha256sum -c SHA256SUMS
```
