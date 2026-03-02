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
import argparse

# enable argument parsing directly from command line for flexibility for the "certificate name" i.e ibm-data-engineering
arg_parser_object = argparse.ArgumentParser(description="Build HTML pages from Markdown lectures for IBM Data Engineering.", epilog='Check at the top of the script for configuration options.', prog="build-learning.py")

# parse in a single optional argument for the certificate name, default to "ibm-data-engineering"
arg_parser_object.add_argument('-c', '--certificate', type=str, default='ibm-data-engineering', help='The certificate name to build for (parsed in aexists in the tree please)')
args = arg_parser_object.parse_args()

# conifguration stuff for dirs
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__)) # current dir
REPO_ROOT = os.path.dirname(SCRIPT_DIR) # the dir parent to scripts dir
LEARNING_DIR = os.path.join(REPO_ROOT, "learning", "ibm-data-engineering") # where our classes live

# global dictionary to hold course metadata read from metadata.txt files in each course's raw-markdown directory
COURSE_METADATA = {}  # e.g. {'8': {'number': '8', 'name': 'ETL and Data Pipelines...'}, ...}

def load_all_course_metadata():
    """Scan raw-markdown/ for course directories containing metadata.txt and load course names."""
    global COURSE_METADATA
    raw_md_dir = os.path.join(LEARNING_DIR, "raw-markdown")
    if not os.path.exists(raw_md_dir):
        return
    for entry in sorted(os.listdir(raw_md_dir)):
        if entry.startswith('course-') and os.path.isdir(os.path.join(raw_md_dir, entry)):
            meta_path = os.path.join(raw_md_dir, entry, 'metadata.txt')
            if os.path.exists(meta_path):
                with open(meta_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                num_match = re.search(r'Course Number:\s*(\d+)', content)
                name_match = re.search(r'Course Name:\s*(.+)', content)
                if num_match:
                    c_num = num_match.group(1)
                    c_name = name_match.group(1).strip() if name_match else f"Course {c_num}"
                    COURSE_METADATA[c_num] = {'number': c_num, 'name': c_name}
    print(f"Loaded metadata for {len(COURSE_METADATA)} course(s): {', '.join(f'Course {k}' for k in sorted(COURSE_METADATA.keys(), key=lambda x: int(x) if x.isdigit() else x))}")

# here is the default HTML template for lectures, with placeholders for dynamic content like title, nav, and body
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

# functions to modularise the template generation process, starting with metadata extraction from filename and markdown content, then building a tree structure for navigation, generating nav HTML, updating index files with new nav, transforming raw HTML with BeautifulSoup for styling, and finally processing each markdown file to generate the final HTML output.
def extract_metadata(filename, md_text):
    """Extract metadata like Course, Module, Lecture numbers and Title."""
    metadata = {
        'course_num': 'X',
        'module_num': 'X',
        'lecture_num': 'X',
        'lecture_title': 'Untitled Lecture'
    } # fed in directly from the .md files later
    
    match_filename = re.search(r'course-(\d+)[/\\]module-(\d+)-lecture-(\d+)', filename.replace('\\', '/')) # regex to match file names
    if match_filename: # extracts appropriate metadata from the filename, which is expected to be in the format "course-{course_num}/module-{module_num}-lecture-{lecture_num}.md"
        metadata['course_num'] = match_filename.group(1)
        metadata['module_num'] = match_filename.group(2)
        metadata['lecture_num'] = match_filename.group(3)
        
    h1_match = re.search(r'^#\s+(.+)$', md_text, flags=re.MULTILINE) # extract the first H1 as the lecture title, which is expected to be in the format "# Lecture {lecture_num}: {Lecture Title}"
    if h1_match: # h1 is the title (heading) of the lecture, and we can further split it to get a cleaner title if it follows the expected format
        title_full = h1_match.group(1).strip()
        title_split = title_full.split(': ', 1)
        if len(title_split) > 1:
            metadata['lecture_title'] = title_split[1]
        else:
            metadata['lecture_title'] = title_full
            
    return metadata

# this method heere seeks to build a nested dictionary structure (tree) that organizes the lectures by course and module, which will be used later to generate the navigation dropdowns in the HTML. It reads all markdown files, extracts their metadata, and organizes them accordingly.
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

# This function attempts to read the existing index.html for a course or module to extract the title from the <title> tag. If it can't find it, it falls back to a default title like "Course {c}" or "Module {m}". This allows the navigation dropdowns to show more descriptive titles if they are already defined in the index.html files.
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

# This function generates the HTML for the navigation bar based on the current position in the course/module/lecture hierarchy. It creates dropdowns for courses, modules, and lectures, and marks the current page as active. The depth parameter indicates how deep we are in the hierarchy (0 for hub, 1 for course, 2 for module), which helps determine which dropdowns to show and how to format the links.
def generate_nav_html(tree, depth, current_c=None, current_m=None, current_l=None):
    if depth == 0: root_rel = "./"
    elif depth == 1: root_rel = "../"
    else: root_rel = "../../"
    
    course_titles = {}
    for c in tree.keys():
        if c in COURSE_METADATA:
            course_titles[c] = f"Course {c}: {COURSE_METADATA[c]['name']}"
        else:
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

# This function updates the navigation bar in an existing index.html file by replacing the entire <nav> block with a new one generated from the current tree structure. It uses a regex to find the <nav>...</nav> section and replaces it with the new HTML. This allows us to keep the existing structure and styling of the index.html files while updating the navigation links.
def update_index_nav_regex(filepath, nav_html):
    if not os.path.exists(filepath): return
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    # Replace the <nav> block
    new_content = re.sub(r'<nav>.*?</nav>', f'<nav>\n{nav_html}\n      </nav>', content, flags=re.DOTALL)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_content)
        
# This function iterates through all the index.html files for the hub, courses, and modules, and updates their navigation bars using the current tree structure. It ensures that all index pages have up-to-date navigation links reflecting any new lectures that were added.
def update_all_index_navs(tree):
    # learning hub (depth 0)
    hub_path = os.path.join(LEARNING_DIR, "index.html")
    nav_html = generate_nav_html(tree, depth=0)
    update_index_nav_regex(hub_path, nav_html)
    
    # cert courses (depth 1)
    for c in tree.keys():
        c_path = os.path.join(LEARNING_DIR, f"course-{c}", "index.html")
        nav_html = generate_nav_html(tree, depth=1, current_c=c)
        update_index_nav_regex(c_path, nav_html)
        
        # course modules (depth 2)
        for m in tree[c].keys():
            m_path = os.path.join(LEARNING_DIR, f"course-{c}", f"module-{m}", "index.html")
            nav_html = generate_nav_html(tree, depth=2, current_c=c, current_m=m)
            update_index_nav_regex(m_path, nav_html)

# This function takes the raw HTML generated from the markdown content and uses BeautifulSoup to manipulate it for better styling. It removes the original H1 (since we use it as the title), transforms mermaid code blocks into divs with appropriate classes for styling, converts blockquotes into styled callout boxes, and wraps sections under H2 headers into "section-card" divs with fade-in effects. It also adds fade-in classes to paragraphs for a nicer appearance.
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

# This function updates the module's index.html file to include a new card for the lecture that was just generated. It checks if a card for the lecture already exists (based on the filename), and if so, it replaces it with the new one. If not, it tries to find an "Upcoming" placeholder card to replace, or appends the new card at the end of the grid. The new card includes the lecture number, title, and description, and has fade-in classes for styling.
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

# This function processes a single markdown file to generate the corresponding HTML lecture page. It extracts metadata, converts markdown to HTML, applies transformations for styling, generates the navigation bar, and writes the final HTML output to the appropriate location. It also updates the module index page to include a card for this lecture.
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

# These functions dynamically generate hub, course, and module index pages from the tree and COURSE_METADATA.
# They ensure all courses with raw-markdown content get proper navigation pages.

def generate_hub_index(tree):
    """Generate the hub index.html with dynamic course cards for all courses with content."""
    hub_path = os.path.join(LEARNING_DIR, "index.html")
    nav_html = generate_nav_html(tree, depth=0)

    # Build course cards
    course_cards = ""
    delay = 3
    for c in sorted(tree.keys(), key=lambda x: int(x) if x.isdigit() else x):
        c_meta = COURSE_METADATA.get(c, {})
        c_name = c_meta.get('name', f'Course {c}')
        d = min(delay, 5)

        # Build module links for the expandable section
        module_links = f'          <a href="course-{c}/index.html" class="module-link">Go to Course Dashboard \u203a</a>\n'
        for m in sorted(tree[c].keys(), key=lambda x: int(x) if x.isdigit() else x):
            num_lectures = len(tree[c][m])
            module_links += f'          <a href="course-{c}/module-{m}/index.html" class="module-link">Module {m} ({num_lectures} lecture{"s" if num_lectures != 1 else ""})</a>\n'

        total_lectures = sum(len(tree[c][m]) for m in tree[c])
        num_modules = len(tree[c])
        desc = f"{num_modules} module{'s' if num_modules != 1 else ''}, {total_lectures} lecture{'s' if total_lectures != 1 else ''}. {c_name}."

        course_cards += f'''      <div class="hub-card fade-in fade-in-d{d}">
        <div class="card-level">Course {c}</div>
        <div class="card-title">{c_name}</div>
        <div class="card-desc">{desc}</div>
        \n        <button class="expand-btn" onclick="toggleExpand(this)">Expand to see more</button>
        <div class="expand-wrapper">
{module_links}        </div>
      </div>
'''
        delay += 1

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>IBM Data Engineering Hub</title>
  <link rel="stylesheet" href="style.css">
</head>
<body>
  <div class="page-wrapper" id="content">
    <div class="header-bar">
      <span class="brand">IBM Data Engineering</span>
      <nav>
{nav_html}
      </nav>
    </div>

    <h1 class="fade-in">\U0001f9e0 IBM Data Engineering Courses</h1>
    <p class="fade-in fade-in-d1" style="font-size:1.05rem;">
      Professional Certificate Learning Pathway<br>
      <span style="color:var(--text-muted);">Curated modules, lectures, and resources for comprehensive data engineering mastery.</span>
    </p>

    <h2 class="fade-in fade-in-d2">\U0001f4da Course Path</h2>
    
    <div class="hub-grid">
{course_cards}    </div>

    <div class="page-footer fade-in fade-in-d5">
      <p>Prepared by Paul Namalomba &middot; IBM Data Engineering</p>
    </div>
  </div>

  <script>
    function toggleExpand(btn) {{{{
      const card = btn.closest('.hub-card');
      card.classList.toggle('expanded');
      if (card.classList.contains('expanded')) {{{{
        btn.textContent = 'Show less';
      }}}} else {{{{
        btn.textContent = 'Expand to see more';
      }}}}
    }}}}
  </script>
</body>
</html>"""
    with open(hub_path, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f" -> Generated hub index: {hub_path}")


def generate_course_index(tree, course_num):
    """Generate a course-level index.html with module cards."""
    course_dir = os.path.join(LEARNING_DIR, f"course-{course_num}")
    os.makedirs(course_dir, exist_ok=True)
    index_path = os.path.join(course_dir, "index.html")

    c_meta = COURSE_METADATA.get(course_num, {})
    c_name = c_meta.get('name', f'Course {course_num}')
    nav_html = generate_nav_html(tree, depth=1, current_c=course_num)

    # Build module cards
    module_cards = ""
    delay = 3
    for m in sorted(tree[course_num].keys(), key=lambda x: int(x) if x.isdigit() else x):
        lectures = tree[course_num][m]
        d = min(delay, 5)

        lecture_links = f'          <a href="module-{m}/index.html" class="module-link">Go to Module Dashboard \u203a</a>\n'
        for lec in lectures:
            lecture_links += f'          <a href="module-{m}/{lec["filename"]}" class="module-link">Lecture {lec["num"]}: {lec["title"]}</a>\n'

        first_titles = ', '.join(lec['title'] for lec in lectures[:3])
        desc = f"{len(lectures)} lecture{'s' if len(lectures) != 1 else ''}: {first_titles}{'...' if len(lectures) > 3 else ''}."
        if len(desc) > 150: desc = desc[:147] + "..."

        module_cards += f'''\n      <div class="hub-card fade-in fade-in-d{d}">
        <div class="card-level">Module {m}</div>
        <div class="card-title">Module {m}</div>
        <div class="card-desc">{desc}</div>
        \n        <button class="expand-btn" onclick="toggleExpand(this)">Expand to see more</button>
        <div class="expand-wrapper">
{lecture_links}        </div>
      </div>
'''
        delay += 1

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Course {course_num}: {c_name}</title>
  <link rel="stylesheet" href="../style.css">
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
      <a href="../index.html">Hub</a> <span>&rsaquo;</span> Course {course_num}
    </div>

    <h1 class="fade-in">\U0001f4d8 Course {course_num}: {c_name}</h1>
    <p class="fade-in fade-in-d1" style="font-size:1.05rem;">
      Professional Certificate Learning Pathway
    </p>

    <h2 class="fade-in fade-in-d2">\U0001f4da Course Modules</h2>
    
    <div class="hub-grid">
{module_cards}    </div>

    <div class="page-footer fade-in fade-in-d5">
      <p>Prepared by Paul Namalomba &middot; IBM Data Engineering</p>
    </div>
  </div>

  <script>
    function toggleExpand(btn) {{{{
      const card = btn.closest('.hub-card');
      card.classList.toggle('expanded');
      if (card.classList.contains('expanded')) {{{{
        btn.textContent = 'Show less';
      }}}} else {{{{
        btn.textContent = 'Expand to see more';
      }}}}
    }}}}
  </script>
</body>
</html>"""
    with open(index_path, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f" -> Generated course index: {index_path}")


def generate_module_index_page(tree, course_num, module_num):
    """Generate a module-level index.html with lecture cards."""
    course_dir = os.path.join(LEARNING_DIR, f"course-{course_num}")
    module_dir = os.path.join(course_dir, f"module-{module_num}")
    os.makedirs(module_dir, exist_ok=True)
    index_path = os.path.join(module_dir, "index.html")

    c_meta = COURSE_METADATA.get(course_num, {})
    c_name = c_meta.get('name', f'Course {course_num}')
    nav_html = generate_nav_html(tree, depth=2, current_c=course_num, current_m=module_num)

    lectures = tree[course_num][module_num]

    # Build lecture cards as clickable links
    lecture_cards = ""
    delay = 3
    for lec in lectures:
        d = min(delay, 5)
        lecture_cards += f'''\n      <a href="{lec['filename']}" class="hub-card fade-in fade-in-d{d}">
        <div class="card-level">Lecture {lec['num']}</div>
        <div class="card-title">{lec['title']}</div>
        <div class="card-desc">Module {module_num}, Lecture {lec['num']}</div>
      </a>
'''
        delay += 1

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Module {module_num} &mdash; Course {course_num}: {c_name}</title>
  <link rel="stylesheet" href="../../style.css">
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
      <a href="../../index.html">Hub</a> <span>&rsaquo;</span> 
      <a href="../index.html">Course {course_num}</a> <span>&rsaquo;</span> 
      Module {module_num}
    </div>

    <h1 class="fade-in">\U0001f4d6 Module {module_num}</h1>
    <p class="fade-in fade-in-d1" style="font-size:1.05rem;">
      Course {course_num}: {c_name}
    </p>

    <h2 class="fade-in fade-in-d2">\U0001f4da Lectures</h2>
    
    <div class="hub-grid">
{lecture_cards}    </div>

    <div class="page-footer fade-in fade-in-d5">
      <p>Prepared by Paul Namalomba &middot; IBM Data Engineering</p>
    </div>
  </div>
</body>
</html>"""
    with open(index_path, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f" -> Generated module index: {index_path}")


# this method is the executor (orchestrator) that glues everything together. It loads course metadata, searches for all markdown files, builds the tree structure for navigation, processes each markdown file to generate HTML, generates all index pages, and finally updates all index navigation bars.
def main():
    # Step 1: load course metadata from metadata.txt files
    load_all_course_metadata()

    # Step 2: find and build tree from markdown files
    search_pattern = os.path.join(LEARNING_DIR, "raw-markdown", "**", "*.md")
    md_files = glob.glob(search_pattern, recursive=True)
    
    if not md_files:
        print("No markdown files found!")
        return

    print(f"Found {len(md_files)} lectures to compile.")
    tree = build_tree(md_files)
    
    # Step 3: process each markdown file to generate lecture HTML pages
    for md_path in md_files:
        process_markdown_file(md_path, tree)

    # Step 4: generate all index pages (hub, courses, modules) dynamically from the tree
    print("Generating index pages...")
    generate_hub_index(tree)
    for c in sorted(tree.keys(), key=lambda x: int(x) if x.isdigit() else x):
        generate_course_index(tree, c)
        for m in sorted(tree[c].keys(), key=lambda x: int(x) if x.isdigit() else x):
            generate_module_index_page(tree, c, m)

    # Step 5: update all navigation bars across existing index files to reflect the full tree
    print("Updating Global Index Navigation Bars...")
    update_all_index_navs(tree)
        
    print("Done! HTML files generated successfully.")

# runtime orchestration entry point
if __name__ == "__main__":
    main()
