# SSL/TLS PowerUser Guide (PowerShell)

**Last updated**: December 05, 2025<br>
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

SSL/TLS provides encrypted communication channels for secure data transmission. This guide covers certificate generation, management, and verification using PowerShell and OpenSSL on Windows. Power users need to understand certificate lifecycle management, cipher suite configuration, and security best practices for production deployments.

## Contents

- [SSL/TLS PowerUser Guide (PowerShell)](#ssltls-poweruser-guide-powershell)
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
    - [Import Certificate to Windows Certificate Store](#import-certificate-to-windows-certificate-store)
  - [Troubleshooting](#troubleshooting)
  - [Performance and Tuning](#performance-and-tuning)
  - [References and Further Reading](#references-and-further-reading)

---

## Quickstart

1. **Install OpenSSL**: Download from [Shining Light Productions](https://slproweb.com/products/Win32OpenSSL.html) or use Chocolatey: `choco install openssl`
2. **Add to PATH**: Add OpenSSL bin directory to system PATH environment variable
3. **Generate self-signed certificate**: `openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365 -nodes`
4. **Verify certificate**: `openssl x509 -in cert.pem -text -noout`
5. **Test TLS connection**: `openssl s_client -connect example.com:443 -showcerts`
6. **Convert formats**: `openssl pkcs12 -export -out certificate.pfx -inkey key.pem -in cert.pem`

## Key Concepts

- **Certificate Authority (CA)**: Trusted entity that issues digital certificates; root CAs are pre-installed in operating systems
- **Private/Public Key Pair**: Asymmetric cryptography foundation; private key signs/decrypts, public key verifies/encrypts
- **Certificate Signing Request (CSR)**: File containing public key and identity information submitted to CA for certificate issuance
- **Certificate Formats**: PEM (Base64 text), DER (binary), PFX/P12 (bundled cert+key), CRT/CER (certificate only)
- **Cipher Suites**: Combination of key exchange, authentication, encryption, and MAC algorithms negotiated during TLS handshake
- **TLS Versions**: Use TLS 1.2+ exclusively; TLS 1.0/1.1 and SSL 2.0/3.0 are deprecated and insecure

## Configuration and Best Practices

**OpenSSL Configuration File** (`openssl.cnf`):

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
- Store private keys with restrictive permissions (ACLs)
- Use Hardware Security Modules (HSMs) for production CA keys
- Implement certificate rotation 30 days before expiration

## Security Considerations

1. **Private Key Protection**: Never commit private keys to version control; use Windows DPAPI or Azure Key Vault
2. **Certificate Pinning**: Pin certificates in applications to prevent MITM attacks with rogue CAs
3. **OCSP Stapling**: Enable Online Certificate Status Protocol stapling to improve revocation checking
4. **Perfect Forward Secrecy**: Use ephemeral Diffie-Hellman (DHE/ECDHE) cipher suites exclusively
5. **Disable Weak Protocols**: Explicitly disable SSL 2.0, SSL 3.0, TLS 1.0, TLS 1.1 via registry or application config
6. **Cipher Suite Order**: Prioritize AEAD ciphers (AES-GCM, ChaCha20-Poly1305) over CBC mode
7. **Certificate Transparency**: Monitor CT logs for unauthorized certificate issuance for your domains

**Windows Registry Hardening**:

```powershell
# Disable TLS 1.0 and 1.1
New-Item 'HKLM:\SYSTEM\CurrentControlSet\Control\SecurityProviders\SCHANNEL\Protocols\TLS 1.0\Server' -Force
New-ItemProperty -Path 'HKLM:\SYSTEM\CurrentControlSet\Control\SecurityProviders\SCHANNEL\Protocols\TLS 1.0\Server' -Name 'Enabled' -Value 0 -PropertyType 'DWord'
New-Item 'HKLM:\SYSTEM\CurrentControlSet\Control\SecurityProviders\SCHANNEL\Protocols\TLS 1.1\Server' -Force
New-ItemProperty -Path 'HKLM:\SYSTEM\CurrentControlSet\Control\SecurityProviders\SCHANNEL\Protocols\TLS 1.1\Server' -Name 'Enabled' -Value 0 -PropertyType 'DWord'
```

## Examples

### Generate Self-Signed Certificate with SAN

Generate a self-signed certificate with Subject Alternative Names for local development, valid for one year with 4096-bit RSA key.

```powershell
# Create configuration file
$config = @"
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
"@

Set-Content -Path "openssl.cnf" -Value $config

# Generate certificate
openssl req -x509 -newkey rsa:4096 -keyout private.key -out certificate.crt -days 365 -nodes -config openssl.cnf

# Verify certificate
openssl x509 -in certificate.crt -text -noout | Select-String "Subject Alternative Name" -Context 0,3
```

### Create Certificate Signing Request (CSR) for Production

Create a CSR for submission to a Certificate Authority with proper organizational details and multiple SANs for production domain.

```powershell
# Generate private key
openssl genrsa -out production.key 4096

# Create CSR config
$csrConfig = @"
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
"@

Set-Content -Path "csr.cnf" -Value $csrConfig

# Generate CSR
openssl req -new -key production.key -out production.csr -config csr.cnf

# Verify CSR content
openssl req -in production.csr -noout -text | Select-String "Subject:|DNS:"
```

### Convert Certificate Formats and Bundle

Convert between PEM and PFX formats, create certificate bundles with intermediate CAs, and set password protection for distribution.

```powershell
# Convert PEM to PFX with password
$password = ConvertTo-SecureString -String "StrongPassword123!" -Force -AsPlainText
openssl pkcs12 -export -out certificate.pfx -inkey private.key -in certificate.crt -certfile ca-bundle.crt -password pass:StrongPassword123!

# Convert PFX to PEM
openssl pkcs12 -in certificate.pfx -out certificate-full.pem -nodes -password pass:StrongPassword123!

# Extract only certificate from PFX
openssl pkcs12 -in certificate.pfx -clcerts -nokeys -out certificate-only.crt -password pass:StrongPassword123!

# Extract only private key from PFX
openssl pkcs12 -in certificate.pfx -nocerts -nodes -out private-only.key -password pass:StrongPassword123!

# Create certificate chain bundle
Get-Content certificate.crt, intermediate.crt, root.crt | Set-Content -Path full-chain.pem
```

### Test TLS Connection and Cipher Suites

Test TLS connectivity, enumerate supported cipher suites, and verify certificate chain for a remote server.

```powershell
# Test TLS connection with full handshake details
openssl s_client -connect example.com:443 -showcerts -servername example.com

# Test specific TLS version
openssl s_client -connect example.com:443 -tls1_2 -servername example.com

# Extract server certificate
$cert = openssl s_client -connect example.com:443 -servername example.com 2>$null | openssl x509
$cert | Set-Content -Path "server-cert.pem"

# Check certificate expiration
$expiryDate = openssl x509 -in server-cert.pem -noout -enddate
Write-Host "Certificate expires: $expiryDate"

# List supported cipher suites
openssl ciphers -v 'HIGH:!aNULL:!MD5:!3DES' | ForEach-Object { $_ }

# Test specific cipher suite
openssl s_client -connect example.com:443 -cipher ECDHE-RSA-AES256-GCM-SHA384 -servername example.com
```

### Verify Certificate Chain and Revocation

Verify certificate chain against CA bundle, check OCSP revocation status, and validate certificate properties.

```powershell
# Verify certificate against CA bundle
openssl verify -CAfile ca-bundle.pem certificate.crt

# Extract OCSP responder URL
$ocspUrl = openssl x509 -in certificate.crt -noout -ocsp_uri
Write-Host "OCSP Responder: $ocspUrl"

# Check OCSP status
openssl ocsp -issuer ca-bundle.pem -cert certificate.crt -url $ocspUrl -CAfile ca-bundle.pem

# Verify certificate dates
$notBefore = openssl x509 -in certificate.crt -noout -startdate
$notAfter = openssl x509 -in certificate.crt -noout -enddate
Write-Host "Valid from: $notBefore"
Write-Host "Valid until: $notAfter"

# Check certificate fingerprint (SHA256)
$fingerprint = openssl x509 -in certificate.crt -noout -fingerprint -sha256
Write-Host "SHA256 Fingerprint: $fingerprint"
```

### Import Certificate to Windows Certificate Store

Import certificates into Windows Certificate Store programmatically with proper store locations and access permissions.

```powershell
# Import PFX to Personal store for Current User
$pfxPassword = ConvertTo-SecureString -String "StrongPassword123!" -Force -AsPlainText
Import-PfxCertificate -FilePath "certificate.pfx" -CertStoreLocation Cert:\CurrentUser\My -Password $pfxPassword

# Import PFX to Local Machine store (requires admin)
Import-PfxCertificate -FilePath "certificate.pfx" -CertStoreLocation Cert:\LocalMachine\My -Password $pfxPassword -Exportable

# Import CA certificate to Trusted Root
Import-Certificate -FilePath "ca-root.crt" -CertStoreLocation Cert:\LocalMachine\Root

# List certificates in Personal store
Get-ChildItem -Path Cert:\CurrentUser\My | Select-Object Subject, Thumbprint, NotAfter

# Export certificate from store
$cert = Get-ChildItem -Path Cert:\CurrentUser\My | Where-Object { $_.Subject -like "*example.com*" } | Select-Object -First 1
Export-Certificate -Cert $cert -FilePath "exported-cert.cer"
```

## Troubleshooting

**Certificate Verification Failures**:

- **Error**: "unable to get local issuer certificate"
  - **Cause**: Missing intermediate CA certificates in chain
  - **Fix**: Download intermediate certificates from CA and include in bundle: `openssl verify -CAfile full-chain.pem cert.crt`

**Private Key Mismatch**:

- **Error**: "key values mismatch"
  - **Cause**: Private key doesn't match certificate public key
  - **Fix**: Compare modulus: `openssl x509 -noout -modulus -in cert.crt | openssl md5` vs `openssl rsa -noout -modulus -in key.pem | openssl md5`

**Certificate Expired**:

- **Error**: "certificate has expired"
  - **Check**: `openssl x509 -in cert.crt -noout -dates`
  - **Fix**: Renew certificate before expiration; automate with Let's Encrypt or ACME protocol

**Common Logs to Check**:

- Windows Event Viewer: Security logs (Event ID 36888 for certificate errors)
- Application logs for TLS handshake failures
- IIS logs: `%SystemDrive%\inetpub\logs\LogFiles`
- OpenSSL debug output: Add `-debug` or `-msg` flags to s_client

**Cipher Suite Negotiation Failures**:

- **Check supported ciphers**: `openssl ciphers -v | Select-String "TLSv1.2"`
- **Server preference**: Use `-cipher` flag to test specific suites
- **Client/server mismatch**: Ensure overlap in supported cipher suites

## Performance and Tuning

**Key Size vs Performance**:

- RSA 2048-bit: Baseline performance, adequate for most use cases
- RSA 4096-bit: 7x slower key generation, 2x slower handshakes, recommended for CA and long-lived certificates
- ECDSA P-256: Faster handshakes than RSA, smaller key sizes, use for high-throughput servers

**Session Resumption**:

```powershell
# Enable TLS session tickets in IIS (reduces handshake overhead)
Set-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Control\SecurityProviders\SCHANNEL" -Name "EnableSessionTicket" -Value 1

# Configure session cache timeout (seconds)
Set-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Control\SecurityProviders\SCHANNEL" -Name "ServerCacheTime" -Value 3600
```

**OCSP Stapling**:

- Reduces client-side latency by 200-300ms per handshake
- Enable in IIS 8.0+: Enabled by default
- Verify: `openssl s_client -connect example.com:443 -status -servername example.com | Select-String "OCSP"`

**Hardware Acceleration**:

- Use AES-NI CPU instructions for AES-GCM cipher suites (10x faster)
- Verify support: `openssl speed -evp aes-256-gcm`
- Offload to dedicated crypto hardware for >10Gbps workloads

**Monitoring Commands**:

```powershell
# Measure TLS handshake time
Measure-Command { openssl s_client -connect example.com:443 -servername example.com < $null }

# Profile cipher suite performance
openssl speed rsa2048 rsa4096 ecdsap256

# Monitor certificate expiration
Get-ChildItem -Path Cert:\LocalMachine\My | Where-Object { $_.NotAfter -lt (Get-Date).AddDays(30) }
```

## References and Further Reading

- [OpenSSL Documentation](https://www.openssl.org/docs/) - Official OpenSSL command reference and library documentation
- [Mozilla SSL Configuration Generator](https://ssl-config.mozilla.org/) - Generate secure TLS configs for web servers and apps
- [SSL Labs Server Test](https://www.ssllabs.com/ssltest/) - Comprehensive TLS/SSL server configuration analysis
- [RFC 8446 - TLS 1.3](https://datatracker.ietf.org/doc/html/rfc8446) - Latest TLS protocol specification
- [Microsoft Schannel Documentation](https://docs.microsoft.com/en-us/windows-server/security/tls/tls-ssl-schannel-ssp-overview) - Windows TLS/SSL implementation details
