# GitHub Stats Generation

This directory contains GitHub statistics generated automatically by GitHub Actions.

## Files

- `github-stats.svg` - Overall GitHub statistics (repos, followers, stars, etc.)
- `top-languages.svg` - Top programming languages by repository count
- `cache.json` - Cached API responses (1-hour TTL to respect rate limits)

## How It Works

1. **GitHub Action** (`.github/workflows/generate-stats.yml`) runs daily at midnight UTC
2. **Python script** (`scripts/generate_stats.py`) fetches data from GitHub API
3. **SVG files** are generated with current statistics
4. **Auto-commit** pushes updated SVGs back to the repository
5. **README** displays the SVGs via raw GitHub URLs

## Rate Limiting

- Uses `GITHUB_TOKEN` for authenticated API calls (5,000 requests/hour)
- Implements 1-hour cache to minimize API calls
- Falls back to cached data if rate limit is reached

## Manual Update

To manually trigger stats generation:

1. Go to **Actions** tab in GitHub
2. Select **Generate GitHub Stats** workflow
3. Click **Run workflow**

## Local Testing

```bash
# Install dependencies
pip install requests Pillow

# Run script (works without token, but has lower rate limits)
python scripts/generate_stats.py

# OR with token for higher rate limits (optional)
# Linux/Mac:
export GITHUB_TOKEN="your_token_here"
export GITHUB_USERNAME="paulnamalomba"
python scripts/generate_stats.py

# Windows PowerShell:
$env:GITHUB_TOKEN="your_token_here"
$env:GITHUB_USERNAME="paulnamalomba"
python scripts/generate_stats.py
```

The generated SVG files will be in the `stats/` directory.

**Note**: The script works without a token (60 requests/hour) but using a token increases the limit to 5,000 requests/hour.
