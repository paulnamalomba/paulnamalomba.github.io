"""Shared, deterministic accessibility markup for static page generators."""

import re

from bs4 import BeautifulSoup


TOGGLE_ICON = '<svg viewBox="0 0 24 24" width="18" height="18" aria-hidden="true"><path d="m6 9 6 6 6-6" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>'


def harden_html(content: str) -> str:
    """Preserve content while applying the shared static interface contract."""
    soup = BeautifulSoup(content, "html.parser")
    if not soup.body:
        return content

    main = soup.find("main")
    if main is None:
        main = soup.select_one(".page-wrapper, .login-container, .login-wrapper")
        if main is not None:
            main.name = "main"
        elif soup.select_one(".slide"):
            main = soup.new_tag("main", id="main")
            first_slide = soup.select_one(".slide")
            first_slide.insert_before(main)
            for slide in list(soup.select("body > .slide")):
                main.append(slide.extract())
    if main is not None:
        main["id"] = main.get("id", "main")
        main["tabindex"] = "-1"
        if not soup.select_one(".skip-link"):
            skip = soup.new_tag("a", href=f"#{main['id']}", **{"class": "skip-link"})
            skip.string = "Skip to content"
            soup.body.insert(0, skip)

    for index, button in enumerate(soup.select("[data-menu-button], .hamburger"), 1):
        header = button.find_parent("header")
        navigation = header.select_one("[data-nav], .nav-links") if header else None
        if navigation:
            navigation["id"] = navigation.get("id", f"site-navigation-{index}")
            button["type"] = "button"
            button["aria-controls"] = navigation["id"]
            button["aria-expanded"] = "false"
    for nav in soup.find_all("nav"):
        nav["aria-label"] = nav.get("aria-label", "Primary navigation")

    containers = soup.select(".nav-dropdown, .dropdown-menu, .dropdown-nested, .breadcrumb-dropdown")
    for index, container in enumerate(containers, 1):
        panel = container.find(class_=re.compile(r"^(dropdown-content|dropdown-nested-content|breadcrumb-dropdown-content)$"), recursive=False)
        trigger = container.find(["button", "a", "span"], recursive=False)
        if panel is None or trigger is None:
            continue
        existing_toggle = container.find("button", recursive=False)
        if existing_toggle:
            trigger = existing_toggle
        elif trigger.name == "a" and trigger.get("href") != "#":
            toggle = soup.new_tag("button", type="button", **{
                "class": "submenu-toggle",
                "aria-label": f"Toggle {trigger.get_text(strip=True)} links",
            })
            toggle.append(BeautifulSoup(TOGGLE_ICON, "html.parser").svg)
            panel.insert_before(toggle)
            trigger = toggle
        else:
            trigger.name = "button"
            trigger.attrs.pop("href", None)
        classes = trigger.get("class", [])
        if "dropdown-button" not in classes:
            trigger["class"] = [*classes, "dropdown-button"]
        panel["id"] = panel.get("id", f"dropdown-panel-{index}")
        trigger["type"] = "button"
        trigger["aria-controls"] = panel["id"]
        trigger["aria-expanded"] = "false"

    for index, button in enumerate(soup.select(".expand-btn, .qa-question"), 1):
        container = button.find_parent(class_=re.compile(r"\b(hub-card|qa-item)\b")) or button.parent
        sibling = button.find_next_sibling()
        panel = sibling if sibling and "qa-answer" in sibling.get("class", []) else container.select_one(".expand-wrapper, .qa-answer")
        if panel:
            panel["id"] = panel.get("id", f"disclosure-panel-{index}")
            button["type"] = "button"
            button["aria-controls"] = panel["id"]
            button["aria-expanded"] = "false"
            button.attrs.pop("onclick", None)

    for button in soup.select("[data-guide-filter]"):
        button["type"] = "button"
        button["aria-pressed"] = str(button["data-guide-filter"] == "all").lower()
    filters = soup.select_one(".filter-list")
    if filters:
        filters["role"] = "group"
        filters["aria-label"] = "Guide category"
    results = soup.select_one(".guide-grid:has([data-guide-card])")
    search = soup.select_one("[data-guide-search]")
    if results and search:
        results["id"] = "guide-results"
        search["aria-controls"] = results["id"]
    count = soup.select_one("[data-result-count]")
    if count:
        count["role"] = "status"
        count["aria-live"] = "polite"
        count["aria-atomic"] = "true"
    empty = soup.select_one("[data-empty-state]")
    if empty:
        empty["hidden"] = ""

    previous_level = 0
    for heading in soup.find_all(re.compile(r"^h[1-6]$")):
        level = int(heading.name[1])
        if previous_level and level > previous_level + 1:
            level = previous_level + 1
            heading.name = f"h{level}"
        previous_level = level

    ids = {tag["id"] for tag in soup.select("[id]")}
    for link in soup.select('a[href^="#"]'):
        fragment = link["href"][1:]
        candidate = re.sub(r"-+", "-", fragment)
        if fragment not in ids and candidate in ids:
            link["href"] = f"#{candidate}"
        elif fragment == "seska" and fragment not in ids:
            (link.parent if link.parent.name == "li" else link).decompose()

    for link in soup.select('a[href="LICENSE"]'):
        link["href"] = "https://github.com/paulnamalomba/system-management_scripts#license"

    if not soup.select_one('script[src="/scripts/interface.js"]'):
        script = soup.new_tag("script", src="/scripts/interface.js", defer="")
        soup.head.append(script)

    for script in soup.find_all("script"):
        source = script.get("src", "")
        if "highlight.js" in source or "mermaid" in source:
            script["defer"] = ""
        if script.string:
            code = str(script.string)
            if "if (window.hljs)" not in code:
                code = code.replace("hljs.highlightAll();", "if (window.hljs) window.hljs.highlightAll();")
            if "if (window.mermaid)" not in code:
                code = code.replace("mermaid.initialize(", "if (window.mermaid) window.mermaid.initialize(")
            code = re.sub(
                r"behavior:\s*[\"']smooth[\"']",
                'behavior: window.matchMedia("(prefers-reduced-motion: reduce)").matches ? "auto" : "smooth"',
                code,
            )
            if code != str(script.string):
                script.string.replace_with(code)

    return str(soup)
