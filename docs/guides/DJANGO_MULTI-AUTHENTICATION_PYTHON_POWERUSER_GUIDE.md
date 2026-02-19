# DJANGO Multi-Authentication PowerUser Guide (Python)

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

This guide focuses on implementing robust multi-authentication in Django using Python: combining username/password, OAuth2/OIDC (Google, Azure AD, GitHub), JWT for APIs, and optional SAML and MFA. It shows how to structure settings, authentication backends, URL routing, and views so that you can safely support multiple identity providers in one project.

## Contents

- [DJANGO Multi-Authentication PowerUser Guide (Python)](#django-multi-authentication-poweruser-guide-python)
  - [Overview](#overview)
  - [Contents](#contents)
  - [Quickstart](#quickstart)
    - [Install and Scaffold Project](#install-and-scaffold-project)
    - [Core Dependencies](#core-dependencies)
  - [Key Concepts](#key-concepts)
    - [Authentication Backends](#authentication-backends)
    - [Session vs Token Auth](#session-vs-token-auth)
  - [Configuration and Best Practices](#configuration-and-best-practices)
    - [Settings Layout](#settings-layout)
    - [Environment Variables](#environment-variables)
  - [Security Considerations](#security-considerations)
    - [Password Storage and MFA](#password-storage-and-mfa)
    - [Token Handling](#token-handling)
  - [Examples](#examples)
    - [Example 1: Base Auth Setup](#example-1-base-auth-setup)
    - [Example 2: OAuth2/OIDC with Social Login](#example-2-oauth2oidc-with-social-login)
    - [Example 3: JWT for APIs](#example-3-jwt-for-apis)
    - [Example 4: MFA with django-otp](#example-4-mfa-with-django-otp)
  - [Troubleshooting](#troubleshooting)
    - [Common Configuration Errors](#common-configuration-errors)
    - [Debugging Tips](#debugging-tips)
  - [Performance and Tuning](#performance-and-tuning)
    - [Scaling Auth-heavy APIs](#scaling-auth-heavy-apis)
  - [References and Further Reading](#references-and-further-reading)

---

## Quickstart

### Install and Scaffold Project

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

pip install "Django>=4.2,<5" djangorestframework

django-admin startproject config .
python manage.py startapp accounts
```

### Core Dependencies

For multi-auth, you commonly combine:

```bash
pip install \
  django-allauth \
  djangorestframework-simplejwt \
  django-otp django-otp-yubikey \
  python3-saml
```

---

## Key Concepts

### Authentication Backends

In `settings.py`:

```python
AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",           # Username/password
    "allauth.account.auth_backends.AuthenticationBackend",  # Social auth (Google, GitHub, etc.)
]
```

- Order matters; Django will try backends sequentially.
- Custom backends can enforce additional constraints (tenant, domain, flags).

### Session vs Token Auth

- **Session auth**: Browser-centric; server-side session and CSRF protection.
- **Token/JWT auth**: API-centric; stateless bearer tokens with short lifetimes.
- **Hybrid**: Same user base, multiple auth methods (session for UI, JWT for API).

---

## Configuration and Best Practices

### Settings Layout

A typical production layout:

```python
# config/settings/base.py
from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ["DJANGO_SECRET_KEY"]
DEBUG = os.environ.get("DJANGO_DEBUG", "False") == "True"

ALLOWED_HOSTS = os.environ.get("DJANGO_ALLOWED_HOSTS", "").split(",")

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # Third-party
    "rest_framework",
    "rest_framework_simplejwt",
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "allauth.socialaccount.providers.google",

    "otp",
    "otp_totp",

    # Local
    "accounts",
]
```

REST framework and JWT:

```python
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
        "rest_framework.authentication.SessionAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
}

from datetime import timedelta

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=15),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=30),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
}
```

### Environment Variables

```bash
export DJANGO_SECRET_KEY="<long-random-secret>"
export DJANGO_DEBUG="False"
export DJANGO_ALLOWED_HOSTS="localhost,api.example.com"

# Google OAuth2
export SOCIAL_AUTH_GOOGLE_CLIENT_ID="<client-id>"
export SOCIAL_AUTH_GOOGLE_CLIENT_SECRET="<client-secret>"

# Azure AD
export SOCIAL_AUTH_AZUREAD_TENANT_ID="<tenant-id>"
export SOCIAL_AUTH_AZUREAD_CLIENT_ID="<client-id>"
export SOCIAL_AUTH_AZUREAD_CLIENT_SECRET="<client-secret>"

# JWT
export JWT_SIGNING_KEY="<jwt-signing-key>"
```

---

## Security Considerations

### Password Storage and MFA

- Always use Django’s built-in password hashing (`PBKDF2` by default) or stronger algorithms (`Argon2`).
- Enforce strong password policies and rate limit login attempts.
- Use MFA for admin and privileged roles (via `django-otp` or external IdPs).

Example: enabling Argon2:

```python
PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.Argon2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2PasswordHasher",
]
```

### Token Handling

- Keep access tokens short-lived; use refresh tokens for continuity.
- Use HTTPS everywhere; never transmit tokens over HTTP.
- Store JWT signing keys securely (Key Vault, environment variables, or files with restricted permissions).

---

## Examples

### Example 1: Base Auth Setup

`accounts/models.py`:

```python
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    # Example extension: tenant field
    tenant_id = models.CharField(max_length=64, blank=True, null=True)
```

`config/settings/base.py`:

```python
AUTH_USER_MODEL = "accounts.User"
LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/"
```

URLs:

```python
# config/urls.py
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("allauth.urls")),
    path("api/auth/", include("accounts.api_urls")),
]
```

### Example 2: OAuth2/OIDC with Social Login

`config/settings/base.py` (allauth configuration):

```python
SITE_ID = 1

ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_EMAIL_VERIFICATION = "mandatory"
ACCOUNT_AUTHENTICATION_METHOD = "username_email"

SOCIALACCOUNT_PROVIDERS = {
    "google": {
        "APP": {
            "client_id": os.environ.get("SOCIAL_AUTH_GOOGLE_CLIENT_ID"),
            "secret": os.environ.get("SOCIAL_AUTH_GOOGLE_CLIENT_SECRET"),
            "key": "",
        }
    }
}
```

Template snippet for login options:

```html
<a href="{% provider_login_url 'google' %}">Sign in with Google</a>
```

### Example 3: JWT for APIs

`accounts/api_urls.py`:

```python
from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path("token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
]
```

Example API view:

```python
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated


class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        return Response({
            "username": user.username,
            "email": user.email,
            "auth": request.auth.__class__.__name__ if request.auth else "session",
        })
```

### Example 4: MFA with django-otp

`config/settings/base.py`:

```python
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",

    "otp.middleware.OTPMiddleware",
]
```

Simple view enforcing OTP:

```python
from django_otp.decorators import otp_required
from django.http import HttpResponse


@otp_required
def sensitive_view(request):
    return HttpResponse("You passed MFA and can access this sensitive view.")
```

---

## Troubleshooting

### Common Configuration Errors

- **Improper redirect URIs**: Ensure configured redirect URIs at the IdP match Django’s URLs.
- **CSRF token missing**: For session-based auth, ensure CSRF middleware and template tags are correctly set up.
- **JWT not accepted**: Check audience (`aud`) and issuer (`iss`) claims, and that signing keys match.

### Debugging Tips

- Enable Django’s debug toolbar in non-production environments.
- Log authentication attempts and failures with enough context (user, provider, IP).
- Use `python -m http.server` or tools like `httpie` to simulate callback requests.

---

## Performance and Tuning

### Scaling Auth-heavy APIs

- Cache frequently accessed user/permission data in Redis.
- Use database connection pooling for high login volumes.
- Offload authentication to an external gateway (e.g. API Gateway or identity proxy) where appropriate.

---

## References and Further Reading

- Django Authentication: https://docs.djangoproject.com/en/4.2/topics/auth/
- Django REST Framework: https://www.django-rest-framework.org/
- django-allauth: https://django-allauth.readthedocs.io/
- django-otp: https://django-otp-official.readthedocs.io/
- SimpleJWT: https://django-rest-framework-simplejwt.readthedocs.io/
