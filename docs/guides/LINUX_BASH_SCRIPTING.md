# Linux Bash shell: automation, execution, and daemons

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
[![OS](https://img.shields.io/badge/System-Linux_GNU-black.svg)](https://www.kernel.org/)
[![CLI](https://img.shields.io/badge/Interpreter-Bash-gray.svg)](https://www.gnu.org/software/bash/)

## Overview

This guide covers Bash scripting with standard input, output, and error streams (`stdin`, `stdout`, `stderr`), background-job scheduling through `cron`, and pipelines that connect commands.

## Contents

- [Linux Bash shell: automation, execution, and daemons](#linux-bash-shell-automation-execution-and-daemons)
  - [Overview](#overview)
  - [Contents](#contents)
  - [1. Configuration (Windows \& Linux)](#1-configuration-windows--linux)
    - [Unix/Linux environments](#unixlinux-environments)
    - [Windows (WSL convergence)](#windows-wsl-convergence)
  - [2. Writing basic scripts (piping \& execution logic)](#2-writing-basic-scripts-piping--execution-logic)
    - [Standard streams and piping](#standard-streams-and-piping)
    - [Strict mode scripts](#strict-mode-scripts)
  - [3. Pre-execution commands (permissions \& validation)](#3-pre-execution-commands-permissions--validation)
    - [The execution bit constraints](#the-execution-bit-constraints)
    - [Carriage return translation](#carriage-return-translation)
  - [4. Runtime commands (cron automation \& daemons)](#4-runtime-commands-cron-automation--daemons)
    - [Daemon execution management](#daemon-execution-management)
    - [The cron scheduler](#the-cron-scheduler)
  - [5. Debugging (trace output \& path traps)](#5-debugging-trace-output--path-traps)
    - [Internal environment tracing](#internal-environment-tracing)
    - [Path variables \& cron failures](#path-variables--cron-failures)

---

## 1. Configuration (Windows & Linux)

The `bash` interpreter executes shell commands and interacts with the Linux kernel.

### Unix/Linux environments

Bash is pre-installed on most Linux distributions. Check its path before writing the shebang line.

```bash
which bash
# Output typically identifies exclusively as /bin/bash or /usr/bin/bash
```

### Windows (WSL convergence)

On Windows, use Windows Subsystem for Linux (WSL) to run Bash in a Linux environment. Opening a Windows command prompt does not start Bash.

```powershell
# Open an elevated PowerShell terminal and install real Linux kernels directly
wsl --install -d Ubuntu
# Proceed to spawn native Bash sessions inside the Windows Host natively
wsl
```

---

## 2. Writing basic scripts (piping & execution logic)

Unix tools commonly perform one task and pass text to other tools through standard streams.

### Standard streams and piping

Bash processes use three standard file descriptors:

1. `stdin (0)`: Input stream via keyboard or incoming pipe logic.
2. `stdout (1)`: Successful execution output text.
3. `stderr (2)`: Error messages and diagnostics.

The Pipe operator (`|`) routes the `stdout` of the left process identically into the `stdin` of the right process.

```bash
#!/bin/bash
# Shebang line enforces interpreter targeting regardless of terminal state

# Example: Read a 5GB log, pipe it to grep filtering strictly for "ERROR",
# then pipe to wc to count the absolute numerical volume of failures.
cat /var/log/syslog | grep "ERROR" | wc -l

# Appending logic onto the end of a physical file
echo "Automation process concluded at $(date)" >> /opt/scripts/status.log

# Rerouting catastrophic errors (stderr descriptor 2) silently into the void (/dev/null)
# to ensure cleaner explicit terminal interfaces.
rm -rf /tmp/orphaned_cache 2> /dev/null
```

### Strict mode scripts

Configure scripts to stop on unhandled errors so later commands do not run with invalid state.

```bash
#!/bin/bash
set -e  # Immediate exit if any downstream command returns a non-zero exit code.
set -o pipefail # Catch failures buried recursively inside complex pipe strings.
set -u  # Throw hard errors upon evaluating undefined environment variables.
```

---

## 3. Pre-execution commands (permissions & validation)

Before running a script, check its execution permissions and line endings.

### The execution bit constraints

A newly created text file usually lacks execute permission. Set the execute bit before running it directly.

```bash
# Verify absolute permissions
ls -la script.sh
# Requires +x execution bindings logically
chmod +x script.sh
```

### Carriage return translation

Windows editors may save files with `\r\n` line endings, while Bash scripts on Linux use `\n`. The extra carriage return can produce `bash: ./script.sh: /bin/bash^M: bad interpreter`.

```bash
# Install tool capable of ripping Windows formatting off natively
sudo apt install dos2unix
dos2unix script.sh
```

---

## 4. Runtime commands (cron automation & daemons)

Run scheduled or long-lived Bash jobs through the appropriate scheduler or background process.

### Daemon execution management

Detach long-running jobs from the SSH session so a dropped connection does not interrupt them.

```bash
# Execute independent physical processes dropping SIGHUP triggers
nohup ./long_running_job.sh > process.log 2>&1 &
```

_The `2>&1` operator redirects `stderr` to `stdout` so both streams reach the same log._

### The cron scheduler

The `crond` daemon runs scheduled jobs. Edit the crontab to set their frequency.

```bash
# Access user-specific tables natively
crontab -e
```

The crontab fields are: `[Minute] [Hour] [Day of Month] [Month] [Day of Week]`

```bash
# Execute strictly at 3:00 AM absolutely every single day.
0 3 * * * /opt/scripts/database_backup.sh >> /var/log/db_backup.log 2>&1

# Execute strictly every 15 minutes globally.
*/15 * * * * /opt/scripts/health_check.sh
```

---

## 5. Debugging (trace output & path traps)

Execution tracing helps you inspect command evaluation and variable values while a script runs.

### Internal environment tracing

Use `-x` to trace evaluated commands and variable expansions during execution.

```bash
# Execute in explicit trace mode over standard script logic
bash -x script.sh
```

```
# Expected output behavior exposing the dynamic variable binding directly:
+ DB_HOST=postgres.internal.net
+ echo 'Connecting strictly to postgres.internal.net'
Connecting strictly to postgres.internal.net
```

### Path variables & cron failures

A script may work in an interactive SSH session but fail under `cron` because the environments differ.

- **The Root Cause:** The interactive shell may add `/usr/local/bin` through `.bashrc`. Jobs run by `cron` use a smaller `$PATH` that may omit locally installed tools such as Node or Python packages.
- **The Resolution:** Use absolute paths for commands and files in the script.

```bash
# FAILURE PRONE (Assumes 'python3' and 'docker' map cleanly to PATH)
python3 manage.py
docker restart web_server

# OPERATIONAL STANDARD (Absolute binaries physically referenced)
/usr/bin/python3 /opt/app/manage.py
/usr/bin/docker restart web_server
```
