#!/usr/bin/env python3
"""
build-docs.py — Local build script for paulnamalomba.github.io docs pages.

Replaces the deploy-docs.yml GitHub Action workflow.  Run from the repo root:

    python scripts/build-docs.py

Requires: pip install markdown pygments  (already in requirements.txt)
"""

import argparse
import html
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
    <a class="skip-link" href="#main">Skip to content</a>
    <header>
        <div class="container">
            <nav>
                <div class="logo"><a href="/">Paul Namalomba</a></div>
                <button class="hamburger" aria-label="Toggle navigation" aria-expanded="false">
                    <span></span>
                    <span></span>
                </button>
                <ul class="nav-links">
                    <li><a href="/">Portfolio</a></li>
                    <li><a href="/docs/">Knowledge Base</a></li>
                    <li><a href="/docs/guides/">All Guides</a></li>
                    <li><a href="/docs/system-scripts/">System Scripts</a></li>
                </ul>
            </nav>
        </div>
    </header>
"""

FOOTER_HTML = """\
    <footer>
        <div class="container footer-inner">
            <span>&copy; 2026 Paul Namalomba · Field notes from systems work.</span>
            <a href="/">Back to portfolio &rarr;</a>
        </div>
    </footer>
    <script>
        const hamburger = document.querySelector('.hamburger');
        const navLinks = document.querySelector('.nav-links');
        hamburger.addEventListener('click', () => {
            const expanded = hamburger.getAttribute('aria-expanded') === 'true';
            hamburger.setAttribute('aria-expanded', !expanded);
            hamburger.classList.toggle('active');
            navLinks.classList.toggle('open');
            document.body.classList.toggle('menu-open', !expanded);
        });
        // Close menu when a nav link is clicked
        navLinks.querySelectorAll('a').forEach(link => {
            link.addEventListener('click', () => {
                hamburger.classList.remove('active');
                navLinks.classList.remove('open');
                hamburger.setAttribute('aria-expanded', 'false');
                document.body.classList.remove('menu-open');
            });
        });
    </script>
"""


def page_shell(title: str, body: str, extra_css: str = "") -> str:
    """Wrap *body* in the full HTML page chrome."""
    style_block = f"\n    <style>{extra_css}</style>" if extra_css else ""
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="Practical technical guides by Paul Namalomba on backend engineering, data systems, infrastructure and scientific computing.">
    <meta name="theme-color" content="#f2f0e9">
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


def guide_metadata(filename: str, content: str) -> dict[str, str]:
    """Extract human-friendly metadata for a guide library card."""
    heading = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
    title = heading.group(1).strip() if heading else to_title(filename)
    title = re.sub(r"\s+[—-]\s+Power User Guide.*$", "", title, flags=re.IGNORECASE)
    updated = re.search(r"\*\*Last updated\*\*:\s*([^<\n]+)", content, re.IGNORECASE)
    updated_text = updated.group(1).strip() if updated else "Reference guide"

    name = filename.upper()
    if any(term in name for term in ("POSTGRES", "REDIS", "KAFKA", "ML_", "PYTHON_ML", "BATCH_THREAD", "MEMORY_MANAGEMENT")):
        category = "data"
        label = "Data & performance"
    elif any(term in name for term in ("DJANGO", "DOTNET", "AUTH_", "API", "REALTIME", "C_SHARP", "JAVA", "LANGUAGE_RUNTIME", "CLEAN_ARCH")):
        category = "backend"
        label = "Backend & architecture"
    elif any(term in name for term in ("DOCKER", "SSH", "SSL", "SYSTEMCTL", "UBUNTU", "WINDOWS", "GIT_GH", "VI_", "LINUX", "WEB_SERVER", "RESPONSIVE")):
        category = "infrastructure"
        label = "Infrastructure & tooling"
    else:
        category = "systems"
        label = "Systems engineering"

    # Prefer the first substantive paragraph after Overview/Context, without badges or metadata.
    summary = "Implementation notes, trade-offs and production-minded patterns from hands-on systems work."
    section = re.search(r"^##\s+(?:Overview|Context)\s*$([\s\S]+?)(?=^##\s|\Z)", content, re.MULTILINE | re.IGNORECASE)
    if section:
        for paragraph in re.split(r"\n\s*\n", section.group(1)):
            clean = re.sub(r"!?\[([^\]]*)\]\([^)]*\)", r"\1", paragraph)
            clean = re.sub(r"[*_`#<>]", "", clean)
            clean = " ".join(clean.split())
            if len(clean) > 70:
                summary = clean[:177].rstrip(" ,.;:") + ("…" if len(clean) > 177 else "")
                break

    return {
        "filename": filename,
        "title": title,
        "updated": updated_text,
        "category": category,
        "label": label,
        "summary": summary,
    }


def md_to_html(md_text: str) -> str:
    rendered = markdown.markdown(
        md_text,
        extensions=["fenced_code", "codehilite", "tables", "toc"],
    )

    # A few source guides contain additional level-one headings inside the
    # document body. Keep the first as the page title and demote later H1s so
    # every generated guide has one clear primary heading.
    first_h1 = True

    def normalize_h1(match: re.Match[str]) -> str:
        nonlocal first_h1
        if first_h1:
            first_h1 = False
            return match.group(0)
        return re.sub(r"h1", "h2", match.group(0), count=2, flags=re.IGNORECASE)

    return re.sub(r"<h1\b[^>]*>.*?</h1>", normalize_h1, rendered, flags=re.IGNORECASE | re.DOTALL)


def repair_internal_fragments(html_text: str) -> str:
    """Align hand-authored Markdown TOC fragments with generated heading IDs."""
    ids = set(re.findall(r'\sid="([^"]+)"', html_text))

    def replace(match: re.Match[str]) -> str:
        fragment = match.group(1)
        if fragment in ids:
            return match.group(0)
        candidate = re.sub(r"-+", "-", fragment)
        if candidate in ids:
            return f'href="#{candidate}"'
        numbered = re.sub(r"-(\d+)$", r"_\1", candidate)
        if numbered in ids:
            return f'href="#{numbered}"'
        return match.group(0)

    return re.sub(r'href="#([^"]+)"', replace, html_text)


def write_generated_html(path: str, content: str) -> None:
    """Write deterministic repository-native HTML without trailing whitespace."""
    normalized = "\r\n".join(line.rstrip().replace("\t", "    ") for line in content.splitlines()) + "\r\n"
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write(normalized)


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
    guides: list[dict[str, str]] = []
    for md_file in sorted(os.listdir(guides_dir)):
        if not md_file.endswith(".md"):
            continue
        md_path = os.path.join(guides_dir, md_file)
        html_file = md_file[:-3] + ".html"
        html_path = os.path.join(guides_dir, html_file)

        with open(md_path, "r", encoding="utf-8") as f:
            content = f.read()
        metadata = guide_metadata(md_file, content)
        guides.append(metadata)

        # Rewrite intra-doc links and malformed bare-email Markdown links.
        content = content.replace(".md)", ".html)")
        content = re.sub(r"\]\((?![a-z]+:)([^)\s]+@[^)\s]+)\)", r"](mailto:\1)", content, flags=re.IGNORECASE)

        html_content = repair_internal_fragments(md_to_html(content))
        title = metadata["title"]

        body = f"""\
    <main id="main" class="container docs-container">
        <div class="card docs-card">
            <div class="docs-breadcrumb">
                <a href="index.html">← Back to Guides</a>
                <span>|</span>
                <a href="/">Portfolio Home</a>
            </div>
            <article class="docs-content">{html_content}</article>
        </div>
    </main>
"""

        write_generated_html(html_path, page_shell(title, body))

    # ── Index page ──
    cards = ""
    for guide in guides:
        html_name = guide["filename"][:-3] + ".html"
        title = html.escape(guide["title"])
        cards += f"""\
            <article class="guide-card" data-guide-card data-category="{guide['category']}">
                <span class="guide-category">{guide['label']} · {html.escape(guide['updated'])}</span>
                <h3>{title}</h3>
                <p>{html.escape(guide['summary'])}</p>
                <a href="{html_name}"><span>Read guide</span><span aria-hidden="true">&rarr;</span></a>
            </article>\n
"""

    featured_names = [
        "BATCH_THREADING_AND_MPI_FOR_LARGE_DB_OPS.md",
        "CLEAN_ARCHITECTURE_PROJECT_STRUCTURES.md",
        "WEB_APIS_AND_SERVING.md",
    ]
    featured = [next((g for g in guides if g["filename"] == name), None) for name in featured_names]
    featured = [g for g in featured if g]
    featured_cards = "".join(
        f"""<a class="featured-guide" href="{g['filename'][:-3]}.html">
            <small>{g['label']}</small>
            <h3>{html.escape(g['title'])}</h3>
            <p>{html.escape(g['summary'])}</p>
            <b>Read field note &rarr;</b>
        </a>"""
        for g in featured
    )

    body = f"""\
    <main id="main">
        <section class="docs-hero">
            <div class="container docs-hero-grid">
                <div><p class="eyebrow">Paul Namalomba · Technical field notes</p><h1>Notes for systems that need to <em>work.</em></h1></div>
                <div class="docs-hero-copy">
                    <p>Production-minded guides on backend architecture, data infrastructure, scientific computing and the tools around them.</p>
                    <div class="docs-stats"><div><strong>{len(guides)}</strong><span>In-depth guides</span></div><div><strong>4</strong><span>Engineering domains</span></div></div>
                </div>
            </div>
        </section>
        <section class="docs-toolbar" aria-label="Guide filters">
            <div class="container toolbar-grid">
                <label class="search-wrap"><span class="sr-only">Search guides</span><input type="search" placeholder="Search topics, tools or languages…" data-guide-search></label>
                <div class="filter-list">
                    <button class="filter-button active" data-guide-filter="all">All</button>
                    <button class="filter-button" data-guide-filter="backend">Backend</button>
                    <button class="filter-button" data-guide-filter="data">Data</button>
                    <button class="filter-button" data-guide-filter="infrastructure">Infrastructure</button>
                    <button class="filter-button" data-guide-filter="systems">Systems</button>
                </div>
            </div>
        </section>
        <section class="docs-library">
            <div class="container">
                <div class="library-heading"><div><p class="eyebrow">Start here</p><h2>Featured field notes</h2></div><p>Built from applied work, not abstract checklists.</p></div>
                <div class="featured-guides">{featured_cards}</div>
                <div class="library-heading"><div><p class="eyebrow">Full library</p><h2>Explore every guide</h2></div><p data-result-count>{len(guides)} guides</p></div>
                <div class="guide-grid">{cards}</div>
                <div class="empty-state" data-empty-state>No guides match that search. Try a broader term or another category.</div>
            </div>
        </section>
        <script src="/scripts/guides.js" defer></script>
    </main>
"""

    index_path = os.path.join(guides_dir, "index.html")
    write_generated_html(index_path, page_shell("Technical Guides", body))

    print(f"  Built {len(guides)} guide pages + index  ->  {guides_dir}")


# ──────────────────────────────────────────────
# Step 3 — Generate docs/index.html
# ──────────────────────────────────────────────

def build_docs_index(docs_dir: str) -> None:
    """Build the editorial knowledge-base landing page."""
    body = """\
    <main id="main">
        <section class="docs-hero">
            <div class="container docs-hero-grid">
                <div><p class="eyebrow">Knowledge base · Paul Namalomba</p><h1>Field notes from building <em>real systems.</em></h1></div>
                <div class="docs-hero-copy">
                    <p>Implementation guides, architecture comparisons and reusable scripts shaped by backend, data and computational engineering work.</p>
                    <div class="docs-stats"><div><strong>40</strong><span>Technical guides</span></div><div><strong>11</strong><span>Script collections</span></div></div>
                </div>
            </div>
        </section>
        <section class="knowledge-paths">
            <div class="container path-grid">
                <a class="path-card" href="/docs/guides/"><small>Read & understand</small><h2>Technical guides</h2><p>Deep, practical notes on architecture, databases, infrastructure, performance and scientific software.</p><b>Browse all 40 guides &rarr;</b></a>
                <a class="path-card" href="/docs/system-scripts/"><small>Use & adapt</small><h2>System scripts</h2><p>Production-minded PowerShell utilities for navigation, files, environments, scheduling and maintenance.</p><b>Explore 11 collections &rarr;</b></a>
            </div>
        </section>
        <section class="docs-library">
            <div class="container">
                <div class="library-heading"><div><p class="eyebrow">Recommended reading</p><h2>Start with applied problems</h2></div><p>Three guides that reflect the work behind this portfolio.</p></div>
                <div class="featured-guides">
                    <a class="featured-guide" href="/docs/guides/BATCH_THREADING_AND_MPI_FOR_LARGE_DB_OPS.html"><small>Data & performance</small><h3>Memory-aware database operations at scale</h3><p>Batching, threading and MPI chunking for large updates.</p><b>Read field note &rarr;</b></a>
                    <a class="featured-guide" href="/docs/guides/CLEAN_ARCHITECTURE_PROJECT_STRUCTURES.html"><small>Architecture</small><h3>Clean structures across three ecosystems</h3><p>C#, Flutter and TypeScript patterns compared.</p><b>Read field note &rarr;</b></a>
                    <a class="featured-guide" href="/docs/guides/WEB_APIS_AND_SERVING.html"><small>Backend systems</small><h3>Choosing a web API framework</h3><p>Operational trade-offs across popular stacks.</p><b>Read field note &rarr;</b></a>
                </div>
            </div>
        </section>
    </main>
"""

    out = os.path.join(docs_dir, "index.html")
    write_generated_html(out, page_shell("Technical Knowledge Base", body))

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
    <main id="main" class="container docs-container">
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
    </main>
"""

    out_dir = os.path.join(docs_dir, "guide-home")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "index.html")
    write_generated_html(out_path, page_shell("Guide & Scripts", body))

    print(f"  Built guide-home/index.html")


# ──────────────────────────────────────────────
# Step 5 — Generate system-scripts pages
# ──────────────────────────────────────────────

def powershell_description(source: str, fallback: str) -> str:
    """Extract a concise description from line comments or PowerShell help blocks."""
    text = source.lstrip("\ufeff").lstrip()
    if text.startswith("<#"):
        block_end = text.find("#>")
        block = text[2:block_end if block_end >= 0 else None]
        synopsis = re.search(
            r"\.SYNOPSIS\s*(.*?)(?=\n\s*\.[A-Z]+|\Z)",
            block,
            re.IGNORECASE | re.DOTALL,
        )
        if synopsis:
            value = " ".join(synopsis.group(1).split())
            if value:
                return value

    lines: list[str] = []
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("#"):
            value = stripped.lstrip("# ").strip()
            if value:
                lines.append(value)
        elif stripped == "" and not lines:
            continue
        else:
            break
    return " ".join(lines[:2]) if lines else fallback


def build_system_scripts(scripts_dir: str) -> None:
    """Build HTML pages for every .ps1 script and a card index."""
    lexer = PowerShellLexer()
    formatter = HtmlFormatter(linenos=True, cssclass="codehilite", style="default")
    highlight_css = formatter.get_style_defs(".codehilite")

    scripts = []
    script_descriptions: dict[str, str] = {}
    for ps1_file in sorted(os.listdir(scripts_dir)):
        if not ps1_file.endswith(".ps1"):
            continue
        scripts.append(ps1_file)

        ps1_path = os.path.join(scripts_dir, ps1_file)
        with open(ps1_path, "r", encoding="utf-8-sig") as f:
            source = f.read()
        script_descriptions[ps1_file] = powershell_description(source, ps1_file)

        highlighted = highlight(source, lexer, formatter)
        title = to_title(ps1_file)

        body = f"""\
    <main id="main" class="container docs-container">
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
    </main>
"""

        html_path = os.path.join(scripts_dir, ps1_file[:-4] + ".html")
        write_generated_html(html_path, page_shell(title, body, extra_css=highlight_css))

    # ── Index page ──
    cards = ""
    for script in scripts:
        html_name = script[:-4] + ".html"
        title = to_title(script)
        desc = script_descriptions[script]

        cards += f"""\
    <div class="card">
        <h3><a href="{html_name}">{html.escape(title)}</a></h3>
        <p>{html.escape(desc)}</p>
        <p><code>{html.escape(script)}</code></p>
    </div>\n
"""

    body = f"""\
    <main id="main" class="container docs-container">
        <h1>System Scripts</h1>
        <div class="grid">
    {cards}                </div>
    </main>
"""

    index_path = os.path.join(scripts_dir, "index.html")
    write_generated_html(index_path, page_shell("System Scripts", body))

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
    parser.add_argument(
        "--no-sync",
        action="store_true",
        help="Rebuild the checked-in documentation without syncing a source repository.",
    )
    args = parser.parse_args()

    sys_mgmt_repo = None if args.no_sync else resolve_system_mgmt_repo(args.sys_mgmt)
    docs_dir = os.path.join(REPO_ROOT, "docs")
    guides_dir = os.path.join(docs_dir, "guides")
    scripts_dir = os.path.join(docs_dir, "system-scripts")

    print("=" * 60)
    print("build-docs.py — Building docs HTML locally")
    print("=" * 60)

    if sys_mgmt_repo:
        print("\n[1/5] Syncing guides from system-management_scripts …")
        sync_files(os.path.join(sys_mgmt_repo, "guides"), guides_dir, ".md")

        print("\n[2/5] Syncing PowerShell scripts …")
        sync_files(os.path.join(sys_mgmt_repo, "windows"), scripts_dir, ".ps1")
    else:
        print("\n[1/5] Skipping guide sync (--no-sync)")
        print("\n[2/5] Skipping script sync (--no-sync)")

    print("\n[3/5] Building guide HTML pages …")
    build_guides(guides_dir)

    print("\n[4/5] Building docs index + guide-home …")
    build_docs_index(docs_dir)
    if sys_mgmt_repo:
        build_guide_home(docs_dir, sys_mgmt_repo)

    print("\n[5/5] Building system-scripts HTML pages …")
    build_system_scripts(scripts_dir)

    print("\n" + "=" * 60)
    print("Done!  Now commit and push to deploy.")
    print("=" * 60)


if __name__ == "__main__":
    main()
