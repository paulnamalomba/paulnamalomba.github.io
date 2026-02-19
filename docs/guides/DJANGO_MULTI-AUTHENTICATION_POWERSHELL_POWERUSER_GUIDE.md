# DJANGO Multi-Authentication PowerUser Guide (PowerShell)

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

This guide targets PowerShell power users who operate and automate Django applications that implement multiple authentication mechanisms (username/password, OAuth2/OIDC, SAML, and MFA). It focuses on Windows-based operational tasks: provisioning environments, managing secrets and certificates, configuring reverse proxies, deploying Django services, and running diagnostics against authentication flows.

## Contents

- [DJANGO Multi-Authentication PowerUser Guide (PowerShell)](#django-multi-authentication-poweruser-guide-powershell)
  - [Overview](#overview)
  - [Contents](#contents)
  - [Quickstart](#quickstart)
    - [Prerequisites](#prerequisites)
    - [Core Automation Workflow](#core-automation-workflow)
  - [Key Concepts](#key-concepts)
    - [Authentication Layers](#authentication-layers)
    - [Identity Providers](#identity-providers)
  - [Configuration and Best Practices](#configuration-and-best-practices)
    - [Environment and Secrets](#environment-and-secrets)
    - [Reverse Proxy and TLS](#reverse-proxy-and-tls)
  - [Security Considerations](#security-considerations)
    - [Secrets and Certificates](#secrets-and-certificates)
    - [Audit and Compliance](#audit-and-compliance)
  - [Examples](#examples)
    - [Example 1: Provision Django Environment](#example-1-provision-django-environment)
    - [Example 2: Configure Environment for Multi-Auth](#example-2-configure-environment-for-multi-auth)
    - [Example 3: Automate TLS with Certbot on WSL](#example-3-automate-tls-with-certbot-on-wsl)
    - [Example 4: End-to-End Auth Health Check](#example-4-end-to-end-auth-health-check)
  - [Troubleshooting](#troubleshooting)
    - [Common Operational Issues](#common-operational-issues)
    - [Diagnostic Commands](#diagnostic-commands)
  - [Performance and Tuning](#performance-and-tuning)
    - [Scaling and Observability](#scaling-and-observability)
  - [References and Further Reading](#references-and-further-reading)

---

## Quickstart

### Prerequisites

- Windows 10/11 with PowerShell 7 or later
- Python 3.10+ installed and available in `PATH`
- Git installed
- Optional: WSL2 with an Ubuntu distribution for Linux-native tooling (Certbot, Nginx)
- Administrative privileges for service and firewall configuration

### Core Automation Workflow

1. **Clone the Django project** (with multi-auth already wired in):

```powershell
$projectRoot = "C:\Projects\django-multi-auth"
if (-not (Test-Path $projectRoot)) {
    git clone https://github.com/your-org/django-multi-auth.git $projectRoot
}
Set-Location $projectRoot
```

2. **Create and activate a virtual environment**:

```powershell
python -m venv .venv
. .\.venv\Scripts\Activate.ps1
```

3. **Install dependencies**:

```powershell
pip install -U pip
pip install -r requirements.txt
```

4. **Apply migrations and create superuser**:

```powershell
python manage.py migrate
python manage.py createsuperuser
```

5. **Run development server**:

```powershell
python manage.py runserver 0.0.0.0:8000
```

---

## Key Concepts

### Authentication Layers

- **Django Auth Backend**: Core authentication system (`AUTHENTICATION_BACKENDS`) that supports multiple authenticators (model backend, remote user, social auth, custom backends).
- **Session vs Token Auth**: Traditional Django session cookies vs stateless token-based auth (JWT/OAuth2) used by APIs.
- **Multi-Provider Auth**: Supporting username/password plus one or more providers (Google, Microsoft, GitHub, corporate IdP) simultaneously.
- **MFA/2FA**: Additional factor (TOTP, hardware keys, SMS) enforced at login or sensitive operations.

### Identity Providers

- **OAuth2/OIDC**: Standard protocols used by providers like Azure AD, Auth0, Okta, Google; Django typically integrates via libraries (e.g. `django-allauth`, `python-social-auth`).
- **SAML**: XML-based protocol commonly used in enterprise SSO; may be integrated via `python3-saml` or similar libraries.
- **Internal Users**: Users stored in Django’s database, often used for fallback or service accounts.
- **Service Accounts**: Non-human accounts used for automation/integration; should be tightly scoped and audited.

---

## Configuration and Best Practices

### Environment and Secrets

Store all authentication-related configuration in environment variables or secret stores, not in source code:

```powershell
# Example environment variables for Django multi-auth
$env:DJANGO_SETTINGS_MODULE = "config.settings.production"
$env:DJANGO_SECRET_KEY = "<strong-secret>"
$env:DJANGO_DEBUG = "False"

# OAuth/OIDC providers
$env:OAUTH_GOOGLE_CLIENT_ID     = "<google-client-id>"
$env:OAUTH_GOOGLE_CLIENT_SECRET = "<google-client-secret>"
$env:OAUTH_AZURE_CLIENT_ID      = "<azure-client-id>"
$env:OAUTH_AZURE_TENANT_ID      = "<tenant-id>"

# SAML configuration
$env:SAML_METADATA_URL          = "https://idp.example.com/metadata"
$env:SAML_ENTITY_ID             = "https://django-app.example.com/saml/metadata/"

# JWT configuration
$env:JWT_SIGNING_KEY            = "<long-random-signing-key>"
$env:JWT_ACCESS_TOKEN_LIFETIME  = "900"   # seconds
$env:JWT_REFRESH_TOKEN_LIFETIME = "2592000"  # 30 days
```

Best practices:

- Load secrets from Windows Credential Manager, Azure Key Vault, or environment-specific secure stores.
- Use separate settings modules per environment (`development`, `staging`, `production`).
- Keep provider configuration (client IDs, endpoints, scopes) in `.env` files that are never committed.
- Script environment provisioning for consistency across machines.

### Reverse Proxy and TLS

Even on Windows, production Django deployments commonly run behind a reverse proxy (Nginx, Apache, IIS, or Azure App Service). Use PowerShell to manage configuration and certificates:

```powershell
# Example: enable Windows Firewall rule for reverse proxy port
$port = 443
$ruleName = "DjangoReverseProxy-$port"

if (-not (Get-NetFirewallRule -DisplayName $ruleName -ErrorAction SilentlyContinue)) {
    New-NetFirewallRule -DisplayName $ruleName `
        -Direction Inbound `
        -Action Allow `
        -Protocol TCP `
        -LocalPort $port
}
```

Best practices:

- Terminate TLS at the reverse proxy and forward traffic to Django over HTTP on localhost.
- Enforce `SECURE_SSL_REDIRECT`, `SESSION_COOKIE_SECURE`, and `CSRF_COOKIE_SECURE` in Django settings.
- Use HSTS headers at the proxy level.
- Automate certificate renewal (Let’s Encrypt via WSL/Certbot or a corporate PKI).

---

## Security Considerations

### Secrets and Certificates

- Use strong, randomly generated `SECRET_KEY` values per environment.
- Restrict who can read environment configuration files and credentials.
- Rotate client secrets and JWT signing keys regularly.
- Maintain a certificate inventory (CN, SANs, expiry dates) for all domains used by Django.

PowerShell snippet to list certificates for the current user:

```powershell
Get-ChildItem Cert:\CurrentUser\My | Select-Object `
    Subject, Thumbprint, NotBefore, NotAfter | `
    Sort-Object NotAfter
```

### Audit and Compliance

- Enable structured logging for authentication events (login success/failure, provider used, IP address).
- Forward logs to a SIEM (Azure Monitor, Splunk, ELK) using agents or log shipping scripts.
- Ensure retention of logs according to your compliance requirements.

---

## Examples

### Example 1: Provision Django Environment

```powershell
param(
    [string]$ProjectRoot = "C:\Projects\django-multi-auth",
    [string]$RepoUrl = "https://github.com/your-org/django-multi-auth.git"
)

if (-not (Test-Path $ProjectRoot)) {
    git clone $RepoUrl $ProjectRoot
}

Set-Location $ProjectRoot

if (-not (Test-Path ".venv")) {
    python -m venv .venv
}

. .\.venv\Scripts\Activate.ps1
pip install -U pip
pip install -r requirements.txt

python manage.py migrate
python manage.py collectstatic --noinput
```

### Example 2: Configure Environment for Multi-Auth

```powershell
function Set-DjangoMultiAuthEnvironment {
    param(
        [string]$Environment = "development"
    )

    switch ($Environment) {
        "development" {
            $env:DJANGO_SETTINGS_MODULE = "config.settings.dev"
            $env:DJANGO_DEBUG = "True"
        }
        "staging" {
            $env:DJANGO_SETTINGS_MODULE = "config.settings.staging"
            $env:DJANGO_DEBUG = "False"
        }
        "production" {
            $env:DJANGO_SETTINGS_MODULE = "config.settings.production"
            $env:DJANGO_DEBUG = "False"
        }
    }

    # Set common auth variables (values typically come from a secure store)
    $env:OAUTH_GOOGLE_CLIENT_ID     = "<client-id>"
    $env:OAUTH_GOOGLE_CLIENT_SECRET = "<client-secret>"
    $env:JWT_SIGNING_KEY            = "<signing-key>"
    $env:SAML_METADATA_URL          = "https://idp.example.com/metadata"

    Write-Host "Configured Django environment for '$Environment'."
}

# Usage
Set-DjangoMultiAuthEnvironment -Environment "staging"
```

### Example 3: Automate TLS with Certbot on WSL

```powershell
# Run Certbot inside WSL to obtain/renew certificates
$domain = "django-app.example.com"
$wslCommand = "sudo certbot certonly --nginx -d $domain --non-interactive --agree-tos -m admin@$domain"

wsl.exe $wslCommand

# Copy certificate to Windows certificate store (example; adjust paths)
$linuxCertPath = "/etc/letsencrypt/live/$domain/fullchain.pem"
$linuxKeyPath  = "/etc/letsencrypt/live/$domain/privkey.pem"

wsl.exe "sudo cat $linuxCertPath" | Out-File "C:\temp\$domain-cert.pem" -Encoding ascii
wsl.exe "sudo cat $linuxKeyPath"  | Out-File "C:\temp\$domain-key.pem"  -Encoding ascii

# Import into Windows store or use with reverse proxy
```

### Example 4: End-to-End Auth Health Check

```powershell
function Test-DjangoAuthHealth {
    param(
        [string]$BaseUrl = "https://django-app.example.com"
    )

    $endpoints = @(
        "/accounts/login/",
        "/accounts/google/login/",
        "/accounts/azure/login/",
        "/api/token/",
        "/saml/login/"
    )

    foreach ($path in $endpoints) {
        $url = "$BaseUrl$path"
        try {
            $response = Invoke-WebRequest -Uri $url -Method GET -UseBasicParsing -TimeoutSec 15
            Write-Host "[$($response.StatusCode)] $url" -ForegroundColor Green
        }
        catch {
            Write-Host "[ERROR] $url - $($_.Exception.Message)" -ForegroundColor Red
        }
    }
}

# Usage
Test-DjangoAuthHealth -BaseUrl "https://django-app.example.com"
```

---

## Troubleshooting

### Common Operational Issues

- **502/504 from reverse proxy**: Django gunicorn/uvicorn process not running or port mismatch.
- **TLS handshake errors**: Certificate not trusted, hostname mismatch, or expired certificate.
- **Login loop**: Incorrect redirect URIs configured at the identity provider.
- **Provider-specific failures**: Client ID/secret mismatch or missing scopes.

### Diagnostic Commands

```powershell
# Check listening ports
Get-NetTCPConnection -LocalPort 8000,443 | Select-Object LocalAddress, LocalPort, State, OwningProcess

# Check running Python processes
Get-Process python, python3 -ErrorAction SilentlyContinue | Select-Object Id, ProcessName, StartTime

# Tail Django logs (assuming logs directory)
Get-Content .\logs\django-auth.log -Wait -Tail 50
```

---

## Performance and Tuning

### Scaling and Observability

- Use a process manager (e.g. `supervisord`, `systemd` via WSL, or Windows services) for Django workers.
- Scale horizontally with multiple worker processes behind a reverse proxy.
- Enable application metrics (Prometheus, OpenTelemetry) and expose basic health endpoints.
- Monitor auth error rates and latency per provider.

---

## References and Further Reading

- Django Authentication: https://docs.djangoproject.com/en/4.2/topics/auth/
- Django Deployment Checklist: https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/
- OAuth 2.0 and OpenID Connect: https://auth0.com/docs/protocols
- Certbot Documentation: https://certbot.eff.org/
