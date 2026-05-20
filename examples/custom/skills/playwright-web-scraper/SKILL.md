---
name: playwright-web-scraper
description: Scrape websites using Playwright and saves token-efficient Markdown to a file.
---

# Web Scraper Skill

When you need to extract information from a website, use the `scrape.py` script to render the JavaScript and extract the data.

## Usage Instructions

Because websites contain massive amounts of text, **you must output the results to a temporary file** and then read that file. If you do not use an output file, your terminal buffer will deadlock and hang.

**Pathing Instruction:**
The script is located in the `scripts` folder **in the exact same directory as this SKILL.md file**. You must construct the correct relative path from your current terminal working directory.

### Step 1: Run the Scraper (using `uv run`)
Run the script and output it to a local markdown file (e.g., `scraped_data.md`).

`execute('uv run scripts/scrape.py --url "https://example.com" --output "scraped_data.md')`
