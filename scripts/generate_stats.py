#!/usr/bin/env python3
"""
Generate GitHub statistics as SVG files using GitHub API.
Includes caching and rate limit handling.
"""

import os
import json
import requests
from datetime import datetime
from pathlib import Path

# Configuration
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
GITHUB_USERNAME = os.getenv('GITHUB_USERNAME', 'paulnamalomba')
OUTPUT_DIR = Path('stats')
CACHE_FILE = OUTPUT_DIR / 'cache.json'

# Create output directory
OUTPUT_DIR.mkdir(exist_ok=True)

# GitHub API headers - only include Authorization if token is available
HEADERS = {'Accept': 'application/vnd.github.v3+json'}
if GITHUB_TOKEN:
    HEADERS['Authorization'] = f'token {GITHUB_TOKEN}'
    print("✓ Using authenticated GitHub API (5,000 req/hour)")
else:
    print("⚠️  No GITHUB_TOKEN found - using unauthenticated API (60 req/hour)")
    print("   Set GITHUB_TOKEN environment variable for higher rate limits")


def get_github_stats():
    """Fetch GitHub stats from API with caching."""
    
    # Check cache first
    if CACHE_FILE.exists():
        with open(CACHE_FILE, 'r') as f:
            cache = json.load(f)
            cache_time = datetime.fromisoformat(cache['timestamp'])
            # Use cache if less than 1 hour old
            if (datetime.now() - cache_time).seconds < 3600:
                print("Using cached data")
                return cache['data']
    
    print("Fetching fresh data from GitHub API...")
    
    # Fetch user data
    user_url = f'https://api.github.com/users/{GITHUB_USERNAME}'
    user_response = requests.get(user_url, headers=HEADERS)
    user_response.raise_for_status()
    user_data = user_response.json()
    
    # Fetch repositories
    repos_url = f'https://api.github.com/users/{GITHUB_USERNAME}/repos?per_page=100&type=owner'
    repos_response = requests.get(repos_url, headers=HEADERS)
    repos_response.raise_for_status()
    repos_data = repos_response.json()
    
    # Calculate stats
    total_stars = sum(repo['stargazers_count'] for repo in repos_data)
    total_forks = sum(repo['forks_count'] for repo in repos_data)
    
    # Language statistics
    languages = {}
    for repo in repos_data:
        if repo['language']:
            languages[repo['language']] = languages.get(repo['language'], 0) + 1
    
    # Sort languages by count
    top_languages = sorted(languages.items(), key=lambda x: x[1], reverse=True)[:5]
    
    stats = {
        'public_repos': user_data['public_repos'],
        'followers': user_data['followers'],
        'following': user_data['following'],
        'total_stars': total_stars,
        'total_forks': total_forks,
        'top_languages': top_languages,
        'created_at': user_data['created_at']
    }
    
    # Cache the data
    cache_data = {
        'timestamp': datetime.now().isoformat(),
        'data': stats
    }
    with open(CACHE_FILE, 'w') as f:
        json.dump(cache_data, f, indent=2)
    
    return stats


def generate_stats_svg(stats):
    """Generate SVG with GitHub statistics."""
    
    # Calculate account age
    created_date = datetime.fromisoformat(stats['created_at'].replace('Z', '+00:00'))
    account_age_days = (datetime.now().replace(tzinfo=created_date.tzinfo) - created_date).days
    account_age_years = account_age_days / 365.25
    
    svg_content = f'''<svg width="495" height="195" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <style>
      .title {{ fill: #58a6ff; font-size: 18px; font-weight: bold; font-family: 'Segoe UI', Ubuntu, Sans-Serif; }}
      .stat {{ fill: #c9d1d9; font-size: 14px; font-family: 'Segoe UI', Ubuntu, Sans-Serif; }}
      .label {{ fill: #8b949e; font-size: 12px; font-family: 'Segoe UI', Ubuntu, Sans-Serif; }}
      .icon {{ fill: #8b949e; }}
    </style>
  </defs>
  
  <rect width="495" height="195" fill="#0d1117" stroke="#30363d" stroke-width="1" rx="4.5"/>
  
  <text x="25" y="35" class="title">📊 GitHub Statistics</text>
  
  <!-- Stats Grid -->
  <g transform="translate(25, 60)">
    <!-- Public Repos -->
    <text x="0" y="0" class="label">📦 Public Repos:</text>
    <text x="200" y="0" class="stat">{stats['public_repos']}</text>
    
    <!-- Followers -->
    <text x="0" y="25" class="label">👥 Followers:</text>
    <text x="200" y="25" class="stat">{stats['followers']}</text>
    
    <!-- Following -->
    <text x="0" y="50" class="label">➡️  Following:</text>
    <text x="200" y="50" class="stat">{stats['following']}</text>
    
    <!-- Total Stars -->
    <text x="0" y="75" class="label">⭐ Total Stars:</text>
    <text x="200" y="75" class="stat">{stats['total_stars']}</text>
    
    <!-- Total Forks -->
    <text x="0" y="100" class="label">🔱 Total Forks:</text>
    <text x="200" y="100" class="stat">{stats['total_forks']}</text>
    
    <!-- Account Age -->
    <text x="0" y="125" class="label">📅 Account Age:</text>
    <text x="200" y="125" class="stat">{account_age_years:.1f} years</text>
  </g>
  
  <text x="470" y="185" class="label" text-anchor="end">Updated: {datetime.now().strftime('%Y-%m-%d')}</text>
</svg>'''
    
    output_file = OUTPUT_DIR / 'github-stats.svg'
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(svg_content)
    
    print(f"Generated: {output_file}")


def generate_languages_svg(stats):
    """Generate SVG with top programming languages."""
    
    top_langs = stats['top_languages'][:5]
    total = sum(count for _, count in top_langs)
    
    # Language colors (GitHub standard colors)
    lang_colors = {
        'Python': '#3572A5',
        'JavaScript': '#f1e05a',
        'TypeScript': '#2b7489',
        'C++': '#f34b7d',
        'C#': '#178600',
        'Fortran': '#4d41b1',
        'Java': '#b07219',
        'HTML': '#e34c26',
        'CSS': '#563d7c',
        'Shell': '#89e051',
        'PowerShell': '#012456',
        'Jupyter Notebook': '#DA5B0B'
    }
    
    svg_height = 50 + len(top_langs) * 30 + 20
    
    svg_content = f'''<svg width="300" height="{svg_height}" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <style>
      .title {{ fill: #58a6ff; font-size: 16px; font-weight: bold; font-family: 'Segoe UI', Ubuntu, Sans-Serif; }}
      .lang {{ fill: #c9d1d9; font-size: 13px; font-family: 'Segoe UI', Ubuntu, Sans-Serif; }}
      .percent {{ fill: #8b949e; font-size: 12px; font-family: 'Segoe UI', Ubuntu, Sans-Serif; }}
    </style>
  </defs>
  
  <rect width="300" height="{svg_height}" fill="#0d1117" stroke="#30363d" stroke-width="1" rx="4.5"/>
  
  <text x="15" y="30" class="title">💻 Top Languages</text>
  
  <g transform="translate(15, 50)">
'''
    
    y_offset = 0
    for lang, count in top_langs:
        percentage = (count / total) * 100
        color = lang_colors.get(lang, '#8b949e')
        
        svg_content += f'''    <!-- {lang} -->
    <circle cx="5" cy="{y_offset + 5}" r="5" fill="{color}"/>
    <text x="20" y="{y_offset + 10}" class="lang">{lang}</text>
    <text x="270" y="{y_offset + 10}" class="percent" text-anchor="end">{percentage:.1f}%</text>
'''
        y_offset += 30
    
    svg_content += '''  </g>
</svg>'''
    
    output_file = OUTPUT_DIR / 'top-languages.svg'
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(svg_content)
    
    print(f"Generated: {output_file}")


def main():
    """Main execution function."""
    try:
        print(f"Generating GitHub stats for: {GITHUB_USERNAME}")
        
        # Fetch stats
        stats = get_github_stats()
        
        # Generate SVGs
        generate_stats_svg(stats)
        generate_languages_svg(stats)
        
        print("\n✅ Stats generation complete!")
        print(f"📁 Output directory: {OUTPUT_DIR.absolute()}")
        
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 403:
            print("⚠️  Rate limit exceeded. Please try again later.")
            print(f"Rate limit info: {e.response.headers.get('X-RateLimit-Remaining', 'N/A')} remaining")
        else:
            print(f"❌ HTTP Error: {e}")
        raise
    except Exception as e:
        print(f"❌ Error: {e}")
        raise


if __name__ == '__main__':
    main()
