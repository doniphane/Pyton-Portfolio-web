# Sécurité de l'application

État du code après audit, et ce qu'il faut vérifier avant/pendant la mise en production.

## Points déjà acquis dans le code

- **Pas de base de données** : catalogue en Python (`app/data/projects.py`), donc pas
  d'injection SQL possible.
- **Templates Jinja2 auto-échappés** : toutes les données affichées (titres,
  descriptions…) sont échappées par défaut, protection XSS côté serveur.
- **Filtres validés côté serveur** (`app/routes.py::_filters_from_request`) : une
  valeur inconnue retombe sur `all`, l'URL ne peut pas casser la page.
- **Pas de secret dans le code** : `SECRET_KEY` et `SITE_URL` viennent de
  l'environnement. La valeur par défaut `dev-secret-change-me` est un piège de
  développement — **il faut toujours définir `SECRET_KEY` en production**.
- **Debug désactivé en production** : `FLASK_DEBUG` absent ⇒ `TEMPLATES_AUTO_RELOAD`
  off et cache des statiques activé. Ne jamais lancer avec `FLASK_DEBUG=1` sur un
  serveur exposé (le debugger Werkzeug permet l'exécution de code à distance).
- **Pages d'erreur 404/500 dédiées** : pas de traceback exposé au visiteur.

## À faire au déploiement

1. **`SECRET_KEY` robuste** :
   ```bash
   python3 -c "import secrets; print(secrets.token_hex(32))"
   ```
   Mettre le résultat dans un fichier `.env` (jamais commité) ou l'environnement.

2. **Reverse proxy Nginx devant Gunicorn** (ne jamais exposer Gunicorn directement).
   Dans le setup Docker du repo, Nginx tourne en conteneur et `web` n'est pas
   publié sur l'hôte — respecter cette séparation.

3. **HTTPS obligatoire** : certificat Let's Encrypt via Certbot. Rediriger HTTP → HTTPS.

4. **En-têtes de sécurité** dans le bloc Nginx :
   ```nginx
   add_header X-Content-Type-Options nosniff;
   add_header X-Frame-Options DENY;
   add_header Referrer-Policy strict-origin-when-cross-origin;
   ```

5. **Firewall** : seuls les ports 22 (SSH), 80 et 443 ouverts (`ufw`).

6. **Utilisateur non-root** pour faire tourner l'app et le service.

7. **Dépendances à jour** : relancer `pip install -U -r requirements.txt` avant
   chaque déploiement et surveiller les CVE de Flask/Werkzeug/gunicorn.

8. **Limitation de requêtes éventuelle** (fail2ban ou `limit_req` Nginx) si le
   site commence à recevoir du trafic.
