import asyncio
import httpx
from bs4 import BeautifulSoup
from markdownify import markdownify as md
import logging

def html_to_markdown_debug(html):
    try:
        if not html: return "EMPTY HTML"
        soup = BeautifulSoup(html, "html.parser")
        
        print(f"DEBUG: Raw HTML Length: {len(html)}")
        
        # Check if it's a parked domain page (often very short or full of scripts)
        scripts = soup.find_all("script")
        print(f"DEBUG: Found {len(scripts)} scripts")
        
        # Test decomposition
        tags_to_strip = ["script", "style", "svg", "iframe", ".ads", "#wm-ipp"]
        # Removing 'nav' and 'footer' from strip list for now to see if it helps
        for s in soup(tags_to_strip): s.decompose()
        
        main = soup.find('main') or soup.find('article') or soup.body or soup
        content = md(str(main), heading_style="ATX", strip=['a', 'img', 'button']).strip()
        
        print(f"DEBUG: Processed Content Length: {len(content)}")
        return content[:500] + "..." if len(content) > 500 else content
    except Exception as e:
        return f"ERROR: {e}"

async def test_url(url):
    print(f"\n--- Testing: {url} ---")
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    try:
        async with httpx.AsyncClient(timeout=20, verify=False, follow_redirects=True) as client:
            resp = await client.get(url, headers=headers)
            print(f"DEBUG: Status Code: {resp.status_code}")
            if resp.status_code == 200:
                print(html_to_markdown_debug(resp.text))
            else:
                print(f"DEBUG: Response Text (first 200 chars): {resp.text[:200]}")
    except Exception as e:
        print(f"DEBUG: Request Error: {e}")

async def main():
    # A few URLs that failed with Length: 0
    urls = [
        "https://web.archive.org/web/20210515123456id_/http://integratedpackaging.com/",
        "https://web.archive.org/web/20200515123456id_/http://labelelettronica.it/",
        "https://web.archive.org/web/20190515123456id_/http://springer-gmbh.com/"
    ]
    for url in urls:
        await test_url(url)

if __name__ == "__main__":
    asyncio.run(main())
