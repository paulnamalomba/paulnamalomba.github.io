# Web servers & proxies: apache2, Nginx, and ngrok

<br>
Last updated: February 26, 2026<br>
Author: [Paul Namalomba](https://github.com/paulnamalomba)<br>
  - SESKA Computational Engineer<br>
  - SEAT Backend Developer<br>
  - Software Developer<br>
  - PhD Candidate (Civil Engineering Spec. Computational and Applied Mechanics)<br>
Contact: [kabwenzenamalomba@gmail.com](mailto:kabwenzenamalomba@gmail.com)<br>
Website: [paulnamalomba.github.io](https://paulnamalomba.github.io)<br>
<br>
[![Nginx](https://img.shields.io/badge/Server-Nginx-green.svg)](https://nginx.org/)
[![Apache](https://img.shields.io/badge/Server-Apache2-red.svg)](https://httpd.apache.org/)

## Overview

This guide covers exposing local applications through web servers and reverse proxies. It explains virtual host configuration (`.conf` files), forwarding local traffic through ngrok tunnels, and managing web server daemons on Unix systems.

## Contents

- [Web servers \& proxies: apache2, Nginx, and ngrok](#web-servers--proxies-apache2-nginx-and-ngrok)
  - [Overview](#overview)
  - [Contents](#contents)
  - [1. Configuration (Windows \& Linux)](#1-configuration-windows--linux)
    - [Linux environment architecture](#linux-environment-architecture)
  - [2. Writing basic Code/scripts (virtual hosts \& proxies)](#2-writing-basic-codescripts-virtual-hosts--proxies)
    - [Nginx: the reverse proxy](#nginx-the-reverse-proxy)
    - [Apache2: directory virtual hosting](#apache2-directory-virtual-hosting)
  - [3. Compile-time commands (syntax verification)](#3-compile-time-commands-syntax-verification)
    - [Nginx syntax tester](#nginx-syntax-tester)
    - [Apache2 syntax tester](#apache2-syntax-tester)
  - [4. Runtime commands (daemonization \& ngrok)](#4-runtime-commands-daemonization--ngrok)
    - [Service management (Nginx / Apache)](#service-management-nginx--apache)
    - [Ngrok: tunneling local environments to the public web](#ngrok-tunneling-local-environments-to-the-public-web)
  - [5. Debugging (502 bad gateway \& port conflicts)](#5-debugging-502-bad-gateway--port-conflicts)
    - [The infamous 502 bad gateway](#the-infamous-502-bad-gateway)
    - [Binding TCP port conflicts](#binding-tcp-port-conflicts)

---

## 1. Configuration (Windows & Linux)

Production-grade web servers are primarily hosted on Unix variants.

### Linux environment architecture

Nginx and Apache distribute their configurations across globally recognized directories (`/etc/nginx` and `/etc/apache2`).

```bash
# Ubuntu/Debian Installation
sudo apt update
sudo apt install nginx apache2

# Ngrok Installation via Snap
sudo snap install ngrok
ngrok config add-authtoken <your-auth-token>
```

**Directory Structure (The Debian Standard):**
Configurations are explicitly delineated between `sites-available` (staging) and `sites-enabled` (active via symbolic links).

- `/etc/nginx/sites-available/` -> Source of truth `.conf` files.
- `/etc/nginx/sites-enabled/` -> Active configurations.

---

## 2. Writing basic Code/scripts (virtual hosts & proxies)

Web server configurations act strictly as traffic controllers. They rarely execute application code directly, instead mapping public domains to local unprivileged ports (Reverse Proxying) or serving static HTML/CSS files directly from disk.

### Nginx: the reverse proxy

Nginx uses an asynchronous, event-driven architecture. The following configuration routes public HTTP traffic on port 80 to a Node.js or .NET API listening on port `5000`.

_Create `/etc/nginx/sites-available/api.example.com.conf`:_

```nginx
server {
    listen 80;
    server_name api.example.com;

    # Static File Routing (Frontend React/Angular)
    location / {
        root /var/www/html/frontend;
        index index.html;
        try_files $uri $uri/ /index.html; # Solves SPA routing 404s
    }

    # Reverse Proxying the Backend API
    location /api/ {
        proxy_pass http://localhost:5000/;

        # Enforce Forwarded Headers so backend knows the REAL client IP
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;

        # Handling WebSocket Persistence
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

### Apache2: directory virtual hosting

Apache's process-driven architecture handles heavy `.htaccess` runtime overriding, preferred heavily by complex PHP applications (like WordPress).

_Create `/etc/apache2/sites-available/app.example.com.conf`:_

```apache
<VirtualHost *:80>
    ServerName app.example.com
    DocumentRoot /var/www/html/application

    <Directory /var/www/html/application>
        Options Indexes FollowSymLinks
        AllowOverride All   # Enables runtime .htaccess routing overrides
        Require all granted
    </Directory>

    ErrorLog ${APACHE_LOG_DIR}/app_error.log
    CustomLog ${APACHE_LOG_DIR}/app_access.log combined
</VirtualHost>
```

---

## 3. Compile-time commands (syntax verification)

These commands check server configuration syntax; they do not compile binary code. Check the configuration before restarting a daemon. An invalid configuration can prevent the daemon from starting and take its virtual hosts offline.

### Nginx syntax tester

```bash
# Symlink your configuration to enabled
sudo ln -s /etc/nginx/sites-available/api.example.com.conf /etc/nginx/sites-enabled/

# CRITICAL: Verify syntax WITHOUT disrupting active traffic
sudo nginx -t

# Outputs:
# nginx: the configuration file /etc/nginx/nginx.conf syntax is ok
# nginx: configuration file /etc/nginx/nginx.conf test is successful
```

### Apache2 syntax tester

```bash
# Enable the site module natively
sudo a2ensite app.example.com.conf

# Verify Syntax
sudo apache2ctl configtest
```

---

## 4. Runtime commands (daemonization & ngrok)

Execution involves signaling the system supervisor (`systemd`) to reload the configuration into memory.

### Service management (Nginx / Apache)

Reloading gracefully switches configurations without dropping active client connections.

```bash
# Graceful daemon reload after successful syntax checks
sudo systemctl reload nginx
sudo systemctl reload apache2

# Full restart (Forces TCP disconnections - Use cautiously)
sudo systemctl restart nginx
```

### Ngrok: tunneling local environments to the public web

Exposing local Webhooks (Stripe, GitHub) or demonstrating APIs to remote teams requires bypassing NAT routers. `ngrok` establishes an aggressive persistent outward tunnel to remote infrastructure, mapping their public URL directly back to your local port.

```bash
# Expose your local Node.js API sitting on port 5000 directly to the internet
ngrok http 5000

# Expected output provides a live Forwarding URL:
# Forwarding  https://abc-123.ngrok-free.app -> http://localhost:5000
```

_Note for APIs:_ Ensure the backend strictly accepts `Host: localhost` overrides when accessed via ngrok, or configure ngrok to spoof the host header: `ngrok http 5000 --host-header="localhost:5000"`.

---

## 5. Debugging (502 bad gateway & port conflicts)

Reverse proxies orchestrating web traffic introduce significant complexity. Understanding the standard error codes quickly isolates whether the problem sits at the network layer or the application codebase.

### The infamous 502 bad gateway

If Nginx returns a `502`, the Nginx daemon correctly caught the public internet request, attempted to `proxy_pass` it to your internal application at `localhost:5000`, and hit a literal wall.

- **The Fix:** The internal application is dead. Nginx is completely innocent. Ensure the backend (Node, .NET, Python) is actually running and listening on port `5000`.
- **The Log Investigation:**
  ```bash
  sudo tail -f /var/log/nginx/error.log
  # Expected trace: "connect() failed (111: Connection refused) while connecting to upstream"
  ```

### Binding TCP port conflicts

You cannot run Apache2 and Nginx concurrently on port 80 or 443 without nested reverse proxying. Attempting to start the second service triggers a port binding failure.

- **The Fix:** Identify which daemon stole your ports natively via the kernel networking tables.
  ```bash
  sudo netstat -tulpn | grep :80
  # Output specifically tags the PID and process name holding the port HOSTAGE.
  ```
