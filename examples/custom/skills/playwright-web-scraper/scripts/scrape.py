#!/usr/bin/env python3

import argparse
import asyncio
import sys
from bs4 import BeautifulSoup
import markdownify
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeout
from playwright_stealth import Stealth

def clean_html_to_markdown(html_content: str) -> str:
    soup = BeautifulSoup(html_content, 'html.parser')
    for element in soup(["script", "style", "noscript", "meta", "nav", "footer", "header", "svg"]):
        element.extract()
    md = markdownify.markdownify(str(soup), heading_style="ATX")
    return "\n".join([line for line in md.splitlines() if line.strip()])

async def scrape_url(url: str, timeout: int, output_file: str):
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    viewport = {"width": 1920, "height": 1080}
    locale = "en-US"

    async with async_playwright() as p:
        # FIX: Added arguments to prevent background/agent terminal hanging
        browser = await p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-setuid-sandbox", "--disable-dev-shm-usage"]
        )
        context = await browser.new_context(user_agent=user_agent)
        page = await context.new_page()
        stealth_instance = Stealth()
        await stealth_instance.apply_stealth_async(page)

        try:
            await page.goto(url, wait_until="networkidle", timeout=timeout)
            await page.wait_for_timeout(3000)

            title = await page.title()
            html_content = await page.content()

            links = await page.evaluate('''() => {
                const links = Array.from(document.querySelectorAll('a'));
                return links.map(a => ({ text: a.innerText.trim(), href: a.href }))
                            .filter(a => a.href && a.href.startsWith('http') && a.text !== '');
            }''')

            md_content = clean_html_to_markdown(html_content)

            # Format the final output
            final_output = f"# TITLE: {title}\n\n## CONTENT:\n\n{md_content}\n\n## TOP 20 OUTBOUND LINKS:\n\n"
            for link in links[:20]:
                final_output += f"- [{link['text']}]({link['href']})\n"

            # FIX: Write to a file instead of terminal stdout to prevent buffer deadlocks
            if output_file:
                with open(output_file, "w", encoding="utf-8") as f:
                    f.write(final_output)
                print(f"SUCCESS: Scraped {url}. Results saved to {output_file}")
            else:
                print(final_output, end="")
                print(f"\n\n[Scraped {url}]")

        except PlaywrightTimeout:
            print(f"ERROR: Timeout reached ({timeout}ms).", file=sys.stderr)
            sys.exit(1)
        except Exception as e:
            print(f"ERROR: {str(e)}", file=sys.stderr)
            sys.exit(1)
        finally:
            await browser.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", required=True)
    parser.add_argument("--timeout", type=int, default=30000)
    # Require an output file
    parser.add_argument("--output", default=None, help="File to save the markdown output (optional, prints to stdout if not provided)")

    args = parser.parse_args()
    asyncio.run(scrape_url(args.url, args.timeout, args.output))
