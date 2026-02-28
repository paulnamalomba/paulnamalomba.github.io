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
          tertiaryColor: '#1a2340'
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
        <a href="{root_relative_path}index.html">Hub</a>
        <a href="{course_relative_path}index.html">Course {course_num}</a>
        <a href="index.html">Module {module_num}</a>
        <a href="#" class="active">Lecture {lecture_num}</a>
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
    # Heuristics for course/module/lecture from text or filename
    metadata = {
        'course_num': 'X',
        'module_num': 'X',
        'lecture_num': 'X',
        'lecture_title': 'Untitled Lecture'
    }
    
    # E.g. raw-markdown/module-8/module-4-lecture-1.md -> course 8? or course is from parent?
    # Usually `module-8` means Course 8, and `module-4-lecture-1.md` means Module 4, Lecture 1.
    match_filename = re.search(r'module-(\d+)[\/\\]module-(\d+)-lecture-(\d+)', filename.replace('\\', '/'))
    if match_filename:
        metadata['course_num'] = match_filename.group(1)
        metadata['module_num'] = match_filename.group(2)
        metadata['lecture_num'] = match_filename.group(3)
        
    # Extract Title from H1
    h1_match = re.search(r'^#\s+(.+)$', md_text, flags=re.MULTILINE)
    if h1_match:
        # Check if title looks like "Module 4, Lecture 2: Apache Kafka"
        title_full = h1_match.group(1).strip()
        title_split = title_full.split(': ', 1)
        if len(title_split) > 1:
            metadata['lecture_title'] = title_split[1]
        else:
            metadata['lecture_title'] = title_full
            
    return metadata

def transform_html_with_bs4(raw_html):
    """
    Applies aggressive beautification transformations using BeautifulSoup.
    - Wraps H2+siblings into `<div class="section-card fade-in">`
    - Transforms Mermaid code blocks into visual graph containers
    - Transforms BlockQuotes into stylised callouts.
    """
    soup = BeautifulSoup(raw_html, 'html.parser')
    
    # Strip H1 as it's already generated in the HTML_TEMPLATE header
    for h1 in soup.find_all('h1'):
        h1.decompose()
        
    # Transform Mermaid blocks
    for code in soup.find_all('code', class_='language-mermaid'):
        pre = code.parent
        if pre and pre.name == 'pre':
            mermaid_text = code.get_text()
            # Create container
            container = soup.new_tag('div', style="background:var(--bg-surface); padding:1rem; border-radius:var(--radius); margin: 1rem 0; overflow-x: auto; display:flex; justify-content:center;")
            container['class'] = 'mermaid-container'
            
            mermaid_pre = soup.new_tag('pre', **{'class': 'mermaid'})
            mermaid_pre.string = mermaid_text
            
            container.append(mermaid_pre)
            pre.replace_with(container)

    # Transform Blockquotes into Callouts
    for bq in soup.find_all('blockquote'):
        div_callout = soup.new_tag('div', **{'class': 'callout tip'})
        
        # Check if first paragraph starts with an emoji or '💡 Summary'
        first_p = bq.find('p')
        if first_p:
            text = first_p.get_text()
            if text.startswith('💡 '):
                # Extract title
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

    # Wrap sections starting with H2
    # We will iterate elements in the body and collect them into cards
    body_elements = list(soup.contents)
    new_soup = BeautifulSoup('', 'html.parser')
    
    current_card = None
    delay_index = 2

    for el in body_elements:
        if isinstance(el, Tag) and el.name == 'h2':
            # Start a new card
            current_card = soup.new_tag('div')
            current_card['class'] = f'section-card fade-in fade-in-d{delay_index}'
            delay_index = min(delay_index + 1, 5) # Cap at d5
            
            new_soup.append(current_card)
            current_card.append(el.extract())
        elif current_card is not None:
            # Append to current card
            if isinstance(el, Tag):
                current_card.append(el.extract())
            else:
                current_card.append(el)
        else:
            # Elements before first H2 (like intro paragraphs)
            if isinstance(el, Tag) and el.name == 'p':
                el['class'] = f"fade-in fade-in-d{delay_index}"
            if isinstance(el, Tag):
                new_soup.append(el.extract())
            else:
                new_soup.append(el)
                
    return str(new_soup)

def update_module_index(metadata, lecture_html_path):
    """
    Updates the target module's index.html file to include a link to the newly generated lecture.
    If the lecture is already linked in the hub-grid, it will replace its title/desc.
    """
    course_dir = os.path.join(LEARNING_DIR, f"course-{metadata['course_num']}")
    module_dir = os.path.join(course_dir, f"module-{metadata['module_num']}")
    index_path = os.path.join(module_dir, "index.html")
    
    if not os.path.exists(index_path):
        print(f"Warning: Module index not found at {index_path}. Skipping grid update.")
        return
        
    with open(index_path, 'r', encoding='utf-8') as f:
        html_content = f.read()
        
    soup = BeautifulSoup(html_content, 'html.parser')
    grid = soup.find('div', class_='hub-grid')
    
    if not grid:
        print(f"Warning: hub-grid not found in {index_path}. Skipping grid update.")
        return
        
    # Check if a card for this lecture already exists
    filename = os.path.basename(lecture_html_path)
    existing_card = soup.find('a', href=filename)
    
    # Calculate an intro description from metadata if possible, otherwise placeholder
    desc = metadata.get('description', 'Auto-generated lecture content.')
    
    # Create the card HTML
    # We use a delay index based on existing number of valid cards (roughly)
    existing_links = len(grid.find_all('a', class_='hub-card'))
    delay_index = min(3 + existing_links, 5)
    
    card_html = f"""
      <a href="{filename}" class="hub-card fade-in fade-in-d{delay_index}">
        <div class="card-level">Lecture {metadata['lecture_num']}</div>
        <div class="card-title">{metadata['lecture_title']}</div>
        <div class="card-desc">{desc}</div>
      </a>
"""
    new_card_soup = BeautifulSoup(card_html, 'html.parser')
    
    if existing_card:
        existing_card.replace_with(new_card_soup.a)
        print(f"   -> Updated existing card for {filename} in module index.")
    else:
        # Find the placeholder if it exists, insert before it
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
            
        print(f"   -> Appended new card for {filename} to module index.")
        
    # Write back
    with open(index_path, 'w', encoding='utf-8') as f:
        # We replace the raw HTML to prevent bs4 from messing with the entire document formatting
        # just for this one grid update
        # However, to be safe, we just write the pretty soup string back for the entire file
        f.write(soup.prettify(formatter="html"))

def process_markdown_file(md_path):
    print(f"Processing: {md_path}")
    with open(md_path, 'r', encoding='utf-8') as f:
        md_text = f.read()

    metadata = extract_metadata(md_path, md_text)
    
    # Extract first paragraph logic to become the description
    desc_match = re.search(r'^[^#\n].+', md_text, flags=re.MULTILINE)
    if desc_match:
        # take the first 120 chars
        desc = desc_match.group(0).strip()
        if len(desc) > 120:
            desc = desc[:117] + "..."
        metadata['description'] = desc
    
    # Markdown -> HTML
    raw_html = markdown.markdown(md_text, extensions=['fenced_code', 'tables'])
    
    # BS4 Transformation
    processed_html = transform_html_with_bs4(raw_html)
    
    # Calculate relative paths for CSS / links based on depth
    # e.g., learning/ibm-data-engineering/course-8/module-4/lecture-1.html
    # depth is 2 relative to ibm-data-engineering
    css_relative_path = "../../style.css"
    root_relative_path = "../../"
    course_relative_path = "../"
    
    final_output = HTML_TEMPLATE.format(
        page_title=f"Lecture {metadata['lecture_num']}: {metadata['lecture_title']}",
        css_relative_path=css_relative_path,
        root_relative_path=root_relative_path,
        course_relative_path=course_relative_path,
        course_num=metadata['course_num'],
        module_num=metadata['module_num'],
        lecture_num=metadata['lecture_num'],
        lecture_title=metadata['lecture_title'],
        body_html=processed_html
    )
    
    # Output path
    # e.g., course-8/module-4/lecture-1.html
    course_dir = os.path.join(LEARNING_DIR, f"course-{metadata['course_num']}")
    module_dir = os.path.join(course_dir, f"module-{metadata['module_num']}")
    
    os.makedirs(module_dir, exist_ok=True)
    out_file = os.path.join(module_dir, f"lecture-{metadata['lecture_num']}.html")
    
    with open(out_file, 'w', encoding='utf-8') as f:
        f.write(final_output)
        
    print(f" -> Generated: {out_file}")
    
    # Update the module index!
    update_module_index(metadata, out_file)

def main():
    search_pattern = os.path.join(LEARNING_DIR, "raw-markdown", "**", "*.md")
    md_files = glob.glob(search_pattern, recursive=True)
    
    if not md_files:
        print("No markdown files found!")
        return

    print(f"Found {len(md_files)} lectures to compile.")
    for md_path in md_files:
        process_markdown_file(md_path)
        
    print("Done! HTML files generated successfully.")

if __name__ == "__main__":
    main()
