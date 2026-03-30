# Windows Application Diagnostics PowerUser Guide

**Last updated**: March 30, 2026<br>
**Author**: [Paul Namalomba](https://github.com/paulnamalomba)<br>
  - SESKA Computational Engineer<br>
  - SEAT Backend Developer<br>
  - Software Developer<br>
  - PhD Candidate (Civil Engineering Spec. Computational and Applied Mechanics)<br>
**Contact**: [kabwenzenamalomba@gmail.com](kabwenzenamalomba@gmail.com)<br>
**Website**: [paulnamalomba.github.io](https://paulnamalomba.github.io)<br>
<br>
[![Framework](https://img.shields.io/badge/OS-Windows-blue.svg)](https://learn.microsoft.com/en-us/windows/)
[![License: MIT](https://img.shields.io/badge/License-MIT-gray.svg)](https://opensource.org/licenses/MIT)

## Overview

When an application decides to take a collective vow of silence across an entire lab, it is rarely a coincidence. Software is rarely that maliciously organized without an underlying systemic cause—usually a pushed update, an aggressive Endpoint Detection and Response (EDR) policy, or a severed dependency. 

Here is a comprehensive, system-level guide to diagnosing application startup failures on Windows 10 and 11 environments, structured to help you trace the failure from the surface GUI down to the bare-metal system calls.

## Contents

- [Windows Application Diagnostics PowerUser Guide](#windows-application-diagnostics-poweruser-guide)
  - [Overview](#overview)
  - [Contents](#contents)
  - [Phase 1: Graphical User Interface (GUI) Methods](#phase-1-graphical-user-interface-gui-methods)
    - [1. The Event Viewer (`eventvwr.msc`)](#1-the-event-viewer-eventvwrmsc)
    - [2. Reliability Monitor (`perfmon /rel`)](#2-reliability-monitor-perfmon-rel)
  - [Phase 2: Command-Line Methods (PowerShell \& CMD)](#phase-2-command-line-methods-powershell--cmd)
    - [1. PowerShell (Versions 5.1 and 7.5+)](#1-powershell-versions-51-and-75)
    - [2. Command Prompt (CMD)](#2-command-prompt-cmd)
  - [Phase 3: System-Level Diagnostics](#phase-3-system-level-diagnostics)
    - [1. Sysinternals Process Monitor (Procmon)](#1-sysinternals-process-monitor-procmon)
    - [2. Advanced: Checking for Silent EDR/Antivirus Kills](#2-advanced-checking-for-silent-edrantivirus-kills)
    - [3. Dependency Walking](#3-dependency-walking)
  - [Lab-Wide Outages](#lab-wide-outages)

---

## Phase 1: Graphical User Interface (GUI) Methods

For quick, visual correlation of failures, the built-in Windows diagnostic GUIs are the first port of call.

### 1. The Event Viewer (`eventvwr.msc`)
The Event Viewer remains the canonical source for application crashes. When an app fails to initialize, the Windows Error Reporting (WER) subsystem usually catches the exception.

* **Execution:** Press `Win + R`, type `eventvwr.msc`, and hit Enter.
* **Target Logs:** Navigate to **Windows Logs** > **Application**.
* **What to Look For:** Filter the log for **Errors** (Red 'X') and look for the following Event IDs:
    * `Event ID 1000`: Application Error (The crash itself. Look at the "Faulting module name" to see if a specific `.dll` is causing the crash).
    * `Event ID 1001`: Windows Error Reporting (WER bucket data).
    * `Event ID 1026`: .NET Runtime Error (Crucial if the application is built on the .NET framework).
* **Systemic Check:** Check **Windows Logs** > **System** for unexpected service terminations or disk/network errors that might be starving the application of resources.

### 2. Reliability Monitor (`perfmon /rel`)
Reliability Monitor aggregates Event Viewer data into a timeline. This is invaluable for lab environments to determine *when* the synchronized failure began and what system changes correlated with it.

* **Execution:** Press `Win + R`, type `perfmon /rel`, and hit Enter.
* **Analysis:** Look for the day the application started failing. Check the lower pane for "Information events" on that exact day—specifically, recent Windows Updates, driver installations, or background software deployments that might have introduced a conflict.

---

## Phase 2: Command-Line Methods (PowerShell & CMD)

For querying multiple lab machines remotely or scripting the diagnostic process, command-line tools are vastly superior to clicking through the Event Viewer.

### 1. PowerShell (Versions 5.1 and 7.5+)
The modern standard for event log querying in PowerShell is `Get-WinEvent`. It is significantly faster than the legacy `Get-EventLog` because it filters at the log-source level rather than retrieving everything and piping it to `Where-Object`. `Get-WinEvent` functions identically across both Windows PowerShell 5.1 and PowerShell Core 7.5+.

**To find the last 10 Application crash events:**
```powershell
Get-WinEvent -FilterHashtable @{LogName='Application'; Level=2; ProviderName='Application Error'} -MaxEvents 10 | 
Select-Object TimeCreated, Id, Message | Format-List
```

**To search for .NET specific crashes:**
```powershell
Get-WinEvent -FilterHashtable @{LogName='Application'; Level=2; ProviderName='.NET Runtime'} -MaxEvents 5 | 
Select-Object TimeCreated, Message | Format-List
```

**To check if an AppLocker or Group Policy is silently killing the app:**
If your lab uses strict execution policies, the app might be getting blocked before it even has a chance to crash.
```powershell
Get-WinEvent -LogName "Microsoft-Windows-AppLocker/EXE and DLL" | Where-Object {$_.LevelDisplayName -eq "Error"}
```

### 2. Command Prompt (CMD)
If PowerShell is restricted or unavailable, `wevtutil` (Windows Events Command Line Utility) is the native executable for querying logs. 

**To retrieve the last 5 Application errors in text format:**
```cmd
wevtutil qe Application /c:5 /f:text /q:"*[System[(Level=2)]] and *[System[Provider[@Name='Application Error']]]"
```

---

## Phase 3: System-Level Diagnostics

When the Event Logs offer nothing but an unhelpful `0xc0000005` (Access Violation) or are entirely empty, the application is likely dying during early initialization before it can write to the OS logs. This requires bringing out the heavy telemetry.

### 1. Sysinternals Process Monitor (Procmon)
Process Monitor captures real-time file system, Registry, and process/thread activity. It is the definitive tool for answering "What exactly was this application doing the millisecond before it died?"

* **Setup:** Download Procmon from Microsoft Sysinternals. Run as Administrator.
* **Filtering (Crucial):** Procmon captures tens of thousands of events per second. You must filter it immediately.
    * Go to **Filter** > **Filter...**
    * Set the condition: `Process Name` `is` `[YourApp.exe]` then click **Include**.
    * *Pro-Tip:* To save memory during debugging, go to **Filter** and check **Drop Filtered Events**.
* **Analysis Strategy:** * Start the capture. Attempt to launch the app. Stop the capture immediately after it fails.
    * Look through the `Result` column. You are hunting for `ACCESS DENIED` (permissions issue), `NAME NOT FOUND` (missing DLLs, config files, or paths), or `FILE LOCKED WITH ONLY READERS`. 
    * In a lab environment, if the app relies on a mapped network drive or a central configuration file, Procmon will instantly highlight the failed UNC path request.

### 2. Advanced: Checking for Silent EDR/Antivirus Kills
Modern EDRs (CrowdStrike, SentinelOne, Microsoft Defender for Endpoint) often kill processes they deem suspicious without notifying the user, and sometimes without writing to the standard Application log.

* Check the specific logs for your EDR solution.
* For Windows Defender, use PowerShell:
    ```powershell
    Get-MpThreatDetection
    ```
    Or check the Event Viewer under: **Applications and Services Logs** > **Microsoft** > **Windows** > **Windows Defender** > **Operational**. Look for Event ID `1116` (Malware detected) or `1117` (Action taken).

### 3. Dependency Walking
If the application relies on specific runtime libraries (C++ Redistributables, specific .NET framework versions) that were accidentally uninstalled or corrupted via a lab-wide script, it will fail silently. Tools like [Dependencies](https://github.com/lucasg/Dependencies) (a modern rewrite of the classic Dependency Walker) can be pointed at the `.exe` to highlight missing `.dll` files in red.

---

## Lab-Wide Outages
Because this is happening on *every* computer simultaneously, you can safely deprioritize local corruption (like a bad sector on a hard drive) and focus your initial diagnostic time on shared variables. The most frequent culprits for synchronous lab failures are:
1.  **Network/Licensing:** The application requires a handshake with a local license server that is currently down or unreachable due to a VLAN change.
2.  **Shared Resources:** The app reads its initial configuration from a network share (`\\lab-server\app-configs\`) that has had its permissions altered.
3.  **Group Policy Updates:** A newly pushed GPO has restricted execution policies or revoked read access to a vital registry key. 

Would you like me to provide a script that can remotely pull and aggregate these specific event logs from a list of the lab computers to pinpoint exactly when the failures began across the network?