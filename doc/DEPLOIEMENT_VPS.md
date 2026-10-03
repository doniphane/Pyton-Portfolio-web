# Déploiement sur un VPS

Guide pas à pas pour héberger le portfolio (Flask + Gunicorn) sur un VPS
Ubuntu/Debian. **Méthode recommandée : Docker** (section ci-dessous). La méthode
sans Docker (systemd + nginx natif) est conservée en fin de document.

## Méthode Docker (recommandée)

### 1. Prérequis

- VPS Ubuntu 22.04+ avec Docker et Docker Compose :
  ```bash
  sudo apt update && sudo apt install -y docker.io docker-compose-v2
  sudo systemctl enable --now docker
  ```
- Domaine pointant vers l'IP du VPS.

### 2. Récupérer le code et configurer

```bash
git clone <ton-repo> portfolio && cd portfolio
cp .env.example .env   # ou créer .env à la main
```

Contenu de `.env` (modèle fourni dans `.env.example`) :

```bash
SECRET_KEY=<clé aléatoire>      # python3 -c "import secrets; print(secrets.token_hex(32))"
SITE_URL=https://ton-domaine.fr # http://127.0.0.1 pour un test local
FLASK_DEBUG=0
```

Après toute modification de `.env`, recharger : `docker compose up -d`.

### 3. Lancer

```bash
docker compose up -d --build
```

Le service `web` (Flask/Gunicorn) tourne dans son conteneur ; le service
`nginx` (conteneur) reçoit le trafic sur les ports 80/443 et le transfère à
`web:8000`. En local, ouvrir `http://127.0.0.1` (port 80).

Utile en exploitation :

```bash
docker compose ps            # état des conteneurs
docker compose logs -f web   # logs de l'app
docker compose restart web   # redémarrer l'app
docker compose down          # tout arrêter
```

### 4. HTTPS avec Certbot (dans un conteneur)

```bash
mkdir -p certbot/conf certbot/www
docker run --rm -v $(pwd)/certbot/conf:/etc/letsencrypt \
  -v $(pwd)/certbot/www:/var/www/certbot \
  certbot/certbot certonly --webroot -w /var/www/certbot \
  -d ton-domaine.fr -d www.ton-domaine.fr
```

Puis décommenter le bloc HTTPS dans `nginx/default.conf` et :

```bash
docker compose restart nginx
```

### 5. Mettre à jour

```bash
git pull
docker compose up -d --build
```

### 6. Firewall

```bash
sudo ufw allow OpenSSH
sudo ufw allow 'Nginx Full'   # ou : 80 et 443
sudo ufw enable
```

---

## Méthode sans Docker (systemd + nginx natif)

### 1. Prérequis

- VPS Ubuntu 22.04+ avec un utilisateur non-root `noelson` (avec sudo).
- Un nom de domaine pointant vers l'IP du VPS (enregistrement A).

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3 python3-venv python3-pip nginx git certbot python3-certbot-nginx
```

### 2. Récupérer le code

```bash
cd /var/www
sudo git clone <ton-repo> portfolio
sudo chown -R noelson:noelson portfolio
cd portfolio
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

### 3. Variables d'environnement

Créer `/var/www/portfolio/.env` (permissions `chmod 600`) :

```bash
SECRET_KEY=<chaîne aléatoire de 64 caractères>
SITE_URL=https://ton-domaine.fr
PORT=8000
FLASK_DEBUG=0
```

Générer la clé : `python3 -c "import secrets; print(secrets.token_hex(32))"`.

### 4. Test rapide

```bash
set -a; source .env; set +a
.venv/bin/gunicorn wsgi:app --bind 127.0.0.1:$PORT --workers 2
```

Vérifier que le site répond sur `curl http://127.0.0.1:8000`, puis arrêter (Ctrl+C).

### 5. Service systemd (démarrage auto)

Créer `/etc/systemd/system/portfolio.service` :

```ini
[Unit]
Description=Portfolio Flask (Gunicorn)
After=network.target

[Service]
User=noelson
WorkingDirectory=/var/www/portfolio
EnvironmentFile=/var/www/portfolio/.env
ExecStart=/var/www/portfolio/.venv/bin/gunicorn wsgi:app --bind 127.0.0.1:8000 --workers 2
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now portfolio
sudo systemctl status portfolio
```

### 6. Nginx en reverse proxy

Créer `/etc/nginx/sites-available/portfolio` :

```nginx
server {
    listen 80;
    server_name ton-domaine.fr www.ton-domaine.fr;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    add_header X-Content-Type-Options nosniff;
    add_header X-Frame-Options DENY;
}
```

```bash
sudo ln -s /etc/nginx/sites-available/portfolio /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx
```

### 7. HTTPS (Let's Encrypt)

```bash
sudo certbot --nginx -d ton-domaine.fr -d www.ton-domaine.fr
```

Le certificat se renouvelle automatiquement.

### 8. Firewall

```bash
sudo ufw allow OpenSSH
sudo ufw allow 'Nginx Full'
sudo ufw enable
```

### 9. Mettre à jour l'app

```bash
cd /var/www/portfolio
git pull
.venv/bin/pip install -r requirements.txt
sudo systemctl restart portfolio
```

## Checklist avant de partager le lien

- [ ] `FLASK_DEBUG` n'est pas à `1`
- [ ] `SECRET_KEY` défini et aléatoire
- [ ] `https://` fonctionne, HTTP redirige vers HTTPS
- [ ] Gunicorn n'est pas exposé : dans `docker-compose.yml`, le service `web`
      utilise `expose` (port interne), seul `nginx` publie 80/443
- [ ] `docker compose ps` montre `web` et `nginx` « Up » après un reboot du VPS
