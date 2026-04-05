# Ubuntu Server 24.04 LTS on Bare Metal: SSD-Only Install, Networking, and SSH

<br>
**Last updated**: April 05, 2026<br>
**Author**: [Paul Namalomba](https://github.com/paulnamalomba)<br>
  - SESKA Computational Engineer<br>
  - SEAT Backend Developer<br>
  - Software Developer<br>
  - PhD Candidate (Civil Engineering Spec. Computational and Applied Mechanics)<br>
**Contact**: [kabwenzenamalomba@gmail.com](mailto:kabwenzenamalomba@gmail.com)<br>
**Website**: [paulnamalomba.github.io](https://paulnamalomba.github.io)<br>
<br>
[![OS](https://img.shields.io/badge/Ubuntu-24.04_LTS-E95420.svg)](https://ubuntu.com/server)
[![Form Factor](https://img.shields.io/badge/Deployment-Bare_Metal-gray.svg)](https://ubuntu.com/download/server)
[![Remote Access](https://img.shields.io/badge/Remote-OpenSSH-green.svg)](https://www.openssh.com/)

## Overview

This guide covers a production-minded installation of Ubuntu Server 24.04 LTS onto a physical machine with a 128 GB SSD, 16 GB RAM, Intel Core i7 9th Gen CPU, and an NVIDIA RTX 1650 GPU. The specific deployment objective is to erase and repurpose the SSD for Ubuntu Server while preserving data that already exists on the HDD for later use, including the possibility of reinstalling Windows in the future without destroying the HDD contents.

The emphasis is not only on getting the machine to boot, but on getting the platform correct: UEFI/GPT layout, bootloader placement on the SSD only, predictable networking, inbound and outbound SSH configuration, initial OS hardening, package hygiene, data-preserving mount strategies, and common failure cases seen during bare-metal installs.

## Contents

- [Ubuntu Server 24.04 LTS on Bare Metal: SSD-Only Install, Networking, and SSH](#ubuntu-server-2404-lts-on-bare-metal-ssd-only-install-networking-and-ssh)
  - [Overview](#overview)
  - [Contents](#contents)
  - [Quickstart](#quickstart)
    - [Prerequisites](#prerequisites)
    - [Recommended Deployment Order](#recommended-deployment-order)
  - [Key Concepts](#key-concepts)
    - [Storage Strategy for This Machine](#storage-strategy-for-this-machine)
    - [UEFI, GPT, and Bootloader Placement](#uefi-gpt-and-bootloader-placement)
    - [Networking Model on Ubuntu Server 24.04](#networking-model-on-ubuntu-server-2404)
    - [SSH Reception vs SSH Emission](#ssh-reception-vs-ssh-emission)
    - [NVIDIA Considerations on a Headless Server](#nvidia-considerations-on-a-headless-server)
  - [Configuration and Best Practices](#configuration-and-best-practices)
    - [1. Pre-Install Safety and Data Preservation](#1-pre-install-safety-and-data-preservation)
    - [2. BIOS/UEFI Firmware Preparation](#2-biosuefi-firmware-preparation)
    - [3. Build the Ubuntu Server Installer USB](#3-build-the-ubuntu-server-installer-usb)
    - [4. Identify the Correct SSD and Protect the HDD](#4-identify-the-correct-ssd-and-protect-the-hdd)
    - [5. Install Ubuntu Server onto the SSD Only](#5-install-ubuntu-server-onto-the-ssd-only)
    - [6. First Boot OS Baseline](#6-first-boot-os-baseline)
    - [7. Networking Setup with Netplan](#7-networking-setup-with-netplan)
      - [DHCP with Router Reservation](#dhcp-with-router-reservation)
      - [Static Address in Netplan](#static-address-in-netplan)
    - [8. SSH Server Setup and Hardening](#8-ssh-server-setup-and-hardening)
    - [9. SSH Client Setup for Outbound Connections](#9-ssh-client-setup-for-outbound-connections)
    - [10. Access the Preserved HDD Safely After Install](#10-access-the-preserved-hdd-safely-after-install)
    - [11. Optional NVIDIA Driver and CUDA Preparation](#11-optional-nvidia-driver-and-cuda-preparation)
  - [Security Considerations](#security-considerations)
    - [Physical and Firmware Security](#physical-and-firmware-security)
    - [OS and Service Hardening](#os-and-service-hardening)
    - [Network Exposure Strategy](#network-exposure-strategy)
  - [Examples](#examples)
    - [Example 1: Disk Inventory Before Installation](#example-1-disk-inventory-before-installation)
    - [Example 2: Static Netplan Configuration](#example-2-static-netplan-configuration)
    - [Example 3: SSH Hardening Drop-In](#example-3-ssh-hardening-drop-in)
    - [Example 4: Mount the Preserved HDD Read-Only First](#example-4-mount-the-preserved-hdd-read-only-first)
    - [Example 5: Install NVIDIA Drivers on a Headless Server](#example-5-install-nvidia-drivers-on-a-headless-server)
  - [Troubleshooting](#troubleshooting)
    - [Installer and Boot Problems](#installer-and-boot-problems)
      - [Problem: The installer sees both disks and you are not sure which one is the SSD](#problem-the-installer-sees-both-disks-and-you-are-not-sure-which-one-is-the-ssd)
      - [Problem: Ubuntu installs, but the system only boots when the HDD is attached](#problem-ubuntu-installs-but-the-system-only-boots-when-the-hdd-is-attached)
      - [Problem: Firmware says no bootable device after installation](#problem-firmware-says-no-bootable-device-after-installation)
    - [Networking Problems](#networking-problems)
      - [Problem: Network is down after editing Netplan](#problem-network-is-down-after-editing-netplan)
      - [Problem: The host can ping IPs but not domain names](#problem-the-host-can-ping-ips-but-not-domain-names)
      - [Problem: Link is unstable or slow](#problem-link-is-unstable-or-slow)
    - [SSH Problems](#ssh-problems)
      - [Problem: Connection refused on port 22](#problem-connection-refused-on-port-22)
      - [Problem: Permission denied (publickey)](#problem-permission-denied-publickey)
      - [Problem: You locked yourself out after hardening SSH](#problem-you-locked-yourself-out-after-hardening-ssh)
    - [Disk and Filesystem Problems](#disk-and-filesystem-problems)
      - [Problem: Preserved NTFS partition will not mount read-write](#problem-preserved-ntfs-partition-will-not-mount-read-write)
      - [Problem: HDD auto-mount breaks boot](#problem-hdd-auto-mount-breaks-boot)
      - [Problem: Root filesystem is unexpectedly full on a 128 GB SSD](#problem-root-filesystem-is-unexpectedly-full-on-a-128-gb-ssd)
    - [NVIDIA and Secure Boot Problems](#nvidia-and-secure-boot-problems)
      - [Problem: Driver installed but `nvidia-smi` fails](#problem-driver-installed-but-nvidia-smi-fails)
      - [Problem: Black screen or unstable console after GPU driver changes](#problem-black-screen-or-unstable-console-after-gpu-driver-changes)
  - [Performance and Tuning](#performance-and-tuning)
    - [Storage and SSD Hygiene](#storage-and-ssd-hygiene)
    - [Memory, Swap, and Logging](#memory-swap-and-logging)
    - [Network Stability and Throughput](#network-stability-and-throughput)
  - [References and Further Reading](#references-and-further-reading)

---

## Quickstart

### Prerequisites

- Ubuntu Server 24.04 LTS ISO downloaded from Canonical
- One USB flash drive of at least 4 GB for the installer
- Physical access to the machine, keyboard, monitor, and BIOS/UEFI settings
- A verified backup of anything on the SSD that must not be lost
- A clear understanding that the SSD will be erased for Ubuntu Server
- Basic router/switch access if you want a DHCP reservation or a known static IP
- Ethernet connection strongly preferred for the initial deployment

### Recommended Deployment Order

1. Back up anything needed from the SSD.
2. Record the exact SSD and HDD model/size so you do not format the wrong device.
3. In firmware, boot in pure UEFI mode and prefer AHCI for SATA storage.
4. Boot the Ubuntu Server installer USB.
5. Use a custom storage layout and touch only the SSD.
6. Create a dedicated EFI System Partition on the SSD so the machine boots independently of the HDD.
7. Install OpenSSH during setup or immediately after first boot.
8. Update the OS, configure networking properly, and harden SSH before exposing the host beyond the local network.
9. Mount the preserved HDD read-only first, inspect it, then decide whether to mount it permanently.

---

## Key Concepts

### Storage Strategy for This Machine

Your machine has a relatively small SSD by server standards, so the correct design is to keep the operating system, packages, logs, and active services on the SSD while leaving the HDD untouched until you explicitly decide how to use it later.

For this specific scenario, the most defensible approach is:

- SSD: fully dedicated to Ubuntu Server 24.04 LTS
- HDD: preserved during installation, not formatted, not reused by the installer, and mounted manually only after the new server is stable

This keeps the operating system clean and makes it possible to reintroduce Windows later without having destroyed the HDD contents.

### UEFI, GPT, and Bootloader Placement

On modern hardware, Ubuntu Server should be installed in UEFI mode using a GPT partition table.

The critical operational detail is this: do not let the installer place the bootloader or reuse an EFI partition on the HDD unless that is explicitly intended. If the SSD is the Ubuntu OS disk, it should also contain:

- a GPT label
- an EFI System Partition (ESP), typically 512 MB to 1 GB, FAT32
- the root filesystem on the remaining space

That way, the machine can boot from the SSD even if the HDD is removed or later repurposed.

### Networking Model on Ubuntu Server 24.04

Ubuntu Server 24.04 uses Netplan as the declarative network configuration layer. On server installs, the backend renderer is commonly `systemd-networkd`.

This means network configuration is usually managed in YAML files under:

```bash
/etc/netplan/
```

Typical patterns are:

- DHCP for initial install or lab environments
- DHCP reservation on the router for stable addressing with minimal host complexity
- Static addressing in Netplan for infrastructure roles where the IP must be explicit and self-contained

### SSH Reception vs SSH Emission

The machine plays two separate SSH roles:

- SSH reception: the server accepts inbound SSH sessions from your laptop/workstation or another management node
- SSH emission: the server itself initiates outbound SSH connections to Git servers, backup targets, HPC nodes, or other Linux machines

These two roles have different requirements:

- Inbound SSH requires `openssh-server`, firewall allowance, and hardened `sshd` policy
- Outbound SSH requires `openssh-client`, proper key management, sane `~/.ssh/config`, and controlled trust of remote host keys

### NVIDIA Considerations on a Headless Server

An RTX 1650 is not required for a normal server install. If you only need a stable headless server, do not install NVIDIA proprietary drivers on day one unless you actually need CUDA, GPU compute, transcoding, or model inference.

Reasons to delay NVIDIA driver installation:

- it introduces kernel module complexity
- Secure Boot can block unsigned module loading
- remote-only machines become harder to recover if driver changes break boot or TTY output

If GPU functionality is required later, install and validate it after the base server is already remotely manageable.

---

## Configuration and Best Practices

### 1. Pre-Install Safety and Data Preservation

Before booting the installer, decide what is allowed to be destroyed.

For your stated requirement, the policy is:

- SSD: may be fully erased and rebuilt for Ubuntu Server
- HDD: must be preserved exactly as-is

Operational best practices:

- If possible, physically disconnect the HDD during installation. This is the safest option by a wide margin.
- If you cannot disconnect it, write down the SSD and HDD model names and capacities exactly before starting.
- Photograph the BIOS storage page or record serial/model information.
- Do not trust `/dev/sda` vs `/dev/sdb` ordering across boots; Linux device names can change.
- Prefer identifying disks by model, serial, and persistent path under `/dev/disk/by-id/`.

If the current machine boots Windows from the SSD and also has Ubuntu-related data on the HDD, that is acceptable. The SSD can be repurposed while preserving the HDD. The installer must be prevented from reusing the HDD EFI partition or overwriting its partition table.

### 2. BIOS/UEFI Firmware Preparation

Before installation, enter firmware setup and verify the following:

- Boot mode: `UEFI` only, not Legacy/CSM if avoidable
- SATA mode: `AHCI` preferred unless storage is intentionally configured as RAID
- Secure Boot: enabled or disabled according to your driver plan
- Boot order: USB installer first for deployment, SSD first after installation
- Fast Boot: preferably disabled during installation and early testing

Recommended policy decisions:

- If you do not need NVIDIA proprietary drivers immediately, leaving Secure Boot enabled is reasonable.
- If you know you will install proprietary NVIDIA drivers very early and do not want to handle MOK enrollment, disabling Secure Boot may simplify operations.
- If the firmware exposes both the SSD and HDD as boot candidates, ensure the SSD becomes the permanent boot target after install.

Update firmware if the vendor provides a stable BIOS update that improves storage or UEFI behavior, but do not combine a BIOS flash and an OS install in the same maintenance window unless necessary.

### 3. Build the Ubuntu Server Installer USB

On Windows, use a reliable tool such as Rufus or balenaEtcher.

Recommended settings for Rufus:

- Boot selection: Ubuntu Server 24.04 LTS ISO
- Partition scheme: `GPT`
- Target system: `UEFI (non CSM)`
- Filesystem: default chosen by Rufus
- Write mode: ISO mode is usually fine unless the ISO specifically requires DD mode

Checksum verification is worth doing for production-minded installs. On Windows PowerShell:

```powershell
Get-FileHash .\ubuntu-24.04-live-server-amd64.iso -Algorithm SHA256
```

Compare the SHA256 output against the checksum published by Canonical.

### 4. Identify the Correct SSD and Protect the HDD

From the installer shell or a live environment, inventory disks before touching storage.

Useful commands:

```bash
lsblk -e7 -o NAME,SIZE,TYPE,FSTYPE,MODEL,SERIAL,MOUNTPOINT
sudo blkid
sudo fdisk -l
ls -l /dev/disk/by-id/
```

For NVMe SSDs:

```bash
sudo apt update
sudo apt install -y nvme-cli
sudo nvme list
```

For SATA health and identity checks:

```bash
sudo apt install -y smartmontools
sudo smartctl -i /dev/sda
```

What you are looking for:

- The 128 GB SSD by model and capacity
- The larger HDD by model and capacity
- Existing filesystems and partitions on the HDD that must remain intact

If the installer UI shows multiple disks and you are not 100% certain which one is the SSD, stop and re-identify the hardware before proceeding.

### 5. Install Ubuntu Server onto the SSD Only

The Ubuntu Server ISO uses the Subiquity installer. During storage configuration, choose the path that gives you full control over the SSD.

Recommended installation flow:

1. Boot the installer in UEFI mode.
2. Configure language, keyboard, and temporary network settings.
3. When storage configuration appears, do not accept a guided layout if it includes or references the HDD.
4. Use a custom storage layout.
5. Select only the SSD.
6. Delete all partitions on the SSD if the SSD is being fully repurposed.
7. Create a new GPT partition table on the SSD.
8. Create a new EFI System Partition on the SSD.
9. Create the root filesystem on the remaining SSD capacity.
10. Leave the HDD entirely untouched.

Recommended SSD layout for this machine:

| Mount point | Size | Filesystem | Notes |
| --- | ---: | --- | --- |
| `/boot/efi` | 512 MB to 1 GB | FAT32 | Must be flagged as EFI System Partition |
| `/` | Remainder of SSD | ext4 or LVM-backed ext4 | Root filesystem for OS and packages |
| swap | swapfile preferred | swapfile | With 16 GB RAM, a swap partition is usually unnecessary |

Practical recommendation:

- Use ext4 on the root filesystem unless you have a strong reason for ZFS.
- Use LVM only if you value future resizing and snapshot flexibility enough to justify the added abstraction.
- For a small single-disk server, plain ext4 on the root partition is simpler and easier to recover.

Important installer cautions:

- If the installer tries to reuse an existing EFI partition on the HDD, do not accept it.
- If you see a proposed boot device that points to the HDD, correct it.
- If the SSD is NVMe, expect names like `/dev/nvme0n1p1`; if SATA, expect `/dev/sda1` style names.
- If the installer presents a checkbox to install OpenSSH, enable it.

User creation guidance:

- Create a named administrative user rather than relying on `root`.
- Use a strong password even if you intend to disable password SSH later.
- If you already have a trusted SSH public key, you can import it during setup, but only do this if you control the source and understand what keys are being imported.

### 6. First Boot OS Baseline

After the first successful boot, establish a clean baseline before doing workload-specific changes.

```bash
sudo apt update
sudo apt full-upgrade -y
sudo apt install -y \
    openssh-server \
    openssh-client \
    ufw \
    curl \
    wget \
    git \
    vim \
    tmux \
    htop \
    btop \
    ethtool \
    lsof \
    net-tools \
    dnsutils \
    smartmontools \
    nvme-cli \
    unattended-upgrades \
    fail2ban \
    acl
```

Set core identity and time settings:

```bash
hostnamectl
sudo hostnamectl set-hostname server01
timedatectl
sudo timedatectl set-timezone Africa/Johannesburg
locale
```

Verify time synchronization:

```bash
timedatectl status
systemctl status systemd-timesyncd
```

Enable automatic security updates:

```bash
sudo dpkg-reconfigure -plow unattended-upgrades
sudo systemctl enable --now unattended-upgrades
```

Useful baseline verification:

```bash
uname -a
lsblk
findmnt /
df -h
free -h
systemctl --failed
journalctl -p 3 -xb
```

### 7. Networking Setup with Netplan

Use Ethernet for the initial build unless you have a compelling reason to run a headless server over Wi-Fi.

First, identify the real interface names:

```bash
ip -br link
networkctl list
lspci -nnk | grep -A3 -E 'Ethernet|Network'
```

On Ubuntu Server 24.04, you will typically find a Netplan file such as:

```bash
/etc/netplan/50-cloud-init.yaml
```

or

```bash
/etc/netplan/00-installer-config.yaml
```

Choose one of the following strategies.

#### DHCP with Router Reservation

This is often the best operational compromise for a home lab or small office server.

- Keep the Ubuntu host on DHCP.
- Reserve a fixed address in the router using the NIC MAC address.
- The server stays simple while still getting a stable IP.

#### Static Address in Netplan

Use this when the machine is infrastructure and its IP must remain defined at the host layer.

Example structure:

```yaml
network:
  version: 2
  renderer: networkd
  ethernets:
    enp3s0:
      dhcp4: false
      addresses:
        - 192.168.1.50/24
      routes:
        - to: default
          via: 192.168.1.1
      nameservers:
        addresses:
          - 1.1.1.1
          - 8.8.8.8
        search:
          - lan
```

Validation workflow:

```bash
sudo netplan generate
sudo netplan try
sudo netplan apply
ip addr show
ip route
resolvectl status
ping -c 4 1.1.1.1
ping -c 4 google.com
```

Netplan best practices:

- Use spaces, not tabs, in YAML.
- Prefer `routes:` over deprecated `gateway4:` syntax.
- Keep one interface definition active until connectivity is confirmed.
- Use `netplan try` before `netplan apply` when working remotely.
- If remote, keep a second active terminal session open before changing networking.

If you have multiple interfaces, bind configuration to the intended NIC carefully. Interface names such as `enp3s0`, `eno1`, or `enx<mac>` are not interchangeable.

### 8. SSH Server Setup and Hardening

Inbound SSH is how the machine becomes operationally useful.

Install and enable the server if it was not selected during setup:

```bash
sudo apt install -y openssh-server
sudo systemctl enable --now ssh
sudo systemctl status ssh --no-pager
sudo ss -tlnp | grep ':22'
```

Allow SSH through the firewall:

```bash
sudo ufw allow OpenSSH
sudo ufw enable
sudo ufw status verbose
```

Create a modern keypair on the client machine that will connect to this server:

```bash
ssh-keygen -t ed25519 -a 100 -C "admin@server01"
```

Install the public key on the server:

```bash
ssh-copy-id youruser@server-ip
```

If `ssh-copy-id` is unavailable on the client:

```bash
mkdir -p ~/.ssh
chmod 700 ~/.ssh
cat ~/id_ed25519.pub >> ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys
```

Create an SSH hardening drop-in instead of editing the main config directly:

```bash
sudo mkdir -p /etc/ssh/sshd_config.d
sudo vim /etc/ssh/sshd_config.d/10-hardening.conf
```

Recommended baseline:

```text
PermitRootLogin no
PasswordAuthentication no
KbdInteractiveAuthentication no
PubkeyAuthentication yes
X11Forwarding no
MaxAuthTries 3
ClientAliveInterval 300
ClientAliveCountMax 2
AllowUsers youruser
```

Validate before restarting:

```bash
sudo sshd -t
sudo systemctl restart ssh
sudo systemctl status ssh --no-pager
```

Critical operational rule: do not close your current SSH session until you have opened and verified a second session successfully.

### 9. SSH Client Setup for Outbound Connections

If this server must reach GitHub, internal Git servers, backup machines, or cluster nodes, configure outbound SSH properly.

Generate a keypair on the server:

```bash
ssh-keygen -t ed25519 -a 100 -f ~/.ssh/id_ed25519 -C "server01-outbound"
```

Recommended permissions:

```bash
chmod 700 ~/.ssh
chmod 600 ~/.ssh/id_ed25519
chmod 644 ~/.ssh/id_ed25519.pub
```

Create a client config:

```bash
vim ~/.ssh/config
```

Example:

```text
Host github.com
    HostName github.com
    User git
    IdentityFile ~/.ssh/id_ed25519
    IdentitiesOnly yes
    ServerAliveInterval 30
    ServerAliveCountMax 3

Host backup-host
    HostName 192.168.1.60
    User backup
    IdentityFile ~/.ssh/id_ed25519
    IdentitiesOnly yes
```

Initialize trust carefully:

```bash
ssh -T git@github.com
ssh-keyscan -H github.com >> ~/.ssh/known_hosts
```

If outbound policy is tightened via firewall, explicitly allow egress TCP 22 to required destinations. By default, UFW permits outgoing traffic unless you change the default policy.

### 10. Access the Preserved HDD Safely After Install

Do not immediately auto-mount preserved disks read-write. First verify what is on them.

Inventory again:

```bash
lsblk -f
sudo blkid
```

Mount the relevant HDD partition read-only first:

```bash
sudo mkdir -p /mnt/preserved-hdd
sudo mount -o ro /dev/sdb1 /mnt/preserved-hdd
findmnt /mnt/preserved-hdd
ls -lah /mnt/preserved-hdd
```

If the HDD partition is NTFS:

```bash
sudo apt install -y ntfs-3g
sudo mount -t ntfs3 -o ro /dev/sdb1 /mnt/preserved-hdd
```

If the mount fails with an unsafe state or hibernation warning, the NTFS volume may still carry a Windows Fast Startup or hibernation flag. Do not force-write to it from Linux unless you accept the recovery risk.

When you are finally ready to mount permanently, use UUIDs and conservative options in `/etc/fstab`.

Example for ext4 data:

```fstab
UUID=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx /srv/data ext4 defaults,nofail,x-systemd.automount 0 2
```

Example for NTFS data mounted cautiously:

```fstab
UUID=XXXX-XXXX /srv/windows-data ntfs3 ro,nofail,uid=1000,gid=1000,x-systemd.automount 0 0
```

Test `fstab` changes safely:

```bash
sudo mount -a
findmnt
```

### 11. Optional NVIDIA Driver and CUDA Preparation

Only do this after networking and SSH are stable.

Inspect GPU state:

```bash
lspci | grep -i nvidia
ubuntu-drivers devices
```

Install the recommended driver:

```bash
sudo ubuntu-drivers autoinstall
sudo reboot
```

Verify after reboot:

```bash
nvidia-smi
lsmod | grep nvidia
```

If Secure Boot is enabled, Ubuntu may require Machine Owner Key enrollment for third-party modules. If the driver appears installed but `nvidia-smi` fails and the module is not loaded, Secure Boot is one of the first things to investigate.

---

## Security Considerations

### Physical and Firmware Security

- Set a firmware password if the server is in a shared physical environment.
- Disable unused boot options if practical.
- Keep USB boot disabled during normal operations after deployment if physical tampering is a concern.
- If the box is remotely located and lacks out-of-band management, think carefully before using full-disk encryption because an unattended reboot may require local console unlock.

On full-disk encryption:

- LUKS is a strong choice if theft of the physical SSD is a real threat.
- For a headless server without IPMI/iDRAC/iLO/KVM, LUKS adds reboot-time operational complexity.
- If uptime and unattended recovery matter more than physical-at-rest protection, many operators choose no root-disk encryption on single-node edge servers.

### OS and Service Hardening

- Keep the system patched with `unattended-upgrades` or disciplined maintenance windows.
- Use SSH keys, not passwords, for administration.
- Disable direct root SSH login.
- Install only the packages you actually need.
- Use `ufw` to expose only necessary ports.
- Consider `fail2ban` if the machine will be reachable from untrusted networks.
- Review `sudo` membership and remove unused accounts.
- Inspect failed services and boot errors after the first few reboots.

Useful commands:

```bash
sudo ufw status verbose
sudo fail2ban-client status
sudo getent group sudo
sudo systemctl --failed
sudo journalctl -p warning -b
```

### Network Exposure Strategy

Do not expose the host to the public internet until the following are true:

- SSH key login works
- password SSH is disabled if that matches your policy
- firewall policy is explicit
- the system clock is correct
- updates have been applied
- the intended static IP or DHCP reservation is stable

If the server is internet-facing, also plan for:

- router port-forwarding discipline
- dynamic DNS or fixed public IP strategy
- reverse proxy or VPN access pattern instead of exposing multiple services directly
- centralized logs or at least disciplined local log review

---

## Examples

### Example 1: Disk Inventory Before Installation

```bash
lsblk -e7 -o NAME,SIZE,TYPE,FSTYPE,MODEL,SERIAL,MOUNTPOINT
sudo fdisk -l
ls -l /dev/disk/by-id/
```

Interpretation pattern:

- confirm which device is the 128 GB SSD
- confirm which device is the HDD to preserve
- confirm whether any existing EFI partition sits on the HDD so you do not accidentally reuse it

### Example 2: Static Netplan Configuration

```yaml
network:
  version: 2
  renderer: networkd
  ethernets:
    enp3s0:
      dhcp4: false
      addresses:
        - 192.168.1.50/24
      routes:
        - to: default
          via: 192.168.1.1
      nameservers:
        addresses:
          - 1.1.1.1
          - 8.8.8.8
          - 9.9.9.9
```

Validation:

```bash
sudo netplan generate
sudo netplan try
sudo netplan apply
ip route
resolvectl status
```

### Example 3: SSH Hardening Drop-In

```text
# /etc/ssh/sshd_config.d/10-hardening.conf
PermitRootLogin no
PasswordAuthentication no
KbdInteractiveAuthentication no
PubkeyAuthentication yes
UsePAM yes
X11Forwarding no
MaxAuthTries 3
LoginGraceTime 30
AllowUsers youruser
```

Validate and reload:

```bash
sudo sshd -t
sudo systemctl restart ssh
```

### Example 4: Mount the Preserved HDD Read-Only First

```bash
lsblk -f
sudo mkdir -p /mnt/preserved-hdd
sudo mount -o ro /dev/sdb2 /mnt/preserved-hdd
findmnt /mnt/preserved-hdd
```

If the data looks correct and healthy, then decide whether a persistent `fstab` entry is appropriate.

### Example 5: Install NVIDIA Drivers on a Headless Server

```bash
ubuntu-drivers devices
sudo ubuntu-drivers autoinstall
sudo reboot
nvidia-smi
```

If `nvidia-smi` fails after reboot, inspect Secure Boot, module loading, and kernel logs:

```bash
mokutil --sb-state
journalctl -k -b | grep -Ei 'nvidia|nouveau|secure'
```

---

## Troubleshooting

### Installer and Boot Problems

#### Problem: The installer sees both disks and you are not sure which one is the SSD

- Stop before modifying storage.
- Use `lsblk`, `fdisk -l`, and `/dev/disk/by-id/` to identify model and capacity.
- If doubt remains, shut down and disconnect the HDD physically.

#### Problem: Ubuntu installs, but the system only boots when the HDD is attached

- The bootloader or EFI files were likely placed on the HDD.
- Reboot from installer media and inspect EFI partitions.
- Corrective action usually means creating an ESP on the SSD and reinstalling GRUB for the SSD boot path.
- Check boot entries with `efibootmgr -v` after recovery.

#### Problem: Firmware says no bootable device after installation

- Verify the installer was booted in UEFI mode, not legacy mode.
- Confirm the SSD contains a FAT32 EFI System Partition.
- Check whether the firmware boot order points to the SSD.
- Use `efibootmgr -v` from rescue mode to inspect or recreate boot entries.

### Networking Problems

#### Problem: Network is down after editing Netplan

- YAML indentation errors are common.
- Interface name may be wrong.
- DNS may be missing even when the link is up.
- Run:

```bash
sudo netplan generate
sudo netplan try
journalctl -u systemd-networkd -b
ip addr
ip route
resolvectl status
```

#### Problem: The host can ping IPs but not domain names

- Routing is working; DNS is not.
- Review the `nameservers` block and `resolvectl status`.
- Test with a known resolver such as `1.1.1.1` or your router DNS.

#### Problem: Link is unstable or slow

- Inspect duplex and negotiated speed:

```bash
sudo ethtool enp3s0
```

- Replace bad cables before blaming Linux.
- Check NIC driver binding with `lspci -nnk`.

### SSH Problems

#### Problem: Connection refused on port 22

- The service may not be installed or running.
- Firewall may be blocking it.
- Validate:

```bash
sudo systemctl status ssh
sudo ss -tlnp | grep ':22'
sudo ufw status verbose
```

#### Problem: Permission denied (publickey)

- The wrong key may be offered.
- `authorized_keys` permissions may be wrong.
- The account name may be wrong.
- Use verbose client output:

```bash
ssh -vvv youruser@server-ip
```

- Confirm on the server:

```bash
chmod 700 ~/.ssh
chmod 600 ~/.ssh/authorized_keys
```

#### Problem: You locked yourself out after hardening SSH

- This is why a second tested session matters.
- Revert the last drop-in from local console access.
- Always run `sshd -t` before restarting the service.

### Disk and Filesystem Problems

#### Problem: Preserved NTFS partition will not mount read-write

- Windows Fast Startup or hibernation likely left the filesystem dirty.
- Mount read-only first.
- If the data is critical, clear the dirty state from Windows rather than forcing Linux writes.

#### Problem: HDD auto-mount breaks boot

- Your `/etc/fstab` entry is too strict.
- Add `nofail` and preferably `x-systemd.automount`.
- Test with `sudo mount -a` before rebooting.

#### Problem: Root filesystem is unexpectedly full on a 128 GB SSD

- Check logs, package cache, container images, and backup artifacts.
- Investigate with:

```bash
df -h
sudo du -xh / | sort -h | tail -n 30
sudo journalctl --disk-usage
```

### NVIDIA and Secure Boot Problems

#### Problem: Driver installed but `nvidia-smi` fails

- Kernel module may not be loaded.
- Secure Boot may have blocked it.
- Inspect:

```bash
lsmod | grep nvidia
mokutil --sb-state
journalctl -k -b | grep -Ei 'nvidia|nouveau|secure'
```

#### Problem: Black screen or unstable console after GPU driver changes

- Prefer doing NVIDIA work only after you have SSH access.
- Keep a recovery plan through GRUB advanced options or installer rescue mode.
- For pure server roles, consider leaving the machine on the default open-source stack unless GPU acceleration is truly needed.

---

## Performance and Tuning

### Storage and SSD Hygiene

- Ensure TRIM is active:

```bash
systemctl status fstrim.timer
```

- If it is disabled:

```bash
sudo systemctl enable --now fstrim.timer
```

- Use SSD space intentionally; 128 GB disappears quickly once logs, containers, and datasets accumulate.
- Keep the HDD for bulk data once you have validated and mounted it correctly.

### Memory, Swap, and Logging

With 16 GB RAM, Ubuntu's default swapfile behavior is usually sufficient.

Operational guidance:

- avoid creating an oversized swap partition
- monitor memory pressure before tuning aggressively
- limit log growth on a small SSD

Useful checks:

```bash
free -h
swapon --show
sudo journalctl --disk-usage
grep -R "^SystemMaxUse" /etc/systemd/journald.conf /etc/systemd/journald.conf.d 2>/dev/null
```

If local logs are consuming too much SSD space, tune `journald` retention.

### Network Stability and Throughput

- Prefer wired Ethernet over Wi-Fi for a physical server.
- Reserve the IP on the router if you want stable addressing without host-side static config complexity.
- Verify the NIC is negotiating expected speed and duplex.
- Use `iperf3` for real throughput testing when needed.

Example:

```bash
sudo apt install -y iperf3
iperf3 -c <target-host>
```

---

## References and Further Reading

- Canonical Ubuntu Server documentation: <https://documentation.ubuntu.com/server/>
- Ubuntu installation guide and Subiquity installer docs: <https://canonical-subiquity.readthedocs-hosted.com/>
- Netplan documentation: <https://netplan.readthedocs.io/>
- OpenSSH documentation: <https://www.openssh.com/manual.html>
- Ubuntu community help on UEFI and GRUB recovery: <https://help.ubuntu.com/community/>

For this machine and installation goal, the single most important operational decision is still the simplest one: keep the HDD out of the installer's blast radius. If you can disconnect it physically during installation, do that. If you cannot, identify disks by model and serial, create a dedicated EFI partition on the SSD, and do not accept any installer action that references the HDD.
