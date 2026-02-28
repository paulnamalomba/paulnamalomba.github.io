#!/usr/bin/env python3
"""
build-learning.py — Auto-converter for IBM Data Engineering Markdown Lectures.
This script traverses `learning/**/raw-markdown/` and generates highly styled HTML pages.
It replicates the complex and beautiful HTML structure (cards, mermaid diagrams, syntax highlighting).

Requires: pip install markdown beautifulsoup4
"""

import os
import re
import glob
from bs4 import BeautifulSoup, Tag
import markdown

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(SCRIPT_DIR)
LEARNING_DIR = os.path.join(REPO_ROOT, "learning", "ibm-data-engineering")

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{page_title}</title>
  
  <!-- CSS -->
  <link rel="stylesheet" href="{css_relative_path}">
  
  <!-- Highlight.js for Syntax Highlighting -->
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.8.0/styles/atom-one-dark.min.css">
  <script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.8.0/highlight.min.js"></script>
  <script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.8.0/languages/csharp.min.js"></script>
  
  <!-- Mermaid.js for Diagrams -->
  <script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>
  
  <script>
    document.addEventListener("DOMContentLoaded", function() {{
      hljs.highlightAll();
      mermaid.initialize({{
        startOnLoad: true,
        theme: 'dark',
        themeVariables: {{
          primaryColor: '#131a2e',
          primaryTextColor: '#e8edf5',
          primaryBorderColor: '#2a4080',
          lineColor: '#f0b429',
          secondaryColor: '#0d1321',
          tertiaryColor: '#1a2340',
          fontSize: '16px',
          fontFamily: "'Inter', -apple-system, system-ui, sans-serif"
        }}
      }});
    }});
  </script>
</head>
<body>
  <div class="page-wrapper" id="content">
    <div class="header-bar">
      <span class="brand">IBM Data Engineering</span>
      <nav>
{nav_html}
      </nav>
    </div>

    <div class="breadcrumb">
      <a href="{root_relative_path}index.html">Hub</a> <span>&rsaquo;</span> 
      <a href="{course_relative_path}index.html">Course {course_num}</a> <span>&rsaquo;</span> 
      <a href="index.html">Module {module_num}</a> <span>&rsaquo;</span> 
      Lecture {lecture_num}
    </div>

    <h1 class="fade-in">{lecture_title}</h1>
    <p class="fade-in fade-in-d1" style="font-size:1.05rem;">
      Module {module_num}, Lecture {lecture_num}
    </p>

{body_html}

    <div class="page-footer fade-in fade-in-d5">
      <p>Prepared by Paul Namalomba &middot; IBM Data Engineering</p>
    </div>
  </div>
</body>
</html>
"""

def extract_metadata(filename, md_text):
    """Extract metadata like Course, Module, Lecture numbers and Title."""
    metadata = {
        'course_num': 'X',
        'module_num': 'X',
        'lecture_num': 'X',
        'lecture_title': 'Untitled Lecture'
    }
    
    match_filename = re.search(r'module-(\d+)[\/\\]module-(\d+)-lecture-(\d+)', filename.replace('\\', '/'))
    if match_filename:
        metadata['course_num'] = match_filename.group(1)
        metadata['module_num'] = match_filename.group(2)
        metadata['lecture_num'] = match_filename.group(3)
        
    h1_match = re.search(r'^#\s+(.+)$', md_text, flags=re.MULTILINE)
    if h1_match:
        title_full = h1_match.group(1).strip()
        title_split = title_full.split(': ', 1)
        if len(title_split) > 1:
            metadata['lecture_title'] = title_split[1]
        else:
            metadata['lecture_title'] = title_full
            
    return metadata

def build_tree(md_files):
    tree = {}
    for md_path in md_files:
        with open(md_path, 'r', encoding='utf-8') as f:
            meta = extract_metadata(md_path, f.read())
        c = meta['course_num']
        m = meta['module_num']
        l = meta['lecture_num']
        t = meta['lecture_title']
        
        if c not in tree: tree[c] = {}
        if m not in tree[c]: tree[c][m] = []
        tree[c][m].append({'num': l, 'title': t, 'filename': f"lecture-{l}.html"})
        
    for c in tree:
        for m in tree[c]:
            tree[c][m].sort(key=lambda x: int(x['num']) if x['num'].isdigit() else x['num'])
    return tree

def get_title_from_html(filepath, default_title):
    if not os.path.exists(filepath):
        return default_title
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
        match = re.search(r'<title>(.*?)</title>', content, re.IGNORECASE)
        if match:
            # e.g "Course 8: ETL and Data Pipelines"
            # Some titles might be "Module 4: Event Streaming with Kafka"
            # Strip out generic parts if needed, but the full title is usually preferred
            title = match.group(1).strip()
            # If it's something generic like 'IBM Data Engineering Hub', use default
            if 'Hub' in title and 'Course' not in title:
                return default_title
            return title
    return default_title

def generate_nav_html(tree, depth, current_c=None, current_m=None, current_l=None):
    if depth == 0: root_rel = "./"
    elif depth == 1: root_rel = "../"
    else: root_rel = "../../"
    
    course_titles = {}
    for c in tree.keys():
        path = os.path.join(LEARNING_DIR, f"course-{c}", "index.html")
        course_titles[c] = get_title_from_html(path, f"Course {c}")
        
    module_titles = {}
    if current_c and current_c in tree:
        for m in tree[current_c].keys():
            path = os.path.join(LEARNING_DIR, f"course-{current_c}", f"module-{m}", "index.html")
            module_titles[m] = get_title_from_html(path, f"Module {m}")

    hub_active = ' class="active"' if depth == 0 else ''
    html = f'        <a href="{root_rel}index.html"{hub_active}>Hub</a>\n'

    if current_c or depth >= 0:
        label = course_titles.get(current_c, f"Course {current_c}") if current_c else "Courses"
        active_cls = ' class="active"' if depth == 1 else ''
        html += f'''        
        <div class="nav-dropdown">
          <a href="#" {active_cls}>{label} ▾</a>
          <div class="dropdown-content">\n'''
        for c in sorted(tree.keys(), key=lambda x: int(x) if x.isdigit() else x):
            c_title = course_titles.get(c, f"Course {c}")
            act = ' class="active"' if c == current_c else ''
            html += f'            <a href="{root_rel}course-{c}/index.html"{act}>{c_title}</a>\n'
        html += '''          </div>
        </div>\n'''

    if current_c and (current_m or depth >= 1):
        label = module_titles.get(current_m, f"Module {current_m}") if current_m else "Modules"
        active_cls = ' class="active"' if depth == 2 and not current_l else ''
        html += f'''        
        <div class="nav-dropdown">
          <a href="#" {active_cls}>{label} ▾</a>
          <div class="dropdown-content">\n'''
        for m in sorted(tree[current_c].keys(), key=lambda x: int(x) if x.isdigit() else x):
            m_title = module_titles.get(m, f"Module {m}")
            act = ' class="active"' if m == current_m else ''
            html += f'            <a href="{root_rel}course-{current_c}/module-{m}/index.html"{act}>{m_title}</a>\n'
        html += '''          </div>
        </div>\n'''

    if current_m and (current_l or depth >= 2):
        label = f"Lecture {current_l}" if current_l else "Lectures"
        active_cls = ' class="active"' if current_l else ''
        html += f'''        
        <div class="nav-dropdown">
          <a href="#" {active_cls}>{label} ▾</a>
          <div class="dropdown-content">\n'''
        for lec in tree[current_c][current_m]:
            act = ' class="active"' if lec['num'] == current_l else ''
            # Make sure we use lecture names in dropdown 
            html += f'            <a href="{root_rel}course-{current_c}/module-{current_m}/{lec["filename"]}"{act}>Lecture {lec["num"]}: {lec["title"]}</a>\n'
        html += '''          </div>
        </div>'''

    return html

def update_index_nav_regex(filepath, nav_html):
    if not os.path.exists(filepath): return
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    # Replace the <nav> block
    new_content = re.sub(r'<nav>.*?</nav>', f'<nav>\n{nav_html}\n      </nav>', content, flags=re.DOTALL)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_content)
        
def update_all_index_navs(tree):
    # Hub (depth 0)
    hub_path = os.path.join(LEARNING_DIR, "index.html")
    nav_html = generate_nav_html(tree, depth=0)
    update_index_nav_regex(hub_path, nav_html)
    
    # Courses (depth 1)
    for c in tree.keys():
        c_path = os.path.join(LEARNING_DIR, f"course-{c}", "index.html")
        nav_html = generate_nav_html(tree, depth=1, current_c=c)
        update_index_nav_regex(c_path, nav_html)
        
        # Modules (depth 2)
        for m in tree[c].keys():
            m_path = os.path.join(LEARNING_DIR, f"course-{c}", f"module-{m}", "index.html")
            nav_html = generate_nav_html(tree, depth=2, current_c=c, current_m=m)
            update_index_nav_regex(m_path, nav_html)


def transform_html_with_bs4(raw_html):
    soup = BeautifulSoup(raw_html, 'html.parser')
    
    for h1 in soup.find_all('h1'):
        h1.decompose()
        
    for code in soup.find_all('code', class_='language-mermaid'):
        pre = code.parent
        if pre and pre.name == 'pre':
            mermaid_text = code.get_text()
            container = soup.new_tag('div')
            container['class'] = 'mermaid-container'
            mermaid_pre = soup.new_tag('pre', **{'class': 'mermaid'})
            mermaid_pre.string = mermaid_text
            container.append(mermaid_pre)
            pre.replace_with(container)

    for bq in soup.find_all('blockquote'):
        div_callout = soup.new_tag('div', **{'class': 'callout tip'})
        first_p = bq.find('p')
        if first_p:
            text = first_p.get_text()
            if text.startswith('💡 '):
                title_text = text.split('\n')[0]
                first_p.string = text.replace(title_text + '\n', '', 1).replace(title_text, '', 1)
                title_div = soup.new_tag('div', **{'class': 'callout-title'})
                title_div.string = title_text
                div_callout.append(title_div)
            else:
                title_div = soup.new_tag('div', **{'class': 'callout-title'})
                title_div.string = "💡 Note"
                div_callout.append(title_div)
                
        for child in bq.contents:
            if isinstance(child, Tag):
                div_callout.append(child.extract())
            else:
                div_callout.append(child)
        bq.replace_with(div_callout)

    body_elements = list(soup.contents)
    new_soup = BeautifulSoup('', 'html.parser')
    
    current_card = None
    delay_index = 2

    for el in body_elements:
        if isinstance(el, Tag) and el.name == 'h2':
            current_card = soup.new_tag('div')
            current_card['class'] = f'section-card fade-in fade-in-d{delay_index}'
            delay_index = min(delay_index + 1, 5)
            new_soup.append(current_card)
            current_card.append(el.extract())
        elif current_card is not None:
            if isinstance(el, Tag):
                current_card.append(el.extract())
            else:
                current_card.append(el)
        else:
            if isinstance(el, Tag) and el.name == 'p':
                el['class'] = f"fade-in fade-in-d{delay_index}"
            if isinstance(el, Tag):
                new_soup.append(el.extract())
            else:
                new_soup.append(el)
                
    return str(new_soup)

def update_module_index(metadata, lecture_html_path):
    course_dir = os.path.join(LEARNING_DIR, f"course-{metadata['course_num']}")
    module_dir = os.path.join(course_dir, f"module-{metadata['module_num']}")
    index_path = os.path.join(module_dir, "index.html")
    
    if not os.path.exists(index_path):
        return
        
    with open(index_path, 'r', encoding='utf-8') as f:
        html_content = f.read()
        
    soup = BeautifulSoup(html_content, 'html.parser')
    grid = soup.find('div', class_='hub-grid')
    if not grid: return
        
    filename = os.path.basename(lecture_html_path)
    existing_card = soup.find('a', href=filename)
    desc = metadata.get('description', 'Auto-generated lecture content.')
    existing_links = len(grid.find_all('a', class_='hub-card'))
    delay_index = min(3 + existing_links, 5)
    
    card_html = f'''
      <a href="{filename}" class="hub-card fade-in fade-in-d{delay_index}">
        <div class="card-level">Lecture {metadata['lecture_num']}</div>
        <div class="card-title">{metadata['lecture_title']}</div>
        <div class="card-desc">{desc}</div>
      </a>
'''
    new_card_soup = BeautifulSoup(card_html, 'html.parser')
    
    if existing_card:
        existing_card.replace_with(new_card_soup.a)
    else:
        placeholder = None
        for card in grid.find_all('div', class_='hub-card'):
            level = card.find('div', class_='card-level')
            if level and 'Upcoming' in level.get_text():
                placeholder = card
                break
        if placeholder:
            placeholder.insert_before(new_card_soup.a)
        else:
            grid.append(new_card_soup.a)
            
    with open(index_path, 'w', encoding='utf-8') as f:
        f.write(soup.prettify(formatter="html"))

def process_markdown_file(md_path, tree):
    print(f"Processing: {md_path}")
    with open(md_path, 'r', encoding='utf-8') as f:
        md_text = f.read()

    metadata = extract_metadata(md_path, md_text)
    cur_c = metadata['course_num']
    cur_m = metadata['module_num']
    cur_l = metadata['lecture_num']
    
    desc_match = re.search(r'^[^#\n].+', md_text, flags=re.MULTILINE)
    if desc_match:
        desc = desc_match.group(0).strip()
        if len(desc) > 120: desc = desc[:117] + "..."
        metadata['description'] = desc
    
    raw_html = markdown.markdown(md_text, extensions=['fenced_code', 'tables'])
    processed_html = transform_html_with_bs4(raw_html)
    
    css_relative_path = "../../style.css"
    root_relative_path = "../../"
    course_relative_path = "../"
    
    # Generate Dropdowns
    nav_html = generate_nav_html(tree, depth=2, current_c=cur_c, current_m=cur_m, current_l=cur_l)
    
    final_output = HTML_TEMPLATE.format(
        page_title=f"Lecture {cur_l}: {metadata['lecture_title']}",
        css_relative_path=css_relative_path,
        root_relative_path=root_relative_path,
        course_relative_path=course_relative_path,
        course_num=cur_c,
        module_num=cur_m,
        lecture_num=cur_l,
        lecture_title=metadata['lecture_title'],
        nav_html=nav_html,
        body_html=processed_html
    )
    
    course_dir = os.path.join(LEARNING_DIR, f"course-{cur_c}")
    module_dir = os.path.join(course_dir, f"module-{cur_m}")
    os.makedirs(module_dir, exist_ok=True)
    out_file = os.path.join(module_dir, f"lecture-{cur_l}.html")
    
    with open(out_file, 'w', encoding='utf-8') as f:
        f.write(final_output)
        
    print(f" -> Generated: {out_file}")
    update_module_index(metadata, out_file)

def main():
    search_pattern = os.path.join(LEARNING_DIR, "raw-markdown", "**", "*.md")
    md_files = glob.glob(search_pattern, recursive=True)
    
    if not md_files:
        print("No markdown files found!")
        return

    print(f"Found {len(md_files)} lectures to compile.")
    tree = build_tree(md_files)
    
    for md_path in md_files:
        process_markdown_file(md_path, tree)
        
    print("Updating Global Index Navigation Bars...")
    update_all_index_navs(tree)
        
    print("Done! HTML files generated successfully.")

if __name__ == "__main__":
    main()
