# SSL/TLS PowerUser Guide (Bash)

**Last updated**: December 04, 2025<br>
**Author**: [Paul Namalomba](https://github.com/paulnamalomba)<br>

- SESKA Computational Engineer<br>
- SEAT Backend Developer<br>
- Software Developer<br>
- PhD Candidate (Civil Engineering Spec. Computational and Applied Mechanics)<br>
**Contact**: [kabwenzenamalomba@gmail.com](kabwenzenamalomba@gmail.com)<br>
**Website**: [paulnamalomba.github.io](https://paulnamalomba.github.io)<br>
<br>

[![Framework](https://img.shields.io/badge/OpenSSL-3.x-red.svg)](https://www.openssl.org/docs/)
[![License: MIT](https://img.shields.io/badge/License-MIT-gray.svg)](https://opensource.org/licenses/MIT)

## Overview

SSL/TLS provides encrypted communication channels for secure data transmission. This guide covers certificate generation, management, and verification using Bash and OpenSSL on Linux systems. Power users need to understand certificate lifecycle management, cipher suite configuration, and security best practices for production deployments.

## Contents

- [SSL/TLS PowerUser Guide (Bash)](#ssltls-poweruser-guide-bash)
  - [Overview](#overview)
  - [Contents](#contents)
  - [Quickstart](#quickstart)
  - [Key Concepts](#key-concepts)
  - [Configuration and Best Practices](#configuration-and-best-practices)
  - [Security Considerations](#security-considerations)
  - [Examples](#examples)
    - [Generate Self-Signed Certificate with SAN](#generate-self-signed-certificate-with-san)
    - [Create Certificate Signing Request (CSR) for Production](#create-certificate-signing-request-csr-for-production)
    - [Convert Certificate Formats and Bundle](#convert-certificate-formats-and-bundle)
    - [Test TLS Connection and Cipher Suites](#test-tls-connection-and-cipher-suites)
    - [Verify Certificate Chain and Revocation](#verify-certificate-chain-and-revocation)
    - [Automate Certificate Renewal with Let's Encrypt](#automate-certificate-renewal-with-lets-encrypt)
    - [Monitor Certificate Expiration](#monitor-certificate-expiration)
  - [Troubleshooting](#troubleshooting)
  - [Performance and Tuning](#performance-and-tuning)
  - [References and Further Reading](#references-and-further-reading)

---

## Quickstart

1. **Install OpenSSL**: `sudo apt-get install openssl` (Debian/Ubuntu) or `sudo yum install openssl` (RHEL/CentOS)
2. **Verify installation**: `openssl version -a`
3. **Generate self-signed certificate**: `openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365 -nodes`
4. **Verify certificate**: `openssl x509 -in cert.pem -text -noout`
5. **Test TLS connection**: `openssl s_client -connect example.com:443 -showcerts`
6. **Convert formats**: `openssl pkcs12 -export -out certificate.pfx -inkey key.pem -in cert.pem`

## Key Concepts

- **Certificate Authority (CA)**: Trusted entity that issues digital certificates; root CAs are pre-installed in `/etc/ssl/certs/` or `/etc/pki/tls/certs/`
- **Private/Public Key Pair**: Asymmetric cryptography foundation; private key signs/decrypts, public key verifies/encrypts
- **Certificate Signing Request (CSR)**: File containing public key and identity information submitted to CA for certificate issuance
- **Certificate Formats**: PEM (Base64 text), DER (binary), PFX/P12 (bundled cert+key), CRT/CER (certificate only)
- **Cipher Suites**: Combination of key exchange, authentication, encryption, and MAC algorithms negotiated during TLS handshake
- **TLS Versions**: Use TLS 1.2+ exclusively; TLS 1.0/1.1 and SSL 2.0/3.0 are deprecated and insecure

## Configuration and Best Practices

**OpenSSL Configuration File** (`/etc/ssl/openssl.cnf` or `~/.openssl.cnf`):

```ini
[req]
default_bits = 4096
default_md = sha256
distinguished_name = req_distinguished_name
x509_extensions = v3_ca

[req_distinguished_name]
countryName = Country Name (2 letter code)
stateOrProvinceName = State or Province Name
localityName = Locality Name
organizationName = Organization Name
commonName = Common Name

[v3_ca]
subjectAltName = @alt_names
basicConstraints = critical,CA:FALSE
keyUsage = digitalSignature, keyEncipherment

[alt_names]
DNS.1 = example.com
DNS.2 = *.example.com
IP.1 = 192.168.1.100
```

**Best Practices**:

- Use 4096-bit RSA keys or 256-bit ECDSA keys minimum
- Set certificate validity to 397 days maximum (browser requirement)
- Always include Subject Alternative Names (SANs) for hostnames
- Store private keys with restrictive permissions: `chmod 600 private.key`
- Use Hardware Security Modules (HSMs) for production CA keys
- Implement certificate rotation 30 days before expiration

## Security Considerations

1. **Private Key Protection**: Store keys in `/etc/ssl/private/` with 600 permissions; never commit to version control
2. **Certificate Pinning**: Pin certificates in applications to prevent MITM attacks with rogue CAs
3. **OCSP Stapling**: Enable Online Certificate Status Protocol stapling in Nginx/Apache to improve revocation checking
4. **Perfect Forward Secrecy**: Use ephemeral Diffie-Hellman (DHE/ECDHE) cipher suites exclusively
5. **Disable Weak Protocols**: Explicitly disable SSL 2.0, SSL 3.0, TLS 1.0, TLS 1.1 in server configuration
6. **Cipher Suite Order**: Prioritize AEAD ciphers (AES-GCM, ChaCha20-Poly1305) over CBC mode
7. **Certificate Transparency**: Monitor CT logs for unauthorized certificate issuance for your domains

**Nginx TLS Hardening**:

```nginx
ssl_protocols TLSv1.2 TLSv1.3;
ssl_ciphers 'ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-CHACHA20-POLY1305:ECDHE-RSA-CHACHA20-POLY1305';
ssl_prefer_server_ciphers on;
ssl_session_cache shared:SSL:10m;
ssl_session_timeout 10m;
ssl_stapling on;
ssl_stapling_verify on;
```

## Examples

### Generate Self-Signed Certificate with SAN

Generate a self-signed certificate with Subject Alternative Names for local development, valid for one year with 4096-bit RSA key.

```bash
#!/bin/bash

# Create configuration file
cat > openssl.cnf << EOF
[req]
default_bits = 4096
prompt = no
default_md = sha256
distinguished_name = dn
x509_extensions = v3_req

[dn]
CN = localhost
C = US
ST = State
L = City
O = Organization
OU = Development

[v3_req]
subjectAltName = @alt_names
keyUsage = digitalSignature, keyEncipherment
extendedKeyUsage = serverAuth

[alt_names]
DNS.1 = localhost
DNS.2 = *.localhost
IP.1 = 127.0.0.1
IP.2 = ::1
EOF

# Generate certificate
openssl req -x509 -newkey rsa:4096 -keyout private.key -out certificate.crt \
    -days 365 -nodes -config openssl.cnf

# Set proper permissions
chmod 600 private.key
chmod 644 certificate.crt

# Verify certificate
openssl x509 -in certificate.crt -text -noout | grep -A2 "Subject Alternative Name"
```

### Create Certificate Signing Request (CSR) for Production

Create a CSR for submission to a Certificate Authority with proper organizational details and multiple SANs for production domain.

```bash
#!/bin/bash

# Generate private key
openssl genrsa -out production.key 4096
chmod 600 production.key

# Create CSR config
cat > csr.cnf << EOF
[req]
default_bits = 4096
prompt = no
default_md = sha256
distinguished_name = dn
req_extensions = req_ext

[dn]
CN = example.com
C = US
ST = California
L = San Francisco
O = Example Inc
OU = Engineering

[req_ext]
subjectAltName = @alt_names

[alt_names]
DNS.1 = example.com
DNS.2 = www.example.com
DNS.3 = api.example.com
DNS.4 = *.example.com
EOF

# Generate CSR
openssl req -new -key production.key -out production.csr -config csr.cnf

# Verify CSR content
openssl req -in production.csr -noout -text | grep -E "Subject:|DNS:"

echo "CSR generated successfully. Submit production.csr to your CA."
```

### Convert Certificate Formats and Bundle

Convert between PEM and PFX formats, create certificate bundles with intermediate CAs, and set password protection for distribution.

```bash
#!/bin/bash

# Convert PEM to PFX with password
openssl pkcs12 -export -out certificate.pfx \
    -inkey private.key -in certificate.crt \
    -certfile ca-bundle.crt \
    -password pass:StrongPassword123!

# Convert PFX to PEM
openssl pkcs12 -in certificate.pfx -out certificate-full.pem \
    -nodes -password pass:StrongPassword123!

# Extract only certificate from PFX
openssl pkcs12 -in certificate.pfx -clcerts -nokeys \
    -out certificate-only.crt -password pass:StrongPassword123!

# Extract only private key from PFX
openssl pkcs12 -in certificate.pfx -nocerts -nodes \
    -out private-only.key -password pass:StrongPassword123!

# Create certificate chain bundle
cat certificate.crt intermediate.crt root.crt > full-chain.pem

# Verify bundle order (leaf -> intermediate -> root)
openssl crl2pkcs7 -nocrl -certfile full-chain.pem | \
    openssl pkcs7 -print_certs -noout
```

### Test TLS Connection and Cipher Suites

Test TLS connectivity, enumerate supported cipher suites, and verify certificate chain for a remote server.

```bash
#!/bin/bash

# Test TLS connection with full handshake details
echo | openssl s_client -connect example.com:443 -showcerts -servername example.com

# Test specific TLS version
echo | openssl s_client -connect example.com:443 -tls1_2 -servername example.com

# Extract server certificate
echo | openssl s_client -connect example.com:443 -servername example.com 2>/dev/null | \
    openssl x509 > server-cert.pem

# Check certificate expiration
expiry=$(openssl x509 -in server-cert.pem -noout -enddate | cut -d= -f2)
echo "Certificate expires: $expiry"

# Calculate days until expiration
expiry_epoch=$(date -d "$expiry" +%s)
current_epoch=$(date +%s)
days_left=$(( ($expiry_epoch - $current_epoch) / 86400 ))
echo "Days until expiration: $days_left"

# List supported cipher suites
openssl ciphers -v 'HIGH:!aNULL:!MD5:!3DES'

# Test specific cipher suite
echo | openssl s_client -connect example.com:443 \
    -cipher ECDHE-RSA-AES256-GCM-SHA384 -servername example.com
```

### Verify Certificate Chain and Revocation

Verify certificate chain against CA bundle, check OCSP revocation status, and validate certificate properties.

```bash
#!/bin/bash

# Verify certificate against CA bundle
openssl verify -CAfile /etc/ssl/certs/ca-certificates.crt certificate.crt

# Extract OCSP responder URL
ocsp_url=$(openssl x509 -in certificate.crt -noout -ocsp_uri)
echo "OCSP Responder: $ocsp_url"

# Check OCSP status
openssl ocsp -issuer ca-bundle.pem -cert certificate.crt \
    -url "$ocsp_url" -CAfile ca-bundle.pem

# Verify certificate dates
not_before=$(openssl x509 -in certificate.crt -noout -startdate | cut -d= -f2)
not_after=$(openssl x509 -in certificate.crt -noout -enddate | cut -d= -f2)
echo "Valid from: $not_before"
echo "Valid until: $not_after"

# Check certificate fingerprint (SHA256)
fingerprint=$(openssl x509 -in certificate.crt -noout -fingerprint -sha256)
echo "SHA256 Fingerprint: $fingerprint"

# Verify certificate chain completeness
openssl verify -show_chain -CAfile ca-bundle.pem certificate.crt
```

### Automate Certificate Renewal with Let's Encrypt

Automate certificate issuance and renewal using Certbot for Let's Encrypt, with post-renewal hooks for service reloads.

```bash
#!/bin/bash

# Install Certbot (Debian/Ubuntu)
sudo apt-get update
sudo apt-get install -y certbot python3-certbot-nginx

# Obtain certificate for Nginx
sudo certbot --nginx -d example.com -d www.example.com \
    --non-interactive --agree-tos -m admin@example.com

# Obtain certificate standalone (port 80)
sudo certbot certonly --standalone -d example.com \
    --non-interactive --agree-tos -m admin@example.com

# Dry-run renewal test
sudo certbot renew --dry-run

# Setup automatic renewal cron job
cat > /etc/cron.d/certbot-renew << 'EOF'
0 3 * * * root certbot renew --quiet --post-hook "systemctl reload nginx"
EOF

# Manual renewal
sudo certbot renew --force-renewal

# List all certificates
sudo certbot certificates

# Revoke certificate
sudo certbot revoke --cert-path /etc/letsencrypt/live/example.com/cert.pem
```

### Monitor Certificate Expiration

Create automated monitoring script to check certificate expiration dates and send alerts for certificates expiring within 30 days.

```bash
#!/bin/bash

# monitor-certs.sh - Certificate expiration monitoring script

CERT_DIR="/etc/ssl/certs"
WARNING_DAYS=30
LOG_FILE="/var/log/cert-monitor.log"

# Function to check certificate expiration
check_cert() {
    local cert_file=$1
    local expiry_date=$(openssl x509 -in "$cert_file" -noout -enddate 2>/dev/null | cut -d= -f2)

    if [ -z "$expiry_date" ]; then
        return
    fi

    local expiry_epoch=$(date -d "$expiry_date" +%s)
    local current_epoch=$(date +%s)
    local days_left=$(( ($expiry_epoch - $current_epoch) / 86400 ))

    if [ $days_left -lt 0 ]; then
        echo "EXPIRED: $cert_file (expired $((-days_left)) days ago)" | tee -a "$LOG_FILE"
    elif [ $days_left -lt $WARNING_DAYS ]; then
        echo "WARNING: $cert_file expires in $days_left days" | tee -a "$LOG_FILE"
    fi
}

# Check all certificates
for cert in "$CERT_DIR"/*.crt "$CERT_DIR"/*.pem; do
    [ -f "$cert" ] && check_cert "$cert"
done

# Check remote server certificate
check_remote() {
    local host=$1
    local port=${2:-443}

    echo | openssl s_client -connect "$host:$port" -servername "$host" 2>/dev/null | \
        openssl x509 -noout -dates 2>/dev/null
}

# Example: check remote servers
check_remote "example.com" 443
```

## Troubleshooting

**Certificate Verification Failures**:

- **Error**: "unable to get local issuer certificate"
  - **Cause**: Missing intermediate CA certificates in chain
  - **Fix**: Download intermediate certificates and create bundle: `cat cert.crt intermediate.crt > bundle.crt`

**Private Key Mismatch**:

- **Error**: "key values mismatch"
  - **Cause**: Private key doesn't match certificate public key
  - **Fix**: Compare modulus: `openssl x509 -noout -modulus -in cert.crt | openssl md5` vs `openssl rsa -noout -modulus -in key.pem | openssl md5`

**Certificate Expired**:

- **Error**: "certificate has expired"
  - **Check**: `openssl x509 -in cert.crt -noout -dates`
  - **Fix**: Renew certificate before expiration; automate with Let's Encrypt

**Common Logs to Check**:

- Nginx: `/var/log/nginx/error.log` for SSL handshake failures
- Apache: `/var/log/apache2/error.log` or `/var/log/httpd/error_log`
- System logs: `journalctl -u nginx -n 100` or `/var/log/syslog`
- OpenSSL debug: Add `-debug` or `-msg` flags to s_client

**Permission Errors**:

- **Error**: "Permission denied" when reading private key
  - **Fix**: `sudo chmod 600 /path/to/private.key && sudo chown root:root /path/to/private.key`
- **Error**: Nginx can't read certificate
  - **Fix**: Ensure nginx user has read permissions: `sudo chmod 644 /path/to/cert.crt`

## Performance and Tuning

**Key Size vs Performance**:

- RSA 2048-bit: Baseline performance, adequate for most use cases
- RSA 4096-bit: 7x slower key generation, 2x slower handshakes, recommended for CA and long-lived certificates
- ECDSA P-256: Faster handshakes than RSA, smaller key sizes, use for high-throughput servers

**Session Resumption**:

```nginx
# Nginx configuration for session caching
ssl_session_cache shared:SSL:50m;
ssl_session_timeout 1d;
ssl_session_tickets on;
```

**OCSP Stapling**:

```nginx
# Nginx OCSP stapling configuration
ssl_stapling on;
ssl_stapling_verify on;
ssl_trusted_certificate /etc/ssl/certs/ca-bundle.crt;
resolver 8.8.8.8 8.8.4.4 valid=300s;
resolver_timeout 5s;
```

**Hardware Acceleration**:

- Use AES-NI CPU instructions for AES-GCM cipher suites (10x faster)
- Verify support: `grep -o aes /proc/cpuinfo | uniq`
- Test performance: `openssl speed -evp aes-256-gcm`
- Offload to dedicated crypto hardware for >10Gbps workloads

**Monitoring Commands**:

```bash
# Measure TLS handshake time
time echo | openssl s_client -connect example.com:443 -servername example.com 2>/dev/null

# Profile cipher suite performance
openssl speed rsa2048 rsa4096 ecdsap256

# Monitor active SSL connections (requires ss or netstat)
ss -tan | grep ':443' | wc -l

# Check SSL handshake rate
watch -n 1 'ss -tan | grep ":443.*ESTABLISHED" | wc -l'
```

## References and Further Reading

- [OpenSSL Documentation](https://www.openssl.org/docs/) - Official OpenSSL command reference and library documentation
- [Mozilla SSL Configuration Generator](https://ssl-config.mozilla.org/) - Generate secure TLS configs for web servers and apps
- [SSL Labs Server Test](https://www.ssllabs.com/ssltest/) - Comprehensive TLS/SSL server configuration analysis
- [RFC 8446 - TLS 1.3](https://datatracker.ietf.org/doc/html/rfc8446) - Latest TLS protocol specification
- [Let's Encrypt Documentation](https://letsencrypt.org/docs/) - Free, automated certificate authority documentation
