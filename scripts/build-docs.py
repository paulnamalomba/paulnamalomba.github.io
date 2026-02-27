#!/usr/bin/env python3
"""
build-docs.py — Local build script for paulnamalomba.github.io docs pages.

Replaces the deploy-docs.yml GitHub Action workflow.  Run from the repo root:

    python scripts/build-docs.py

Requires: pip install markdown pygments  (already in requirements.txt)
"""

import argparse
import os
import re
import shutil
import sys

import markdown
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import PowerShellLexer

# ──────────────────────────────────────────────
# Paths
# ──────────────────────────────────────────────

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(SCRIPT_DIR)


def resolve_system_mgmt_repo(cli_arg: str | None) -> str:
    """Return the absolute path to the system-management_scripts repo."""
    if cli_arg:
        p = os.path.abspath(cli_arg)
    else:
        # Default: sibling directory two levels up from scripts/
        p = os.path.join(REPO_ROOT, "..", "system-management_scripts")
        p = os.path.abspath(p)
    if not os.path.isdir(p):
        sys.exit(f"ERROR: system-management_scripts repo not found at {p}")
    return p


# ──────────────────────────────────────────────
# HTML templates
# ──────────────────────────────────────────────

NAV_HTML = """\
<header>
    <div class="container">
        <nav>
            <div class="logo"><a href="/">Paul Namalomba</a></div>
            <ul class="nav-links">
                <li><a href="https://paulnamalomba.github.io/">Portfolio Home</a></li>
                <li><a href="/docs/guide-home/">Guides &amp; Scripts</a></li>
                <li><a href="/docs/guides/">Tech Guides</a></li>
                <li><a href="/docs/system-scripts/">System Scripts</a></li>
            </ul>
        </nav>
    </div>
</header>"""

FOOTER_HTML = """\
<footer>
    <div class="container">
        <p>&copy; 2025 Paul Namalomba. All rights reserved.</p>
    </div>
</footer>"""


def page_shell(title: str, body: str, extra_css: str = "") -> str:
    """Wrap *body* in the full HTML page chrome."""
    style_block = f"\n    <style>{extra_css}</style>" if extra_css else ""
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} - Paul Namalomba</title>
    <link rel="stylesheet" href="/styles.css">{style_block}
</head>
<body class="docs-page">
{NAV_HTML}

{body}

{FOOTER_HTML}
</body>
</html>"""


# ──────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────

def to_title(filename: str) -> str:
    base = filename.rsplit(".", 1)[0]
    return base.replace("_", " ").replace("-", " ").title()


def md_to_html(md_text: str) -> str:
    return markdown.markdown(
        md_text,
        extensions=["fenced_code", "codehilite", "tables", "toc"],
    )


# ──────────────────────────────────────────────
# Step 1 — Sync guides from system-management_scripts
# ──────────────────────────────────────────────

def sync_files(src_dir: str, dst_dir: str, ext: str) -> None:
    """Copy all files with *ext* from *src_dir* into *dst_dir*."""
    os.makedirs(dst_dir, exist_ok=True)
    count = 0
    for name in sorted(os.listdir(src_dir)):
        if name.endswith(ext):
            shutil.copy2(os.path.join(src_dir, name), os.path.join(dst_dir, name))
            count += 1
    print(f"  Synced {count} {ext} files  {src_dir}  ->  {dst_dir}")


# ──────────────────────────────────────────────
# Step 2 — Generate guide HTML pages
# ──────────────────────────────────────────────

def build_guides(guides_dir: str) -> None:
    """Convert every .md in *guides_dir* to .html and create index.html."""
    guides = []
    for md_file in sorted(os.listdir(guides_dir)):
        if not md_file.endswith(".md"):
            continue
        guides.append(md_file)

        md_path = os.path.join(guides_dir, md_file)
        html_file = md_file[:-3] + ".html"
        html_path = os.path.join(guides_dir, html_file)

        with open(md_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Rewrite intra-doc .md links to .html
        content = content.replace(".md)", ".html)")

        html_content = md_to_html(content)
        title = to_title(md_file)

        body = f"""\
<main class="container docs-container">
    <div class="card docs-card">
        <div class="docs-breadcrumb">
            <a href="index.html">← Back to Guides</a>
            <span>|</span>
            <a href="/">Portfolio Home</a>
        </div>
        <article class="docs-content">{html_content}</article>
    </div>
</main>"""

        with open(html_path, "w", encoding="utf-8") as f:
            f.write(page_shell(title, body))

    # ── Index page ──
    cards = ""
    for g in guides:
        html_name = g[:-3] + ".html"
        title = to_title(g)
        cards += f"""\
                    <div class="card">
                        <h3><a href="{html_name}">{title}</a></h3>
                    </div>\n"""

    body = f"""\
<main class="container docs-container">
    <h2>Technical Guides</h2>
    <div class="grid">
{cards}                </div>
</main>"""

    index_path = os.path.join(guides_dir, "index.html")
    with open(index_path, "w", encoding="utf-8") as f:
        f.write(page_shell("Technical Guides", body))

    print(f"  Built {len(guides)} guide pages + index  ->  {guides_dir}")


# ──────────────────────────────────────────────
# Step 3 — Generate docs/index.html
# ──────────────────────────────────────────────

def build_docs_index(docs_dir: str) -> None:
    """Convert docs/index.md → docs/index.html."""
    md_path = os.path.join(docs_dir, "index.md")
    if not os.path.exists(md_path):
        print("  Skipping docs/index.html — index.md not found")
        return

    with open(md_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Strip YAML front-matter
    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            content = parts[2].strip()

    content = content.replace(".md)", ".html)")
    html_content = md_to_html(content)

    body = f"""\
<main class="container docs-container">
    <div class="card docs-card">
        <div class="docs-breadcrumb">
            <a href="/">Portfolio Home</a>
            <span>|</span>
            <a href="/docs/guide-home/">Guides &amp; Scripts</a>
            <span>|</span>
            <a href="/docs/guides/">Tech Guides</a>
            <span>|</span>
            <a href="/docs/system-scripts/">System Scripts</a>
        </div>
        <article class="docs-content">{html_content}</article>
    </div>
</main>"""

    out = os.path.join(docs_dir, "index.html")
    with open(out, "w", encoding="utf-8") as f:
        f.write(page_shell("Technical Documentation", body))

    print(f"  Built docs/index.html")


# ──────────────────────────────────────────────
# Step 4 — Generate guide-home/index.html
# ──────────────────────────────────────────────

def build_guide_home(docs_dir: str, sys_mgmt_repo: str) -> None:
    """Build guide-home/index.html from system-management_scripts README."""
    readme_path = os.path.join(sys_mgmt_repo, "README.md")
    if not os.path.exists(readme_path):
        print("  Skipping guide-home — README.md not found in system-management_scripts")
        return

    with open(readme_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Fix email markdown
    content = content.replace(
        "](kabwenzenamalomba@gmail.com)",
        "](mailto:kabwenzenamalomba@gmail.com)",
    )
    # Rewrite guide links
    content = re.sub(
        r"\(guides/([^\)]+?)\.md\)", r"(/docs/guides/\1.html)", content
    )
    # Rewrite script links
    content = re.sub(
        r"\(windows/([^\)]+?)\.ps1\)", r"(/docs/system-scripts/\1.html)", content
    )

    html_content = md_to_html(content)

    body = f"""\
<main class="container docs-container">
    <div class="card docs-card">
        <div class="docs-breadcrumb">
            <a href="/">Portfolio Home</a>
            <span>|</span>
            <a href="/docs/guides/">Tech Guides</a>
            <span>|</span>
            <a href="/docs/system-scripts/">System Scripts</a>
        </div>
        <article class="docs-content">{html_content}</article>
    </div>
</main>"""

    out_dir = os.path.join(docs_dir, "guide-home")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "index.html")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(page_shell("Guide & Scripts", body))

    print(f"  Built guide-home/index.html")


# ──────────────────────────────────────────────
# Step 5 — Generate system-scripts pages
# ──────────────────────────────────────────────

def build_system_scripts(scripts_dir: str) -> None:
    """Build HTML pages for every .ps1 script and a card index."""
    lexer = PowerShellLexer()
    formatter = HtmlFormatter(linenos=True, cssclass="codehilite", style="default")
    highlight_css = formatter.get_style_defs(".codehilite")

    scripts = []
    for ps1_file in sorted(os.listdir(scripts_dir)):
        if not ps1_file.endswith(".ps1"):
            continue
        scripts.append(ps1_file)

        ps1_path = os.path.join(scripts_dir, ps1_file)
        with open(ps1_path, "r", encoding="utf-8") as f:
            source = f.read()

        # Extract first comment block as description
        desc_lines: list[str] = []
        for line in source.splitlines():
            stripped = line.strip()
            if stripped.startswith("#"):
                desc_lines.append(stripped.lstrip("# ").strip())
            elif stripped == "":
                if desc_lines:
                    break
            else:
                break

        highlighted = highlight(source, lexer, formatter)
        title = to_title(ps1_file)

        body = f"""\
<main class="container docs-container">
    <div class="card docs-card">
        <div class="docs-breadcrumb">
            <a href="index.html">← Back to System Scripts</a>
            <span>|</span>
            <a href="/docs/guide-home/">Guides &amp; Scripts</a>
            <span>|</span>
            <a href="/">Portfolio Home</a>
        </div>
        <article class="docs-content">
            <h1>{title}</h1>
            <p><code>{ps1_file}</code> · <a href="{ps1_file}" download>Download Script</a></p>
            {highlighted}
        </article>
    </div>
</main>"""

        html_path = os.path.join(scripts_dir, ps1_file[:-4] + ".html")
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(page_shell(title, body, extra_css=highlight_css))

    # ── Index page ──
    cards = ""
    for script in scripts:
        html_name = script[:-4] + ".html"
        title = to_title(script)
        ps1_path = os.path.join(scripts_dir, script)
        with open(ps1_path, "r", encoding="utf-8") as f:
            lines = f.read().splitlines()
        desc_parts: list[str] = []
        for line in lines:
            stripped = line.strip()
            if stripped.startswith("#"):
                desc_parts.append(stripped.lstrip("# ").strip())
            elif stripped == "":
                if desc_parts:
                    break
            else:
                break
        desc = desc_parts[0] if desc_parts else script

        cards += f"""\
                    <div class="card">
                        <h3><a href="{html_name}">{title}</a></h3>
                        <p>{desc}</p>
                        <p><code>{script}</code></p>
                    </div>\n"""

    body = f"""\
<main class="container docs-container">
    <h2>System Scripts</h2>
    <div class="grid">
{cards}                </div>
</main>"""

    index_path = os.path.join(scripts_dir, "index.html")
    with open(index_path, "w", encoding="utf-8") as f:
        f.write(page_shell("System Scripts", body))

    print(f"  Built {len(scripts)} script pages + index  ->  {scripts_dir}")


# ──────────────────────────────────────────────
# Main
# ──────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(description="Build docs HTML locally.")
    parser.add_argument(
        "--system-management-scripts",
        dest="sys_mgmt",
        default=None,
        help="Path to system-management_scripts repo (default: sibling dir)",
    )
    args = parser.parse_args()

    sys_mgmt_repo = resolve_system_mgmt_repo(args.sys_mgmt)
    docs_dir = os.path.join(REPO_ROOT, "docs")
    guides_dir = os.path.join(docs_dir, "guides")
    scripts_dir = os.path.join(docs_dir, "system-scripts")

    print("=" * 60)
    print("build-docs.py — Building docs HTML locally")
    print("=" * 60)

    print("\n[1/5] Syncing guides from system-management_scripts …")
    sync_files(os.path.join(sys_mgmt_repo, "guides"), guides_dir, ".md")

    print("\n[2/5] Syncing PowerShell scripts …")
    sync_files(os.path.join(sys_mgmt_repo, "windows"), scripts_dir, ".ps1")

    print("\n[3/5] Building guide HTML pages …")
    build_guides(guides_dir)

    print("\n[4/5] Building docs index + guide-home …")
    build_docs_index(docs_dir)
    build_guide_home(docs_dir, sys_mgmt_repo)

    print("\n[5/5] Building system-scripts HTML pages …")
    build_system_scripts(scripts_dir)

    print("\n" + "=" * 60)
    print("Done!  Now commit and push to deploy.")
    print("=" * 60)


if __name__ == "__main__":
    main()
