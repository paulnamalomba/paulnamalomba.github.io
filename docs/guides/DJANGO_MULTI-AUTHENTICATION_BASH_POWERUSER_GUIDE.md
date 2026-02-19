# DJANGO Multi-Authentication PowerUser Guide (Bash)

**Last updated**: December 09, 2025<br>
**Author**: [Paul Namalomba](https://github.com/paulnamalomba)<br>
  - SESKA Computational Engineer<br>
  - SEAT Backend Developer<br>
  - Software Developer<br>
  - PhD Candidate (Civil Engineering Spec. Computational and Applied Mechanics)<br>
**Contact**: [kabwenzenamalomba@gmail.com](kabwenzenamalomba@gmail.com)<br>
**Website**: [paulnamalomba.github.io](https://paulnamalomba.github.io)<br>
<br>

[![Framework](https://img.shields.io/badge/Django-4.x-blue.svg)](https://docs.djangoproject.com/en/4.2/)
[![License: MIT](https://img.shields.io/badge/License-MIT-gray.svg)](https://opensource.org/licenses/MIT)

## Overview

This guide focuses on Linux and Bash workflows for deploying and operating Django applications that implement multiple authentication mechanisms. You will automate environment setup, systemd services, reverse proxy configuration (Nginx), TLS via Certbot, and basic diagnostics for multi-provider authentication.

## Contents

- [DJANGO Multi-Authentication PowerUser Guide (Bash)](#django-multi-authentication-poweruser-guide-bash)
  - [Overview](#overview)
  - [Contents](#contents)
  - [Quickstart](#quickstart)
    - [System Preparation](#system-preparation)
    - [Project Bootstrap](#project-bootstrap)
  - [Key Concepts](#key-concepts)
    - [Process Layout](#process-layout)
    - [Separation of Concerns](#separation-of-concerns)
  - [Configuration and Best Practices](#configuration-and-best-practices)
    - [Environment Files](#environment-files)
    - [systemd and Nginx](#systemd-and-nginx)
  - [Security Considerations](#security-considerations)
    - [Permissions and Ownership](#permissions-and-ownership)
    - [TLS and HSTS](#tls-and-hsts)
  - [Examples](#examples)
    - [Example 1: Bootstrap Django Project](#example-1-bootstrap-django-project)
    - [Example 2: Configure systemd Service](#example-2-configure-systemd-service)
    - [Example 3: Nginx and Certbot](#example-3-nginx-and-certbot)
    - [Example 4: Auth Diagnostics Script](#example-4-auth-diagnostics-script)
  - [Troubleshooting](#troubleshooting)
    - [Common Deployment Issues](#common-deployment-issues)
    - [Log Inspection](#log-inspection)
  - [Performance and Tuning](#performance-and-tuning)
    - [Gunicorn and Nginx Tuning](#gunicorn-and-nginx-tuning)
  - [References and Further Reading](#references-and-further-reading)

---

## Quickstart

### System Preparation

```bash
# Update packages
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install -y python3 python3-venv python3-pip git nginx certbot python3-certbot-nginx
```

### Project Bootstrap

```bash
PROJECT_ROOT=/opt/django-multi-auth
sudo mkdir -p "$PROJECT_ROOT"
sudo chown "$USER":"$USER" "$PROJECT_ROOT"

cd "$PROJECT_ROOT"

git clone https://github.com/your-org/django-multi-auth.git .

python3 -m venv .venv
source .venv/bin/activate

pip install --upgrade pip
pip install -r requirements.txt

python manage.py migrate
python manage.py collectstatic --noinput
```

---

## Key Concepts

### Process Layout

- **Gunicorn/Uvicorn**: WSGI/ASGI server hosting Django.
- **systemd Service**: Manages Django process, restarts on failure, runs under restricted user.
- **Nginx**: Reverse proxy terminating TLS and forwarding HTTP to Gunicorn.

### Separation of Concerns

- Keep Django settings free of environment-specific paths and secrets.
- Use `/etc/django/<project>.env` for environment variables.
- Use `systemd` to source env files before starting services.

---

## Configuration and Best Practices

### Environment Files

`/etc/django/django-multi-auth.env`:

```bash
DJANGO_SETTINGS_MODULE=config.settings.production
DJANGO_SECRET_KEY=<strong-secret>
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=django.example.com

OAUTH_GOOGLE_CLIENT_ID=<client-id>
OAUTH_GOOGLE_CLIENT_SECRET=<client-secret>
JWT_SIGNING_KEY=<jwt-signing-key>
```

```bash
sudo mkdir -p /etc/django
sudo nano /etc/django/django-multi-auth.env
sudo chmod 600 /etc/django/django-multi-auth.env
sudo chown root:root /etc/django/django-multi-auth.env
```

### systemd and Nginx

`/etc/systemd/system/django-multi-auth.service`:

```ini
[Unit]
Description=Django multi-auth application
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/opt/django-multi-auth
EnvironmentFile=/etc/django/django-multi-auth.env
ExecStart=/opt/django-multi-auth/.venv/bin/gunicorn \
          --workers 3 \
          --bind unix:/run/django-multi-auth.sock \
          config.wsgi:application
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now django-multi-auth
sudo systemctl status django-multi-auth
```

Nginx site config `/etc/nginx/sites-available/django-multi-auth`:

```nginx
server {
    listen 80;
    server_name django.example.com;

    location /static/ {
        alias /opt/django-multi-auth/static/;
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:/run/django-multi-auth.sock;
    }
}
```

```bash
sudo ln -s /etc/nginx/sites-available/django-multi-auth /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

---

## Security Considerations

### Permissions and Ownership

- Run Django under a non-privileged user (e.g. `www-data`).
- Ensure project files are readable by the app user, writable only where necessary (media, logs).
- Keep env files readable only by root.

### TLS and HSTS

Use Certbot to obtain and renew certificates:

```bash
sudo certbot --nginx -d django.example.com --redirect --agree-tos -m admin@django.example.com
```

Ensure HSTS is enabled in Nginx:

```nginx
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
```

---

## Examples

### Example 1: Bootstrap Django Project

```bash
#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT=/opt/django-multi-auth
REPO_URL="https://github.com/your-org/django-multi-auth.git"

sudo mkdir -p "$PROJECT_ROOT"
sudo chown "$USER":"$USER" "$PROJECT_ROOT"
cd "$PROJECT_ROOT"

if [ ! -d .git ]; then
  git clone "$REPO_URL" .
else
  git pull --ff-only
fi

python3 -m venv .venv
source .venv/bin/activate

pip install --upgrade pip
pip install -r requirements.txt

python manage.py migrate
python manage.py collectstatic --noinput
```

### Example 2: Configure systemd Service

```bash
#!/usr/bin/env bash
set -euo pipefail

SERVICE_FILE=/etc/systemd/system/django-multi-auth.service

sudo tee "$SERVICE_FILE" > /dev/null << 'EOF'
[Unit]
Description=Django multi-auth application
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/opt/django-multi-auth
EnvironmentFile=/etc/django/django-multi-auth.env
ExecStart=/opt/django-multi-auth/.venv/bin/gunicorn \
          --workers 3 \
          --bind unix:/run/django-multi-auth.sock \
          config.wsgi:application
Restart=on-failure

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable --now django-multi-auth
sudo systemctl status django-multi-auth --no-pager
```

### Example 3: Nginx and Certbot

```bash
#!/usr/bin/env bash
set -euo pipefail

DOMAIN=django.example.com

sudo tee /etc/nginx/sites-available/django-multi-auth > /dev/null << EOF
server {
    listen 80;
    server_name $DOMAIN;

    location /static/ {
        alias /opt/django-multi-auth/static/;
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:/run/django-multi-auth.sock;
    }
}
EOF

sudo ln -sf /etc/nginx/sites-available/django-multi-auth /etc/nginx/sites-enabled/django-multi-auth
sudo nginx -t
sudo systemctl reload nginx

sudo certbot --nginx -d "$DOMAIN" --redirect --agree-tos -m admin@$DOMAIN
```

### Example 4: Auth Diagnostics Script

```bash
#!/usr/bin/env bash
set -euo pipefail

BASE_URL="https://django.example.com"

endpoints=(
  "/accounts/login/"
  "/accounts/google/login/"
  "/accounts/azure/login/"
  "/api/auth/token/"
  "/saml/login/"
)

for path in "${endpoints[@]}"; do
  url="$BASE_URL$path"
  code=$(curl -s -o /dev/null -w "%{http_code}" "$url")
  echo "$code $url"
  sleep 1
done
```

---

## Troubleshooting

### Common Deployment Issues

- **502 Bad Gateway**: Gunicorn not running or socket path mismatch.
- **404 on static files**: Nginx `alias` directive or `collectstatic` not configured.
- **TLS handshake errors**: Incorrect certificate chain or hostname.

### Log Inspection

```bash
# Django app logs
sudo journalctl -u django-multi-auth -f

# Nginx access and error logs
sudo tail -f /var/log/nginx/access.log /var/log/nginx/error.log
```

---

## Performance and Tuning

### Gunicorn and Nginx Tuning

- Set Gunicorn workers to `(2 * CPU) + 1` as a starting point.
- Use `--max-requests` and `--max-requests-jitter` to mitigate memory leaks.
- Enable Gzip compression and HTTP/2 in Nginx.
- Prefer Unix domain sockets over TCP for local proxying.

---

## References and Further Reading

- Django Deployment: https://docs.djangoproject.com/en/4.2/howto/deployment/
- Gunicorn: https://docs.gunicorn.org/en/stable/
- Nginx: https://nginx.org/en/docs/
- Certbot: https://certbot.eff.org/
