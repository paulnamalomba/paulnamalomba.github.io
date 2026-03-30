# Responsive Web Design Testing PowerUser Guide (PowerShell & HTML)

**Last updated**: February 19, 2026<br>
**Author**: [Paul Namalomba](https://github.com/paulnamalomba)<br>
  - SESKA Computational Engineer<br>
  - SEAT Backend Developer<br>
  - Software Developer<br>
  - PhD Candidate (Civil Engineering Spec. Computational and Applied Mechanics)<br>
**Contact**: [kabwenzenamalomba@gmail.com](kabwenzenamalomba@gmail.com)<br>
**Website**: [paulnamalomba.github.io](https://paulnamalomba.github.io)<br>
<br>

[![Framework](https://img.shields.io/badge/Python-3.x-blue.svg)](https://docs.python.org/3/library/http.server.html)
[![Framework](https://img.shields.io/badge/Chrome_DevTools-130+-green.svg)](https://developer.chrome.com/docs/devtools/)
[![License: MIT](https://img.shields.io/badge/License-MIT-gray.svg)](https://opensource.org/licenses/MIT)

## Overview

Responsive web design testing ensures that HTML/CSS sites render correctly across all viewport sizes — from 320px mobile screens to 2560px desktop monitors. This guide covers serving sites locally with Python's built-in HTTP server, using Chrome/Edge/Firefox DevTools for device emulation, building custom HTML-based overflow debuggers, and automating viewport regression testing. Power users need to understand viewport meta tags, CSS media query breakpoints, overflow detection strategies, and local-first testing workflows to catch layout issues **before** deploying to production (e.g., GitHub Pages, Vercel, Netlify).

## Contents

- [Responsive Web Design Testing PowerUser Guide (PowerShell \& HTML)](#responsive-web-design-testing-poweruser-guide-powershell--html)
  - [Overview](#overview)
  - [Contents](#contents)
  - [Quickstart](#quickstart)
  - [Key Concepts](#key-concepts)
  - [Configuration and Best Practices](#configuration-and-best-practices)
  - [Security Considerations](#security-considerations)
  - [Examples](#examples)
    - [Serve a Static Site Locally with Python](#serve-a-static-site-locally-with-python)
    - [Chrome/Edge DevTools Device Emulation](#chromeedge-devtools-device-emulation)
    - [Firefox Responsive Design Mode](#firefox-responsive-design-mode)
    - [Build a Custom HTML Overflow Debugger](#build-a-custom-html-overflow-debugger)
    - [JavaScript Console Overflow Detection Snippet](#javascript-console-overflow-detection-snippet)
    - [CSS Diagnostic Overlay for Development](#css-diagnostic-overlay-for-development)
    - [Automated Viewport Screenshot Testing with Playwright](#automated-viewport-screenshot-testing-with-playwright)
  - [Troubleshooting](#troubleshooting)
  - [Performance and Tuning](#performance-and-tuning)
  - [References and Further Reading](#references-and-further-reading)

---

## Quickstart

1. **Serve locally**: `cd` into your site directory and run `python -m http.server 8080`
2. **Open in browser**: Navigate to `http://localhost:8080`
3. **Toggle device toolbar**: Press `F12` then `Ctrl+Shift+M` in Chrome/Edge
4. **Select a device**: Choose iPhone 12, Galaxy S20, iPad, etc. from the device dropdown
5. **Inspect overflow**: Right-click any element → Inspect → check if `scrollWidth > clientWidth`
6. **Fix and reload**: Edit CSS, save, reload the browser — changes are instant (no deploy needed)

## Key Concepts

- **Viewport**: The visible area of the web page in the browser; controlled by `<meta name="viewport">` tag
- **Media Query**: CSS `@media` rule that applies styles conditionally based on viewport width, height, orientation, or resolution
- **Breakpoint**: A specific viewport width at which the layout changes; common breakpoints are 320px, 480px, 768px, 1024px, 1200px
- **Overflow**: When an element's rendered width or height exceeds its parent container or the viewport, causing horizontal scrollbars
- **Device Pixel Ratio (DPR)**: Ratio of physical pixels to CSS pixels; Retina displays have DPR of 2x or 3x
- **DevTools Device Mode**: Browser feature that simulates mobile viewports, touch events, user agents, and network throttling
- **Local HTTP Server**: A lightweight server that serves files from a directory over HTTP; Python's `http.server` module is the simplest option
- **Viewport Meta Tag**: `<meta name="viewport" content="width=device-width, initial-scale=1.0">` — required for proper mobile rendering
- **Box Model**: CSS layout model where `box-sizing: border-box` includes padding and border in width calculations, preventing overflow
- **Responsive Unit**: CSS units that scale with viewport — `vw`, `vh`, `%`, `rem`, `em` — vs fixed units like `px`

## Configuration and Best Practices

**Viewport Meta Tag** (required in every HTML `<head>`):
```html
<!-- Standard responsive viewport — MUST be present -->
<meta name="viewport" content="width=device-width, initial-scale=1.0">

<!-- Prevent user zoom (accessibility concern — use sparingly) -->
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
```

**CSS Defensive Defaults** (prevent overflow globally):
```css
/* Reset box model — prevents padding from breaking widths */
*, *::before, *::after {
    box-sizing: border-box;
}

/* Prevent horizontal overflow at the root level */
html, body {
    overflow-x: hidden;
    width: 100%;
}

/* Prevent images, videos, and embeds from overflowing */
img, video, iframe, embed, object, pre, code, table {
    max-width: 100%;
}

/* Break long words and URLs that would overflow containers */
body {
    overflow-wrap: break-word;
    word-break: break-word;
}

/* Cards and content containers should clip and wrap */
.card, .panel, .content-block {
    overflow: hidden;
    overflow-wrap: break-word;
}
```

**Common Breakpoint Strategy**:
```css
/* Mobile-first approach — base styles target small screens */

/* Small phones (≤ 400px) */
@media (max-width: 400px) {
    .container { padding: 0 12px; }
}

/* Standard mobile (≤ 768px) */
@media (max-width: 768px) {
    .container { max-width: 100%; padding: 0 16px; }
    .grid { grid-template-columns: 1fr; }
}

/* Tablet (769px – 1024px) */
@media (min-width: 769px) and (max-width: 1024px) {
    .container { max-width: 900px; }
    .grid { grid-template-columns: repeat(2, 1fr); }
}

/* Desktop (≥ 1025px) — default styles apply */

/* Large monitors (≥ 1600px) */
@media (min-width: 1600px) {
    .container { max-width: 1400px; }
}
```

**Python HTTP Server Configuration**:
```powershell
# Basic static server — serves current directory on port 8080
python -m http.server 8080

# Bind to specific interface (useful for testing from phone on same network)
python -m http.server 8080 --bind 0.0.0.0

# Serve from a specific directory
python -m http.server 8080 --directory ./dist

# Use a different port if 8080 is occupied
python -m http.server 3000
```

**Best Practices**:
- Always test locally before deploying to GitHub Pages, Vercel, or Netlify
- Use mobile-first CSS (base styles target smallest screens, media queries add complexity)
- Set `box-sizing: border-box` globally — prevents padding from breaking widths
- Add `overflow-x: hidden` to `html` and `body` as a safety net
- Add `max-width: 100%` to all images and media elements globally
- Use `min()`, `clamp()`, and `%` for fluid widths instead of fixed `px` where possible
- Test at least five widths: 320px, 375px, 768px, 1024px, 1440px
- Use CSS Grid `minmax()` carefully — `minmax(300px, 1fr)` will force 300px minimum on screens <300px
- Always add `overflow-wrap: break-word` to card-like containers with user-generated or dynamic content
- Keep the Python local server running during development to get instant feedback

## Security Considerations

1. **Local Server Binding**: Bind to `127.0.0.1` (default) in untrusted networks; only use `0.0.0.0` on trusted LANs when testing from a phone
2. **Port Exposure**: Python's HTTP server has no authentication; never expose port 8080 to the public internet
3. **Debug Files**: Always `.gitignore` and delete debug/testing HTML files before committing to production
4. **Viewport Manipulation**: Disabling user zoom (`user-scalable=no`) is an accessibility violation (WCAG 1.4.4); avoid unless absolutely required
5. **External Badge/Image Loading**: Shields.io badges and external images can leak visitor IPs and referrer headers; consider self-hosting critical assets
6. **DevTools Network Throttling**: When testing with throttled networks, ensure no sensitive data is transmitted over unencrypted HTTP
7. **Playwright/Puppeteer Scripts**: Headless browser automation tools can execute arbitrary JavaScript; run only trusted test scripts

## Examples

### Serve a Static Site Locally with Python

Launch a local HTTP server to preview your site exactly as it will appear when deployed, without waiting for CI/CD pipelines or GitHub Pages builds.

```powershell
# Navigate to project root
cd "C:\Users\username\projects\my-website"

# Start Python HTTP server on port 8080
python -m http.server 8080

# Output:
# Serving HTTP on :: port 8080 (http://[::]:8080/) ...

# Open in default browser
Start-Process "http://localhost:8080"

# To serve on all interfaces (for testing from phone on same WiFi):
python -m http.server 8080 --bind 0.0.0.0

# Find your local IP to access from phone:
(Get-NetIPAddress -AddressFamily IPv4 -InterfaceAlias "Wi-Fi").IPAddress
# Then open http://<your-ip>:8080 on your phone browser

# Stop the server with Ctrl+C when done
```

**PowerShell Function** (add to `$PROFILE` for reuse):
```powershell
function Start-WebServer {
    param(
        [int]$Port = 8080,
        [string]$Directory = ".",
        [switch]$OpenBrowser,
        [switch]$LAN
    )

    $bind = if ($LAN) { "0.0.0.0" } else { "127.0.0.1" }

    if ($OpenBrowser) {
        Start-Process "http://localhost:$Port"
    }

    Write-Host "Serving '$Directory' on http://${bind}:${Port} ..." -ForegroundColor Cyan
    if ($LAN) {
        $ip = (Get-NetIPAddress -AddressFamily IPv4 -InterfaceAlias "Wi-Fi" -ErrorAction SilentlyContinue).IPAddress
        if ($ip) { Write-Host "LAN access: http://${ip}:${Port}" -ForegroundColor Green }
    }

    python -m http.server $Port --bind $bind --directory $Directory
}

# Usage:
# Start-WebServer                          → localhost:8080
# Start-WebServer -Port 3000               → localhost:3000
# Start-WebServer -OpenBrowser             → opens browser automatically
# Start-WebServer -LAN                     → accessible from phone on same network
# Start-WebServer -LAN -OpenBrowser -Port 5500  → full options
```

### Chrome/Edge DevTools Device Emulation

Use the built-in device emulation in Chromium-based browsers (Chrome, Edge, Brave) to simulate mobile viewports, DPR, touch events, and network throttling.

```text
STEPS:
1. Open your site: http://localhost:8080
2. Press F12 (or Ctrl+Shift+I) to open DevTools
3. Press Ctrl+Shift+M to toggle Device Toolbar (or click the phone/tablet icon)
4. Select a device preset from the dropdown:
   - iPhone SE (375×667, DPR 2)
   - iPhone 12 Pro (390×844, DPR 3)
   - iPhone 14 Pro Max (430×932, DPR 3)
   - Pixel 7 (412×915, DPR 2.625)
   - Galaxy S20 Ultra (412×915, DPR 3.5)
   - iPad Air (820×1180, DPR 2)
   - iPad Pro (1024×1366, DPR 2)
5. Use "Responsive" mode to freely drag the viewport to any width
6. Right-click any element → Inspect → check computed styles and layout
```

**Key DevTools Features for Responsive Testing**:
```text
DEVICE TOOLBAR OPTIONS:
┌─────────────────────────────────────────────────────────────────┐
│  [Device dropdown ▼]  [Width]x[Height]  [DPR ▼]  [Rotate ↻]  │
│                                                                 │
│  Throttle: [No throttling ▼]   [Show media queries]            │
│  [Capture screenshot 📷]  [Capture full-page screenshot]       │
└─────────────────────────────────────────────────────────────────┘

USEFUL PANELS:
- Elements → Computed → look for elements wider than the viewport
- Elements → Layout → Grid/Flexbox overlay visualisation
- Console → run JavaScript overflow detection snippets (see below)
- Network → Throttle to "Slow 3G" to test loading on mobile networks
- Performance → Test rendering performance at mobile CPU speeds

KEYBOARD SHORTCUTS:
- Ctrl+Shift+M    → Toggle device mode
- Ctrl+Shift+C    → Inspect element picker
- Ctrl+Shift+J    → Open Console directly
- Ctrl+]          → Next panel
- Ctrl+[          → Previous panel
```

**Adding Custom Device Profiles**:
```text
1. Open Device Toolbar (Ctrl+Shift+M)
2. Click "Edit..." at the bottom of the device dropdown
3. Click "Add custom device..."
4. Fill in:
   - Name: "Conference Projector 1920x1080"
   - Width: 1920
   - Height: 1080
   - Device Pixel Ratio: 1
   - User Agent: (leave default)
5. Useful custom devices to add:
   - "Galaxy Fold (folded)": 280×653, DPR 3
   - "4K Monitor": 3840×2160, DPR 1
   - "Conference Projector": 1920×1080, DPR 1
   - "Old iPhone SE": 320×568, DPR 2
```

### Firefox Responsive Design Mode

Firefox has a built-in responsive design mode that is independent of DevTools and offers unique features like network throttling and touch simulation.

```text
STEPS:
1. Open your site: http://localhost:8080
2. Press Ctrl+Shift+M to toggle Responsive Design Mode directly
   (No need to open DevTools first — unlike Chrome)
3. Select a device from the dropdown or type custom dimensions
4. Features unique to Firefox:
   - Screenshot button captures the exact viewport
   - Toggle touch simulation independently
   - DPR selector (1x, 2x, 3x)
   - User agent override
   - Network throttling (No throttling, GPRS, 2G, 3G, DSL, WiFi)

KEYBOARD SHORTCUTS:
- Ctrl+Shift+M    → Toggle responsive design mode
- Ctrl+Shift+I    → Open full DevTools
- Ctrl+Shift+K    → Open Web Console
```

### Build a Custom HTML Overflow Debugger

Create a self-contained HTML file that loads your site in a resizable iframe and programmatically scans every DOM element for overflow. This is the most reliable method for finding the exact CSS selectors causing horizontal scroll on mobile.

**Save as `debug-overflow.html` in your project root** (add to `.gitignore`):
```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Mobile Debug — Overflow Detector</title>
    <style>
        body {
            font-family: 'Segoe UI', sans-serif;
            padding: 1rem;
            max-width: 100%;
            background: #f5f5f5;
        }
        h1 { font-size: 1.5rem; margin-bottom: 0.5rem; }
        .panel {
            background: #fff;
            border: 1px solid #ddd;
            border-radius: 8px;
            padding: 1rem;
            margin-bottom: 1rem;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }
        .panel h3 { margin-bottom: 0.5rem; color: #333; }
        iframe {
            width: 100%;
            height: 700px;
            border: 2px solid #0077B5;
            border-radius: 4px;
            background: #fff;
        }
        .controls {
            display: flex;
            gap: 8px;
            flex-wrap: wrap;
            margin-bottom: 1rem;
        }
        button {
            padding: 8px 16px;
            border: 1px solid #ccc;
            background: #fff;
            border-radius: 4px;
            cursor: pointer;
            font-size: 14px;
            transition: all 0.2s;
        }
        button:hover { background: #f0f0f0; }
        button.active {
            background: #0077B5;
            color: #fff;
            border-color: #0077B5;
        }
        #overflow-results {
            max-height: 400px;
            overflow-y: auto;
            font-family: 'Cascadia Code', 'Consolas', monospace;
            font-size: 13px;
            white-space: pre-wrap;
            padding: 0.5rem;
            background: #1e1e1e;
            color: #d4d4d4;
            border-radius: 4px;
        }
        .offender { color: #f44747; font-weight: bold; }
        .ok { color: #6a9955; font-weight: bold; }
        .info { color: #569cd6; }
        .custom-width {
            display: flex;
            align-items: center;
            gap: 8px;
            margin-top: 8px;
        }
        .custom-width input {
            width: 80px;
            padding: 6px 8px;
            border: 1px solid #ccc;
            border-radius: 4px;
            font-size: 14px;
        }
    </style>
</head>
<body>
    <h1>📱 Mobile Overflow Debugger</h1>
    <p>Loads your site in an iframe at mobile widths and detects which
       elements overflow the viewport.</p>

    <div class="panel">
        <h3>Device Presets</h3>
        <div class="controls">
            <button onclick="setWidth(320)">iPhone SE (320px)</button>
            <button onclick="setWidth(375)">iPhone 12 (375px)</button>
            <button onclick="setWidth(390)">iPhone 14 (390px)</button>
            <button onclick="setWidth(412)">Galaxy S21 (412px)</button>
            <button onclick="setWidth(430)">iPhone 14 Pro Max (430px)</button>
            <button onclick="setWidth(768)">iPad Mini (768px)</button>
            <button onclick="setWidth(820)">iPad Air (820px)</button>
            <button onclick="setWidth(1024)">iPad Pro (1024px)</button>
        </div>
        <div class="custom-width">
            <label>Custom:</label>
            <input type="number" id="custom-w" placeholder="px" min="200" max="3840">
            <button onclick="setWidth(+document.getElementById('custom-w').value)">
                Apply
            </button>
        </div>
        <p style="margin-top:8px">
            Current width: <strong id="current-width">375px</strong>
        </p>
    </div>

    <div class="panel">
        <h3>🔍 Overflow Scan</h3>
        <button onclick="scanOverflow()"
                style="background:#0077B5; color:#fff; margin-bottom:0.5rem;">
            Run Overflow Scan
        </button>
        <button onclick="scanAllWidths()"
                style="background:#2c3e50; color:#fff; margin-bottom:0.5rem;">
            Scan ALL Presets
        </button>
        <div id="overflow-results">
Click "Run Overflow Scan" after selecting a device width…</div>
    </div>

    <div class="panel">
        <h3>Preview</h3>
        <iframe id="preview" src="index.html"></iframe>
    </div>

    <script>
        const iframe   = document.getElementById('preview');
        const label    = document.getElementById('current-width');
        const results  = document.getElementById('overflow-results');
        const presets  = [320, 375, 390, 412, 430, 768, 820, 1024];

        /* ---------- viewport helpers ---------- */
        function setWidth(w) {
            if (!w || w < 200) return;
            iframe.style.width = w + 'px';
            label.textContent  = w + 'px';
            document.querySelectorAll('.controls button').forEach(b =>
                b.classList.toggle('active', b.textContent.includes(w + 'px'))
            );
        }

        /* ---------- single-width scan ---------- */
        function scanOverflow() {
            try {
                const doc = iframe.contentDocument
                         || iframe.contentWindow.document;
                const vw  = iframe.clientWidth;
                const all = doc.querySelectorAll('*');
                let hits  = [];

                all.forEach(el => {
                    const r = el.getBoundingClientRect();
                    if (r.right > vw + 1) {
                        const tag = el.tagName.toLowerCase();
                        const id  = el.id ? '#' + el.id : '';
                        const cls = (typeof el.className === 'string' && el.className)
                            ? '.' + el.className.trim().split(/\s+/).join('.')
                            : '';
                        hits.push({
                            sel : tag + id + cls,
                            over: Math.round(r.right - vw),
                            w   : Math.round(r.width),
                            txt : (el.textContent || '').substring(0, 60).trim()
                        });
                    }
                });

                if (!hits.length) {
                    results.innerHTML =
                        `<span class="ok">✅ No overflow at ${vw}px</span>`;
                    return [];
                }

                /* de-duplicate, sort descending */
                const seen = new Set(), uniq = [];
                hits.sort((a, b) => b.over - a.over);
                hits.forEach(h => {
                    if (!seen.has(h.sel)) { seen.add(h.sel); uniq.push(h); }
                });

                let html = `<span class="offender">⚠️  ${uniq.length} overflowing `
                          + `element(s) at ${vw}px:</span>\n\n`;
                uniq.forEach((o, i) => {
                    html += `<span class="offender">${i+1}. ${o.sel}</span>\n`;
                    html += `   <span class="info">overflows by ${o.over}px  `
                          + `(element width: ${o.w}px)</span>\n`;
                    if (o.txt)
                        html += `   text: "${o.txt.substring(0,50)}…"\n`;
                    html += '\n';
                });
                results.innerHTML = html;
                return uniq;
            } catch (e) {
                results.innerHTML = 'Error: ' + e.message;
                return [];
            }
        }

        /* ---------- multi-width scan ---------- */
        async function scanAllWidths() {
            let report = '<span class="info">━━━ Full Preset Scan ━━━</span>\n\n';
            for (const w of presets) {
                setWidth(w);
                await new Promise(r => setTimeout(r, 300));   // let reflow
                const hits = scanOverflow();
                if (!hits.length) {
                    report += `<span class="ok">✅ ${w}px — clean</span>\n`;
                } else {
                    report += `<span class="offender">⚠️  ${w}px — `
                            + `${hits.length} offender(s)</span>\n`;
                    hits.forEach(h => {
                        report += `   ${h.sel}  (+${h.over}px)\n`;
                    });
                }
                report += '\n';
            }
            results.innerHTML = report;
        }

        /* default to iPhone 12 */
        setWidth(375);
    </script>
</body>
</html>
```

**Usage**:
```powershell
# 1. Place debug-overflow.html in the same directory as index.html
# 2. Start local server
python -m http.server 8080

# 3. Open the debugger
Start-Process "http://localhost:8080/debug-overflow.html"

# 4. Click device preset buttons, then "Run Overflow Scan"
#    — or click "Scan ALL Presets" for a full multi-width report

# 5. The scan reports CSS selectors that overflow, e.g.:
#    ⚠️ 3 overflowing element(s) at 375px:
#    1. div.badges
#       overflows by 42px (element width: 417px)
#    2. section#skills.container
#       overflows by 42px (element width: 417px)

# 6. Fix the CSS, save, reload the debugger — repeat until clean

# 7. IMPORTANT: Delete or .gitignore the file before committing
Remove-Item debug-overflow.html
# Or add to .gitignore:
Add-Content .gitignore "`ndebug-overflow.html"
```

### JavaScript Console Overflow Detection Snippet

Paste this directly into the browser console (F12 → Console) when viewing your site in device mode. No extra files needed.

```javascript
// Paste into DevTools Console while in device emulation mode
// Reports every element whose right edge exceeds the viewport

(function findOverflow() {
    const vw = document.documentElement.clientWidth;
    const all = document.querySelectorAll('*');
    const offenders = [];

    all.forEach(el => {
        const rect = el.getBoundingClientRect();
        if (rect.right > vw + 1) {
            offenders.push({
                element: el,
                selector: el.tagName.toLowerCase()
                    + (el.id ? '#' + el.id : '')
                    + (el.className && typeof el.className === 'string'
                        ? '.' + el.className.trim().split(/\s+/).join('.')
                        : ''),
                overflowPx: Math.round(rect.right - vw),
                width: Math.round(rect.width)
            });
        }
    });

    if (!offenders.length) {
        console.log('%c✅ No overflow detected at ' + vw + 'px',
                    'color:green; font-weight:bold');
        return;
    }

    console.group(`%c⚠️ ${offenders.length} overflowing elements at ${vw}px`,
                   'color:red; font-weight:bold');
    offenders
        .sort((a, b) => b.overflowPx - a.overflowPx)
        .forEach((o, i) => {
            console.log(
                `${i + 1}. %c${o.selector}%c  +${o.overflowPx}px (width: ${o.width}px)`,
                'color:#d63384; font-weight:bold',
                'color:inherit'
            );
            console.log('   ', o.element);  // clickable element reference
        });
    console.groupEnd();
})();
```

**Usage**:
```text
1. Open http://localhost:8080 in Chrome/Edge
2. Press F12 → Ctrl+Shift+M → select a mobile device
3. Switch to the Console tab
4. Paste the snippet above and press Enter
5. Click any logged element reference to jump to it in the Elements panel
6. The element is highlighted on the page — inspect its CSS to find the cause
```

### CSS Diagnostic Overlay for Development

Add a temporary CSS file that outlines every element with a coloured border, making overflow visually obvious without any JavaScript.

**Save as `debug.css`** (link it temporarily in `<head>`):
```css
/* debug.css — TEMPORARY — remove before committing */

/* Outline every element to see box boundaries */
* {
    outline: 1px solid rgba(255, 0, 0, 0.15) !important;
}

/* Highlight elements that might overflow */
img, video, iframe, table, pre, code, .badges, .grid, .card {
    outline: 2px solid rgba(0, 100, 255, 0.4) !important;
}

/* Show viewport boundary — red right border */
body::after {
    content: '';
    position: fixed;
    top: 0;
    right: 0;
    width: 2px;
    height: 100vh;
    background: red;
    z-index: 99999;
    pointer-events: none;
}

/* Show container boundaries */
.container {
    outline: 2px dashed rgba(0, 200, 0, 0.5) !important;
}
```

**Usage**:
```html
<!-- Add temporarily to <head> for debugging — remove before deploy -->
<link rel="stylesheet" href="debug.css">
```

```powershell
# Quick toggle: add debug.css to head
# When done, remove the <link> tag and delete the file
Remove-Item debug.css
```

### Automated Viewport Screenshot Testing with Playwright

Use Microsoft Playwright to programmatically capture screenshots at multiple viewport sizes. This is useful for regression testing — run it after every CSS change to verify nothing breaks.

**Install Playwright**:
```powershell
# Install Playwright with pip
pip install playwright

# Install browser binaries (Chromium, Firefox, WebKit)
python -m playwright install
```

**Save as `test_responsive.py`**:
```python
"""
Automated responsive screenshot testing with Playwright.
Captures screenshots at multiple viewport sizes and detects overflow.
Run: python test_responsive.py
"""

import asyncio
from playwright.async_api import async_playwright

URL = "http://localhost:8080"
OUTPUT_DIR = "./screenshots"

VIEWPORTS = [
    {"name": "iPhone_SE",       "width": 320,  "height": 568,  "dpr": 2},
    {"name": "iPhone_12",       "width": 375,  "height": 812,  "dpr": 3},
    {"name": "iPhone_14",       "width": 390,  "height": 844,  "dpr": 3},
    {"name": "Galaxy_S21",      "width": 412,  "height": 915,  "dpr": 2.625},
    {"name": "iPad_Mini",       "width": 768,  "height": 1024, "dpr": 2},
    {"name": "iPad_Air",        "width": 820,  "height": 1180, "dpr": 2},
    {"name": "Desktop_1080p",   "width": 1920, "height": 1080, "dpr": 1},
]

OVERFLOW_JS = """
() => {
    const vw = document.documentElement.clientWidth;
    const offenders = [];
    document.querySelectorAll('*').forEach(el => {
        const r = el.getBoundingClientRect();
        if (r.right > vw + 1) {
            offenders.push({
                tag: el.tagName.toLowerCase(),
                id: el.id || null,
                classes: el.className || null,
                overflowPx: Math.round(r.right - vw),
                width: Math.round(r.width)
            });
        }
    });
    return offenders;
}
"""


async def main():
    import os
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        print(f"Testing {URL} across {len(VIEWPORTS)} viewports...\n")

        all_clean = True

        for vp in VIEWPORTS:
            ctx = await browser.new_context(
                viewport={"width": vp["width"], "height": vp["height"]},
                device_scale_factor=vp["dpr"],
            )
            page = await ctx.new_page()
            await page.goto(URL, wait_until="networkidle")

            # Full-page screenshot
            path = f"{OUTPUT_DIR}/{vp['name']}_{vp['width']}x{vp['height']}.png"
            await page.screenshot(path=path, full_page=True)

            # Overflow detection
            offenders = await page.evaluate(OVERFLOW_JS)

            if offenders:
                all_clean = False
                print(f"⚠️  {vp['name']} ({vp['width']}px): "
                      f"{len(offenders)} overflow(s)")
                for o in offenders[:5]:
                    sel = o["tag"]
                    if o["id"]:
                        sel += f"#{o['id']}"
                    if o["classes"]:
                        sel += "." + ".".join(o["classes"].split())
                    print(f"     {sel}  +{o['overflowPx']}px")
            else:
                print(f"✅ {vp['name']} ({vp['width']}px): clean")

            await ctx.close()

        await browser.close()
        print("\n" + ("✅ ALL VIEWPORTS CLEAN" if all_clean
                      else "⚠️  OVERFLOW DETECTED — see above"))
        print(f"Screenshots saved to {OUTPUT_DIR}/")


if __name__ == "__main__":
    asyncio.run(main())
```

**Usage**:
```powershell
# 1. Start local server in one terminal
python -m http.server 8080

# 2. Run tests in another terminal
python test_responsive.py

# Output:
# Testing http://localhost:8080 across 7 viewports...
#
# ✅ iPhone_SE (320px): clean
# ✅ iPhone_12 (375px): clean
# ⚠️  Galaxy_S21 (412px): 2 overflow(s)
#      div.badges  +42px
#      section#skills.container  +42px
# ✅ iPad_Mini (768px): clean
# ✅ iPad_Air (820px): clean
# ✅ Desktop_1080p (1920px): clean
#
# ⚠️  OVERFLOW DETECTED — see above
# Screenshots saved to ./screenshots/

# 3. Review screenshots visually
explorer.exe .\screenshots
```

## Troubleshooting

| Problem | Cause | Solution |
| ------- | ----- | -------- |
| Horizontal scrollbar on mobile | Element wider than viewport | Run overflow scan → find the selector → add `max-width: 100%` or `overflow: hidden` |
| `python -m http.server` not found | Python not in PATH or wrong alias | Use `python3 -m http.server` or check `Get-Command python` |
| Port 8080 already in use | Another process occupies the port | Use a different port: `python -m http.server 3000` or kill the process: `Get-Process -Id (Get-NetTCPConnection -LocalPort 8080).OwningProcess \| Stop-Process` |
| Iframe blocked in debug tool | Same-origin policy or X-Frame-Options | Serve both files from the same local server (same origin) |
| DevTools device mode shows desktop | Viewport meta tag missing | Add `<meta name="viewport" content="width=device-width, initial-scale=1.0">` to `<head>` |
| CSS changes not reflecting | Browser cache | Hard reload with `Ctrl+Shift+R` or disable cache in DevTools (Network → Disable cache) |
| Grid `minmax(300px, 1fr)` overflows | Minimum 300px wider than viewport on small phones | Override in media query: `@media (max-width: 768px) { .grid { grid-template-columns: 1fr; } }` |
| Badges/shield images overflow | Flex container doesn't constrain image widths | Add `max-width: 100%` to `.badges` and `.badges img { height: auto; max-width: 100%; }` |
| Long URLs/emails break layout | No word-break on container | Add `overflow-wrap: break-word; word-break: break-word;` to the parent container |
| `<code>` blocks overflow cards | Monospace text doesn't wrap by default | Add `code { word-break: break-all; max-width: 100%; }` |
| Phone can't access local server | Server bound to 127.0.0.1 only | Use `--bind 0.0.0.0` and connect via LAN IP |
| Playwright screenshots are blank | Page not fully loaded | Use `wait_until="networkidle"` or add `await page.wait_for_timeout(2000)` |

## Performance and Tuning

**Python HTTP Server Alternatives** (for faster local serving):
```powershell
# Python http.server is single-threaded — fine for testing, not production

# Alternative: Node.js live-server (auto-reloads on file changes)
npx live-server --port=8080

# Alternative: VS Code Live Server extension
# Install: ext install ritwickdey.LiveServer
# Right-click index.html → "Open with Live Server"

# Alternative: PHP built-in server
php -S localhost:8080
```

**DevTools Performance Tips**:
```text
- Enable "Disable cache" in Network tab during development
- Use "Capture screenshots" in Performance tab to see rendering at each frame
- CPU throttling: 4x or 6x slowdown simulates mobile CPU performance
- Network throttling: "Slow 3G" simulates real mobile network conditions
- Lighthouse: Run in DevTools (Lighthouse tab) for a full mobile audit score
```

**CSS Performance for Responsive Layouts**:
```css
/* Use will-change sparingly for animated responsive transitions */
.card {
    will-change: transform;
}

/* Prefer transform over changing width/left for animations */
.slide-in {
    transform: translateX(0);
    transition: transform 0.3s ease;
}

/* Use contain for complex card layouts to limit reflow */
.card {
    contain: layout style;
}

/* Avoid expensive selectors in media queries */
/* ❌ Bad: */ * > div.card:nth-child(odd) ul li { }
/* ✅ Good: */ .card-item { }
```

**Playwright Performance Tips**:
```python
# Run tests in parallel across browsers
async with async_playwright() as p:
    browsers = await asyncio.gather(
        p.chromium.launch(),
        p.firefox.launch(),
        p.webkit.launch(),
    )
    # Test each viewport on all three engines simultaneously

# Skip full-page screenshots if only checking overflow
await page.screenshot(path=path, full_page=False)  # faster

# Reuse browser context for same-viewport tests
ctx = await browser.new_context(viewport={"width": 375, "height": 812})
for url in urls:
    page = await ctx.new_page()
    await page.goto(url)
    # ... test ...
    await page.close()
```

## References and Further Reading

- [Chrome DevTools Device Mode](https://developer.chrome.com/docs/devtools/device-mode/) - Official Chromium device emulation documentation
- [Firefox Responsive Design Mode](https://firefox-source-docs.mozilla.org/devtools-user/responsive_design_mode/) - Mozilla responsive testing documentation
- [Python http.server](https://docs.python.org/3/library/http.server.html) - Python standard library HTTP server reference
- [MDN Responsive Design](https://developer.mozilla.org/en-US/docs/Learn/CSS/CSS_layout/Responsive_Design) - Comprehensive responsive web design guide
- [CSS Media Queries Level 4](https://www.w3.org/TR/mediaqueries-4/) - W3C specification for media queries
- [Playwright Documentation](https://playwright.dev/python/docs/intro) - Microsoft Playwright for Python — automated browser testing
- [Google Lighthouse](https://developer.chrome.com/docs/lighthouse/) - Automated auditing for performance, accessibility, and responsive design
- [Can I Use](https://caniuse.com/) - Browser support tables for CSS features, media queries, and viewport units
- [Responsively App](https://responsively.app/) - Open-source tool that displays your site at multiple viewports simultaneously
- [VS Code Live Server](https://marketplace.visualstudio.com/items?itemName=ritwickdey.LiveServer) - VS Code extension for live-reloading local server
