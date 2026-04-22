# SSH PowerUser Guide (PowerShell & Bash)

**Last updated**: April 22, 2026<br>
**Author**: [Paul Namalomba](https://github.com/paulnamalomba)<br>

- SESKA Computational Engineer<br>
- SEAT Backend Developer<br>
- Software Developer<br>
- PhD Candidate (Civil Engineering Spec. Computational and Applied Mechanics)<br>

**Contact**: [kabwenzenamalomba@gmail.com](mailto:kabwenzenamalomba@gmail.com)<br>
**Website**: [paulnamalomba.github.io](https://paulnamalomba.github.io)<br>
<br>

[![Protocol](https://img.shields.io/badge/OpenSSH-9.x-green.svg)](https://www.openssh.com/manual.html)
[![Shells](https://img.shields.io/badge/Shells-PowerShell%20%7C%20Bash-blue.svg)](https://learn.microsoft.com/windows-server/administration/openssh/openssh-overview)
[![License: MIT](https://img.shields.io/badge/License-MIT-gray.svg)](https://opensource.org/licenses/MIT)

## Overview

SSH is the standard secure remote access protocol for Linux servers, Windows servers, Git remotes, bastion hosts, and encrypted file transfer. This guide targets native OpenSSH workflows on Windows and Linux, using both PowerShell and Bash where command or path behavior differs. It covers client and server setup, key-based passwordless authentication, `~/.ssh/config` design, file copying with `scp` and `sftp`, advanced forwarding and jump-host patterns, and hardening practices that are actually safe in production.

It is intentionally explicit about one point that often gets mangled in low-quality tutorials: standard OpenSSH does not have a legitimate "store my plaintext password in the config file" feature. If you want to stop typing passwords, the correct pattern is key-based authentication, optionally combined with `ssh-agent`, `IdentityFile`, `IdentitiesOnly`, and host aliases in the SSH config.

## Contents

- [SSH PowerUser Guide (PowerShell \& Bash)](#ssh-poweruser-guide-powershell--bash)
  - [Overview](#overview)
  - [Contents](#contents)
  - [Quickstart](#quickstart)
  - [Key Concepts](#key-concepts)
  - [Configuration and Best Practices](#configuration-and-best-practices)
    - [1. What OpenSSH Components You Actually Need](#1-what-openssh-components-you-actually-need)
    - [2. Install and Verify SSH on Windows and Linux](#2-install-and-verify-ssh-on-windows-and-linux)
    - [3. Generate Modern Keys Correctly](#3-generate-modern-keys-correctly)
    - [4. Install Public Keys for Passwordless Login](#4-install-public-keys-for-passwordless-login)
    - [5. SSH Config Files That Remove Repetition Safely](#5-ssh-config-files-that-remove-repetition-safely)
    - [6. Server-Side SSH Hardening](#6-server-side-ssh-hardening)
    - [7. File Transfer with `scp` and `sftp`](#7-file-transfer-with-scp-and-sftp)
    - [8. Advanced SSH Capabilities](#8-advanced-ssh-capabilities)
  - [Security Considerations](#security-considerations)
  - [Examples](#examples)
    - [Example 1: Install OpenSSH on Windows](#example-1-install-openssh-on-windows)
    - [Example 2: Install OpenSSH on Linux](#example-2-install-openssh-on-linux)
    - [Example 3: Generate a Key and Load It into `ssh-agent`](#example-3-generate-a-key-and-load-it-into-ssh-agent)
    - [Example 4: Install Your Public Key on a Remote Linux Host](#example-4-install-your-public-key-on-a-remote-linux-host)
    - [Example 5: Build a Clean SSH Config](#example-5-build-a-clean-ssh-config)
    - [Example 6: Upload and Download Files](#example-6-upload-and-download-files)
    - [Example 7: Use a Jump Host and Port Forwarding](#example-7-use-a-jump-host-and-port-forwarding)
  - [Troubleshooting](#troubleshooting)
  - [Performance and Tuning](#performance-and-tuning)
  - [References and Further Reading](#references-and-further-reading)

---

## Quickstart

1. Install the OpenSSH client on your machine and the OpenSSH server on any machine that must accept inbound SSH.
2. Generate an `ed25519` keypair with a passphrase using `ssh-keygen`.
3. Start `ssh-agent` and add the private key so you do not retype the passphrase every single session.
4. Install the public key into the target account's `authorized_keys` file.
5. Create a host alias in the SSH config so you only type `ssh myserver` instead of repeating host, user, port, and key flags.
6. Once key login works, disable password authentication on servers that should not accept it.

## Key Concepts

- **OpenSSH client**: Provides `ssh`, `scp`, `sftp`, `ssh-keygen`, `ssh-agent`, and `ssh-add`.
- **OpenSSH server**: Provides `sshd`, which accepts inbound SSH sessions.
- **Host key**: The server's identity key. It proves you are connecting to the same server you connected to previously.
- **User key**: Your own private/public keypair used for authentication.
- **`known_hosts`**: Local file that stores trusted server host keys.
- **`authorized_keys`**: Remote file that stores user public keys allowed to log in.
- **Passwordless SSH**: Usually means key-based login. It does not mean plaintext password storage in `ssh_config`.
- **`ssh-agent`**: A local key cache that holds decrypted private keys in memory after you unlock them once.
- **Host alias**: A friendly name in `~/.ssh/config` that expands to real connection parameters.
- **Jump host / bastion**: An intermediate SSH host used to reach private network targets.
- **Local port forward**: Exposes a remote service on your local machine.
- **Remote port forward**: Exposes a local service on the remote machine.
- **Dynamic port forward**: Creates a SOCKS proxy over SSH.

## Configuration and Best Practices

### 1. What OpenSSH Components You Actually Need

There are two separate SSH roles and they should not be confused:

- **Outbound SSH**: Your machine initiates a connection to another machine. You need the OpenSSH client.
- **Inbound SSH**: Other machines connect to your machine. You need the OpenSSH server.

For a normal developer workstation:

- install the client
- install the server only if the workstation must be reachable remotely

For a Linux or Windows server that you manage remotely:

- install both client and server
- harden the server
- keep client tooling available for Git, backups, bastions, and cross-host admin work

Useful file locations:

| Purpose | Windows | Linux |
| :--- | :--- | :--- |
| Client config | `%USERPROFILE%\.ssh\config` | `~/.ssh/config` |
| Known hosts | `%USERPROFILE%\.ssh\known_hosts` | `~/.ssh/known_hosts` |
| User authorized keys | `%USERPROFILE%\.ssh\authorized_keys` for standard users | `~/.ssh/authorized_keys` |
| Admin authorized keys on Windows server | `C:\ProgramData\ssh\administrators_authorized_keys` may be used by default | Not applicable |
| Server config | `C:\ProgramData\ssh\sshd_config` | `/etc/ssh/sshd_config` or `/etc/ssh/sshd_config.d/*.conf` |

### 2. Install and Verify SSH on Windows and Linux

On modern Windows 10/11 and Windows Server, OpenSSH is normally installed via Windows optional capabilities. PowerShell is the cleanest way to manage it.

On Linux, package names vary slightly, but the split is consistent: client package plus server package.

After installation, verify these basics before doing anything else:

- `ssh -V`
- `sshd -T` on servers where supported
- service status for `ssh`, `sshd`, or `ssh-agent`
- whether TCP port 22 is listening on hosts that should accept connections

On Windows, useful checks are:

- `Get-Service sshd, ssh-agent`
- `Get-NetTCPConnection -LocalPort 22`
- `Test-NetConnection servername -Port 22`

On Linux, useful checks are:

- `systemctl status ssh` or `systemctl status sshd`
- `ss -tlnp | grep ':22'`
- `ssh -V`

### 3. Generate Modern Keys Correctly

Prefer `ed25519` unless you have a legacy interoperability requirement.

Why:

- shorter keys
- fast operations
- strong modern default
- less parameter tuning than RSA

Recommended rule set:

- Use one primary admin key per person, not one shared team private key.
- Add a passphrase unless the key exists purely for locked-down automation.
- Name keys deliberately if you manage multiple environments.
- Keep private keys out of sync tools and source control.

Example naming patterns:

- `id_ed25519` for your default daily key
- `id_ed25519_work` for a work-specific identity
- `id_ed25519_backup` for backup automation

### 4. Install Public Keys for Passwordless Login

The correct passwordless pattern is:

1. generate a keypair locally
2. copy only the public key to the remote host
3. append the public key to `authorized_keys`
4. keep the private key private

If `ssh-copy-id` exists on your Bash client, use it. On Windows PowerShell, the practical equivalents are either:

- upload the public key with `scp`, then append it remotely
- manually append the public key after opening a one-time password session

Key file hygiene matters:

- Linux: `chmod 700 ~/.ssh`, `chmod 600 ~/.ssh/authorized_keys`, `chmod 600 ~/.ssh/config`
- Windows: inherited ACLs can break OpenSSH key acceptance; use `icacls` if permissions become too broad

Windows server nuance:

- if the account is in the local Administrators group, inspect `C:\ProgramData\ssh\sshd_config`
- many Windows OpenSSH server defaults use a `Match Group administrators` block
- that block often redirects key lookup to `C:\ProgramData\ssh\administrators_authorized_keys`
- if your per-user `authorized_keys` file seems ignored, this is one of the first places to check

### 5. SSH Config Files That Remove Repetition Safely

The SSH config file is where quality-of-life improvements live.

Good uses of the config:

- set host aliases
- pin usernames and ports
- point specific hosts at specific keys
- define jump hosts
- set keepalive options
- add local forwarding rules for repetitive workflows

Common safe directives:

| Directive | Purpose |
| :--- | :--- |
| `Host` | Alias block name |
| `HostName` | Real DNS name or IP |
| `User` | Remote account |
| `Port` | Non-default SSH port |
| `IdentityFile` | Private key path |
| `IdentitiesOnly yes` | Forces the client to offer only the chosen key |
| `AddKeysToAgent yes` | Convenient on clients with `ssh-agent` |
| `ServerAliveInterval 30` | Keepalive probe interval |
| `ServerAliveCountMax 3` | Disconnect after repeated failures |
| `ProxyJump` | Jump through a bastion host |
| `LocalForward` | Persistent local port forward |
| `ForwardAgent` | Forward your local agent, only when needed |
| `StrictHostKeyChecking ask` | Safer first-connection behavior |

Bad uses of the config:

- trying to store a plaintext password there
- globally disabling host-key checking
- globally enabling agent forwarding
- using a single wildcard block that silently affects every host on every network

### 6. Server-Side SSH Hardening

Once key-based access is verified, harden the server.

Typical minimum baseline on Linux servers:

- `PermitRootLogin no`
- `PasswordAuthentication no`
- `KbdInteractiveAuthentication no`
- `PubkeyAuthentication yes`
- `PermitEmptyPasswords no`
- `MaxAuthTries 3`
- `AllowUsers youradminuser` or `AllowGroups ssh-admins`

On Windows OpenSSH Server, not every Linux-centric directive is equally relevant, but these still matter:

- `PasswordAuthentication no`
- `PubkeyAuthentication yes`
- `PermitEmptyPasswords no`
- `AllowUsers` or `AllowGroups`
- `MaxAuthTries 3`

Operational rule:

- validate config before restart
- keep one working session open while testing a second session

Typical validation commands:

- Linux: `sudo sshd -t`
- Windows: `sshd -t`

### 7. File Transfer with `scp` and `sftp`

`scp` and `sftp` ride on SSH and inherit the same config, identities, and host aliases.

What to use when:

- `scp`: fast one-shot upload or download, recursive copy, simple scripting
- `sftp`: interactive browsing, directory navigation, multiple put/get actions in one session

Key habits:

- quote Windows paths in PowerShell if they contain spaces
- remember that remote paths are almost always POSIX-style on Linux hosts
- if you use a host alias in the config, use that alias in `scp` and `sftp` too
- custom ports use `-P` for `scp` and `-o Port=` or config entries for `sftp`

### 8. Advanced SSH Capabilities

Once the basics are stable, SSH becomes a secure transport toolkit rather than just a remote shell.

Important advanced patterns:

- **Jump hosts**: `ssh -J bastion target`
- **Local forwarding**: `ssh -L 5432:127.0.0.1:5432 db-host`
- **Remote forwarding**: `ssh -R 8080:127.0.0.1:8080 host`
- **Dynamic forwarding**: `ssh -D 1080 host`
- **Agent forwarding**: `ssh -A host`, use only when necessary and trusted
- **Connection multiplexing**: powerful on Unix-like Bash clients via `ControlMaster` and `ControlPersist`

Important accuracy note:

- connection multiplexing is a Unix-centric OpenSSH optimization used heavily on Linux, macOS, and WSL clients
- it is not a core day-to-day Windows PowerShell workflow, so do not build your main Windows setup around it unless you have verified the environment supports it cleanly

## Security Considerations

1. **Do not disable host-key verification globally**: `StrictHostKeyChecking no` plus `UserKnownHostsFile /dev/null` is a short-lived lab shortcut, not a production habit.
2. **Do not try to automate plaintext passwords with config files**: OpenSSH is designed around keys, agents, and host aliases for a reason.
3. **Use separate keys for people and automation**: a backup job key should not be your personal admin key.
4. **Use passphrases for human-operated keys**: then let `ssh-agent` handle convenience.
5. **Restrict server-side access deliberately**: `AllowUsers`, `AllowGroups`, firewall rules, and non-root administration matter more than just changing the port.
6. **Review host key changes carefully**: an unexpected host key mismatch can indicate a rebuild, an IP reuse event, or a man-in-the-middle problem.
7. **Treat agent forwarding as privileged delegation**: if you forward your agent into an untrusted host, that host can try to use your agent while the session exists.
8. **Protect private keys on disk**: Linux permissions and Windows ACLs both matter.

## Examples

### Example 1: Install OpenSSH on Windows

Use PowerShell as Administrator.

```powershell
# Inspect capability state
Get-WindowsCapability -Online | Where-Object Name -like 'OpenSSH*'

# Install client and server if needed
Add-WindowsCapability -Online -Name OpenSSH.Client~~~~0.0.1.0
Add-WindowsCapability -Online -Name OpenSSH.Server~~~~0.0.1.0

# Start and persist services
Set-Service -Name ssh-agent -StartupType Automatic
Start-Service ssh-agent

Set-Service -Name sshd -StartupType Automatic
Start-Service sshd

# Verify
ssh -V
Get-Service sshd, ssh-agent
Get-NetTCPConnection -LocalPort 22 -ErrorAction SilentlyContinue
```

If the inbound firewall rule does not exist or you want to create it explicitly:

```powershell
New-NetFirewallRule -Name 'OpenSSH-Server-In-TCP' `
  -DisplayName 'OpenSSH Server (TCP 22)' `
  -Enabled True `
  -Direction Inbound `
  -Protocol TCP `
  -Action Allow `
  -LocalPort 22
```

### Example 2: Install OpenSSH on Linux

Debian or Ubuntu style:

```bash
sudo apt update
sudo apt install -y openssh-client openssh-server

sudo systemctl enable --now ssh
ssh -V
sudo systemctl status ssh --no-pager
ss -tlnp | grep ':22'
```

RHEL, Rocky, AlmaLinux, Fedora style:

```bash
sudo dnf install -y openssh-clients openssh-server

sudo systemctl enable --now sshd
ssh -V
sudo systemctl status sshd --no-pager
ss -tlnp | grep ':22'
```

### Example 3: Generate a Key and Load It into `ssh-agent`

PowerShell:

```powershell
# Generate a modern keypair
ssh-keygen -t ed25519 -a 100 -f "$HOME\.ssh\id_ed25519_work" -C "work-admin"

# Ensure the agent is running
Set-Service -Name ssh-agent -StartupType Automatic
Start-Service ssh-agent

# Add the key for this login session
ssh-add "$HOME\.ssh\id_ed25519_work"

# List loaded keys
ssh-add -l
```

Bash:

```bash
ssh-keygen -t ed25519 -a 100 -f ~/.ssh/id_ed25519_work -C "work-admin"

eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_ed25519_work
ssh-add -l
```

If Windows key permissions become a problem, repair them with `icacls`:

```powershell
icacls "$HOME\.ssh" /inheritance:r /grant:r "$env:USERNAME:(OI)(CI)F" /grant:r "SYSTEM:(OI)(CI)F"
icacls "$HOME\.ssh\id_ed25519_work" /inheritance:r /grant:r "$env:USERNAME:R" /grant:r "SYSTEM:R"
```

### Example 4: Install Your Public Key on a Remote Linux Host

Bash with `ssh-copy-id`:

```bash
ssh-copy-id -i ~/.ssh/id_ed25519_work.pub admin@192.168.1.50
ssh admin@192.168.1.50
```

PowerShell equivalent using `scp` plus a remote append:

```powershell
scp "$HOME\.ssh\id_ed25519_work.pub" admin@192.168.1.50:/tmp/id_ed25519_work.pub

ssh admin@192.168.1.50 "umask 077; mkdir -p ~/.ssh; cat /tmp/id_ed25519_work.pub >> ~/.ssh/authorized_keys; rm -f /tmp/id_ed25519_work.pub"

ssh admin@192.168.1.50
```

Manual Linux-side permission repair if login still fails:

```bash
chmod 700 ~/.ssh
chmod 600 ~/.ssh/authorized_keys
chown -R "$USER":"$USER" ~/.ssh
```

### Example 5: Build a Clean SSH Config

PowerShell path:

```powershell
New-Item -ItemType Directory -Force -Path "$HOME\.ssh" | Out-Null
notepad "$HOME\.ssh\config"
```

Bash path:

```bash
mkdir -p ~/.ssh
chmod 700 ~/.ssh
${EDITOR:-vim} ~/.ssh/config
chmod 600 ~/.ssh/config
```

Shared config example:

```text
Host bastion
    HostName 203.0.113.10
    User ops
    Port 22
    IdentityFile ~/.ssh/id_ed25519_work
    IdentitiesOnly yes
    AddKeysToAgent yes
    ServerAliveInterval 30
    ServerAliveCountMax 3

Host app-prod
    HostName 10.10.20.15
    User ubuntu
    IdentityFile ~/.ssh/id_ed25519_work
    IdentitiesOnly yes
    ProxyJump bastion
    LocalForward 15432 127.0.0.1:5432

Host git-work
    HostName github.com
    User git
    IdentityFile ~/.ssh/id_ed25519_work
    IdentitiesOnly yes
```

Then use it cleanly:

```bash
ssh app-prod
scp ./build.tar.gz app-prod:/srv/releases/
sftp app-prod
ssh -T git-work
```

### Example 6: Upload and Download Files

PowerShell upload to Linux host:

```powershell
scp -r ".\publish" app-prod:/srv/myapp/
```

PowerShell download from Linux host:

```powershell
scp app-prod:/var/log/nginx/access.log "$HOME\Downloads\"
```

Bash upload:

```bash
scp -r ./publish app-prod:/srv/myapp/
```

Bash download:

```bash
scp app-prod:/var/log/nginx/access.log ./
```

Interactive `sftp` session:

```bash
sftp app-prod
sftp> pwd
sftp> lpwd
sftp> put ./artifact.zip
sftp> get /var/log/syslog
sftp> mkdir uploads
sftp> cd uploads
sftp> mput ./*.csv
sftp> bye
```

Custom SSH port example:

```bash
scp -P 2222 ./backup.tar.gz admin@example.com:/srv/backups/
```

### Example 7: Use a Jump Host and Port Forwarding

One-off jump host connection:

```bash
ssh -J ops@203.0.113.10 ubuntu@10.10.20.15
```

Local forward to a remote PostgreSQL instance:

```bash
ssh -L 15432:127.0.0.1:5432 app-prod
```

Now your local tools can connect to `127.0.0.1:15432` while the database remains private.

Remote forward exposing a local service to the remote host:

```bash
ssh -R 18080:127.0.0.1:8080 bastion
```

Dynamic SOCKS proxy:

```bash
ssh -D 1080 bastion
```

Unix-like Bash client multiplexing example:

```text
Host *
    ControlMaster auto
    ControlPath ~/.ssh/cm-%r@%h:%p
    ControlPersist 10m
```

That setting can drastically reduce repeated connection startup cost on Linux or WSL clients when you perform many sequential `ssh`, `scp`, or `sftp` operations.

## Troubleshooting

| Problem | Likely Cause | Practical Checks |
| :--- | :--- | :--- |
| `Connection refused` | `sshd` not running or firewall blocked | Check service state and TCP 22 listener |
| `Permission denied (publickey)` | wrong key, wrong user, bad permissions, admin-key redirect on Windows | Use `ssh -vvv`, inspect `authorized_keys`, inspect Windows `Match Group administrators` block |
| Host key mismatch warning | server rebuilt, DNS/IP reuse, or security event | inspect `known_hosts` entry before deleting it |
| Key ignored on Windows | ACLs too broad or wrong authorized keys path | repair ACLs with `icacls`; inspect `C:\ProgramData\ssh\sshd_config` |
| File transfer fails but shell login works | wrong path syntax, wrong port, permissions on remote target | test with a small file first and explicit destination |
| First connection hangs | DNS, firewall, or dead route | `Test-NetConnection host -Port 22` in PowerShell, `ssh -vvv host` in Bash |

Useful PowerShell diagnostics:

```powershell
Test-NetConnection 192.168.1.50 -Port 22
ssh -vvv app-prod
Get-Service sshd, ssh-agent
Get-WinEvent -LogName 'OpenSSH/Operational' -MaxEvents 20
```

Useful Linux diagnostics:

```bash
ssh -vvv app-prod
sudo journalctl -u ssh -n 50 --no-pager
sudo journalctl -u sshd -n 50 --no-pager
sudo sshd -t
ss -tlnp | grep ':22'
```

## Performance and Tuning

- Use host aliases so repetitive workflows stay readable and consistent.
- Use `ssh-agent` for human workflows instead of unencrypted private keys or no-passphrase habits.
- On Unix-like Bash clients, use connection multiplexing if you run many SSH commands in short bursts.
- Use `Compression yes` only when bandwidth is tight and CPU is not the bottleneck.
- Prefer `scp` for simple scripted transfers and `sftp` for interactive transfer sessions.
- For very large, repetitive directory synchronization on Bash systems, `rsync -e ssh` is often better than repeated `scp`, but it is not a native Windows PowerShell-first workflow.

Example optional compression block:

```text
Host slow-link
    HostName 198.51.100.20
    User ops
    Compression yes
    ServerAliveInterval 30
```

## References and Further Reading

- OpenSSH manuals: <https://www.openssh.com/manual.html>
- Microsoft OpenSSH for Windows documentation: <https://learn.microsoft.com/windows-server/administration/openssh/openssh-overview>
- `ssh_config` reference: <https://man.openbsd.org/ssh_config>
- `sshd_config` reference: <https://man.openbsd.org/sshd_config>
- `scp` reference: <https://man.openbsd.org/scp>
- `sftp` reference: <https://man.openbsd.org/sftp>
