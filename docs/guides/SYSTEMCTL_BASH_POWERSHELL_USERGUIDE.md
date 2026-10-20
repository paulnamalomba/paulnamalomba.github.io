# Service and process management guide: Bash vs. PowerShell

**Last updated**: December 18, 2025<br>
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

This guide provides a comparative technical reference for managing system services and processes in Linux (via Bash/Systemd) and Windows (via PowerShell). It covers essential commands and concepts for both operating systems, focusing on service control, process management, and best practices.

## Contents

- [Service and process management guide: Bash vs. PowerShell](#service-and-process-management-guide-bash-vs-powershell)
  - [Overview](#overview)
  - [Contents](#contents)
  - [Part 1: system services management](#part-1-system-services-management)
    - [1.1 Linux: Systemd (`systemctl`)](#11-linux-systemd-systemctl)
      - [Basic service control](#basic-service-control)
      - [Boot management](#boot-management)
      - [Logging (journalctl)](#logging-journalctl)
    - [1.2 Windows: PowerShell service cmdlets](#12-windows-powershell-service-cmdlets)
      - [Basic service control](#basic-service-control-1)
      - [Boot management (startup types)](#boot-management-startup-types)
  - [Part 2: process control \& supervisor](#part-2-process-control--supervisor)
    - [2.1 Linux: supervisor (`supervisorctl`)](#21-linux-supervisor-supervisorctl)
      - [Key commands](#key-commands)
    - [2.2 Windows: PowerShell process management](#22-windows-powershell-process-management)
      - [Native process cmdlets](#native-process-cmdlets)
      - [Advanced inspection (WMI/CIM)](#advanced-inspection-wmicim)
      - [Architectural equivalents to supervisor](#architectural-equivalents-to-supervisor)
  - [Part 3: service configuration \& dependencies](#part-3-service-configuration--dependencies)
    - [3.1 Linux: Systemd unit files](#31-linux-systemd-unit-files)
      - [Anatomy of a unit file](#anatomy-of-a-unit-file)
    - [3.2 Windows: service dependencies \& recovery](#32-windows-service-dependencies--recovery)
      - [Managing dependencies](#managing-dependencies)
      - [Service recovery (Auto-Restart)](#service-recovery-auto-restart)
  - [Part 4: background jobs \& process priority](#part-4-background-jobs--process-priority)
    - [4.1 Linux: job control \& nice](#41-linux-job-control--nice)
      - [Shell job control](#shell-job-control)
      - [Process priority (nice)](#process-priority-nice)
    - [4.2 Windows: PowerShell jobs \& priority](#42-windows-powershell-jobs--priority)
      - [PowerShell jobs](#powershell-jobs)
      - [Process priority](#process-priority)

---

## Part 1: system services management

This section covers the management of background services (daemons in Linux, Services in Windows).

### 1.1 Linux: Systemd (`systemctl`)

`systemd` is the init system and service manager for most modern Linux distributions. `systemctl` is the primary command-line utility for introspection and control.

#### Basic service control

The generic syntax is `sudo systemctl [command] [service_name]`.

- **Start a service:**
  ```bash
  sudo systemctl start nginx
  ```
- **Stop a service:**
  ```bash
  sudo systemctl stop nginx
  ```
- **Restart a service:** (Stops and then starts)
  ```bash
  sudo systemctl restart nginx
  ```
- **Reload configuration:** (Reloads config without dropping connections, if supported)
  ```bash
  sudo systemctl reload nginx
  ```
- **Check status:** (Shows active state, PIDs, and recent logs)
  ```bash
  systemctl status nginx
  ```

#### Boot management

Controls whether a service launches automatically when the OS boots.

- **Enable at boot:** (Creates symlinks)
  ```bash
  sudo systemctl enable nginx
  ```
- **Disable at boot:** (Removes symlinks)
  ```bash
  sudo systemctl disable nginx
  ```
- **Check if enabled:**
  ```bash
  systemctl is-enabled nginx
  ```

#### Logging (journalctl)

`systemd` uses a binary logger called the journal.

- **View logs for a specific service:**
  ```bash
  # -u = unit, -f = follow (tail), -n = number of lines
  journalctl -u nginx -f -n 50
  ```

---

### 1.2 Windows: PowerShell service cmdlets

PowerShell uses the `*-Service` noun for service management.

#### Basic service control

- **Get Service Status:**
  ```powershell
  Get-Service -Name W3SVC
  ```
- **Start a service:**
  ```powershell
  Start-Service -Name W3SVC
  ```
- **Stop a service:**
  ```powershell
  Stop-Service -Name W3SVC
  ```
- **Restart a service:**
  ```powershell
  Restart-Service -Name W3SVC
  ```
- **Filtering Services:**
  PowerShell allows object-based filtering rather than text grep.
  ```powershell
  # Find all running services starting with 'W'
  Get-Service | Where-Object { $_.Status -eq 'Running' -and $_.Name -like 'W*' }
  ```

#### Boot management (startup types)

Windows uses "Startup Types" (Automatic, Manual, Disabled) rather than just enable/disable flags.

- **Set to Automatic (Enable at boot):**
  ```powershell
  Set-Service -Name W3SVC -StartupType Automatic
  ```
- **Set to Disabled (Disable at boot):**
  ```powershell
  Set-Service -Name W3SVC -StartupType Disabled
  ```
- **Set to Manual:**
  ```powershell
  Set-Service -Name W3SVC -StartupType Manual
  ```

---

## Part 2: process control & supervisor

This section compares the Linux `supervisor` tool (process control system) with Windows process management.

### 2.1 Linux: supervisor (`supervisorctl`)

Supervisor is a client/server system that allows its users to monitor and control a number of processes on UNIX-like operating systems. It is often used to keep applications running (respawning them if they crash).

#### Key commands

- **Enter Interactive Shell:**
  ```bash
  sudo supervisorctl
  ```
- **Check Status of All Processes:**
  ```bash
  sudo supervisorctl status
  ```
- **Start/Stop specific process:**
  ```bash
  sudo supervisorctl start my_app_worker
  sudo supervisorctl stop my_app_worker
  ```
- **Restart specific process:**
  ```bash
  sudo supervisorctl restart my_app_worker
  ```
- **Reload Config (Reread & Update):**
  - `reread`: Reloads the configuration files but doesn't restart processes.
  - `update`: Restarts processes whose configuration has changed.
  ```bash
  sudo supervisorctl reread
  sudo supervisorctl update
  ```
- **Tail Logs:**
  Supervisor captures stdout/stderr.
  ```bash
  sudo supervisorctl tail -f my_app_worker
  ```

---

### 2.2 Windows: PowerShell process management

**Note:** Windows does not have a built-in 1:1 equivalent to Supervisor for _process grouping_ and _automatic respawning_ without external tools. Native PowerShell commands interact directly with the OS process table.

#### Native process cmdlets

- **List Processes:**
  ```powershell
  # Equivalent to 'ps aux' or 'top'
  Get-Process
  ```
- **Find Specific Process:**
  ```powershell
  Get-Process -Name chrome
  # Or via ID
  Get-Process -Id 4520
  ```
- **Stop (Kill) Process:**
  ```powershell
  Stop-Process -Name notepad
  # Force kill
  Stop-Process -Name notepad -Force
  ```
- **Start a Process:**
  ```powershell
  Start-Process -FilePath "C:\Path\To\App.exe" -ArgumentList "-config config.json"
  ```

#### Advanced inspection (WMI/CIM)

`Get-Process` does not show the full command line arguments by default. You need WMI or CIM for this.

- **Get Command Line Arguments:**
  ```powershell
  Get-CimInstance Win32_Process | Select-Object ProcessId, Name, CommandLine | Format-List
  ```

#### Architectural equivalents to supervisor

To achieve "keep-alive" functionality (respawning apps if they crash) on Windows, you typically wrap the executable as a Windows Service.

1.  **NSSM (Non-Sucking Service Manager):**
    The industry standard 3rd-party tool for running arbitrary .exe files as services.

    ```powershell
    # Installation (if nssm is in path)
    nssm install MyAppService "C:\path\to\app.exe"
    nssm set MyAppService AppDirectory "C:\path\to"
    nssm start MyAppService
    ```

2.  **Native `New-Service`:**
    Can create services, but the executable must strictly implement the Windows Service API (unlike NSSM which handles the API wrapper).
    ```powershell
    New-Service -Name "MyApp" -BinaryPathName "C:\path\to\service-compatible-app.exe" -StartupType Automatic
    ```

---

## Part 3: service configuration & dependencies

Service definitions and dependencies determine startup order and affect system stability.

### 3.1 Linux: Systemd unit files

In Systemd, services are defined in `.service` files (Unit files), typically located in `/etc/systemd/system/`.

#### Anatomy of a unit file

A basic service file (`/etc/systemd/system/myapp.service`) looks like this:

```ini
[Unit]
Description=My Custom App
After=network.target postgresql.service  # Start after these
Requires=postgresql.service              # Strong dependency

[Service]
Type=simple
User=www-data
ExecStart=/usr/bin/python3 /opt/myapp/main.py
Restart=on-failure                       # Auto-restart if crashes
RestartSec=5s

[Install]
WantedBy=multi-user.target               # Enable for standard multi-user runlevel
```

- **Reloading Daemon:** After editing a unit file, you must run:
  ```bash
  sudo systemctl daemon-reload
  ```

### 3.2 Windows: service dependencies & recovery

Windows services store configuration in the Registry. While `Set-Service` covers basics, `sc.exe` (Service Control) or WMI is often needed for advanced configuration.

#### Managing dependencies

- **View Dependencies (PowerShell):**
  ```powershell
  # Services that depend on 'LanmanWorkstation'
  Get-Service -Name LanmanWorkstation -DependentServices

  # Services that 'LanmanWorkstation' depends on
  Get-Service -Name LanmanWorkstation -RequiredServices
  ```

#### Service recovery (Auto-Restart)

Configuring a service to restart automatically upon failure is common. PowerShell's `Set-Service` doesn't expose recovery options directly; use `sc.exe` (legacy but effective) or CIM.

- **Configure Restart on Failure (cmd/sc.exe):**
  ```powershell
  # Set failure actions: Restart after 1st, 2nd, and subsequent failures (delay 60s)
  sc.exe failure "W3SVC" reset= 86400 actions= restart/60000/restart/60000/restart/60000
  ```

---

## Part 4: background jobs & process priority

Managing ad-hoc background tasks and system resource allocation.

### 4.1 Linux: job control & nice

#### Shell job control

Bash allows running commands in the background of the current shell session.

- **Start in background:** Append `&`
  ```bash
  long_running_script.sh &
  ```
- **List jobs:**
  ```bash
  jobs
  ```
- **Bring to foreground:**
  ```bash
  fg %1
  ```

#### Process priority (nice)

- **Start with lower priority:** (Higher nice value = lower priority, range -20 to 19)
  ```bash
  nice -n 10 ./backup.sh
  ```
- **Change priority of running process:**
  ```bash
  renice -n 10 -p 1234
  ```

### 4.2 Windows: PowerShell jobs & priority

#### PowerShell jobs

PowerShell jobs run in a separate process (wsmprovhost.exe), allowing the main console to remain responsive.

- **Start a Job:**
  ```powershell
  $job = Start-Job -ScriptBlock { Get-ChildItem -Recurse C:\Windows }
  ```
- **Check Status:**
  ```powershell
  Get-Job
  ```
- **Get Results:** (Removes data from queue unless -Keep is used)
  ```powershell
  Receive-Job -Job $job
  ```

#### Process priority

You can adjust the `PriorityClass` of a process object.

- **Set Priority:**
  ```powershell
  $proc = Get-Process -Name "notepad"
  $proc.PriorityClass = "BelowNormal" # Options: Idle, BelowNormal, Normal, AboveNormal, High, RealTime
  ```

---

_This guide covers service and process management on Linux and Windows._
