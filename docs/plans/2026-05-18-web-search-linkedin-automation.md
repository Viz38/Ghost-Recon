# Web Search & LinkedIn Company Profile Discovery Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Automate the fallback web search and LinkedIn company profile extraction process for dead domains when primary archival scanning fails. Implement strict, multi-factor target selection and validation logic to prevent name collisions (e.g. matching wrong companies with similar names) and ensure that gathered raw data is 100% accurate.

**Architecture:** 
1. **Fallback Trigger**: Triggers *only* if the primary archival crawler fails (returning empty/block/under 300 characters).
2. **Domain-Prioritized Search Queries**: Generates query matrices heavily weighted towards the unique target domain (e.g. `"domain.com" site:linkedin.com/company/` and literal `"domain.com"` searches) rather than generic business name strings.
3. **Multi-Factor Target Selector**: Evaluates search candidates against a strict validation score:
   - base token overlap between clean name and domain name
   - explicit domain string match in link/snippet
   - website verification on scraped page
4. **LinkedIn Company Scraper with Domain Verification**: Public Playwright or API-based extraction that parses the profile's listed website and verifies it matches the target dead domain.
5. **Structured Data Assembler**: Assembles the validated snippets and verified profile data into a structured payload for downstream LLM classification. If no candidates pass the strict verification score, the orchestrator returns `"BLOCK: NO_VALID_TARGET"` to prevent writing junk metadata.

**Tech Stack:** Python 3.12, HTTPX, Beautiful Soup, Google Search/Serper API, Playwright/Camoufox, pytest.

---

## Technical Design & Safety Margins (Target Verification)

To eliminate name collisions and incorrect target selection, we will implement a multi-tiered scoring function:

$$\text{Validation Score} = \text{Domain String Match (50pts)} + \text{Domain Suffix Cleansed Token Match (30pts)} + \text{Listed Website Match (50pts)}$$

- **Domain String Match (+50 pts)**: Awarded if the dead domain string (e.g. `acmeelectric.com`) is present in the candidate URL, title, or search snippet.
- **Cleansed Token Match (up to +30 pts)**: Strips domain suffixes (`.com`, `.co.uk`, etc.) and organizational suffixes (`LLC`, `Inc`, `Corp`) and computes the Jaccard index or exact match of the core company name.
- **Listed Website Match (+50 pts)**: Awarded if the scraped LinkedIn company profile explicitly lists a website matching the target domain.
- **Strict Cutoff**: Any candidate scoring **below 50 points** is immediately discarded. If no search results cross the threshold, the system records `"BLOCK: NO_VALID_TARGET"`, protecting data integrity.

---

### Task 1: Domain-Prioritized Query Matrix Builder

**Files:**
- Create: `Integrated/utils/search_matrix.py`
- Test: `Integrated/tests/test_search_matrix.py`

**Step 1: Write the failing test**

Create `Integrated/tests/test_search_matrix.py`:
```python
import pytest
from utils.search_matrix import generate_company_queries

def test_generate_company_queries():
    domain = "acmeelectric.com"
    company_name = "Acme Electric"
    
    queries = generate_company_queries(domain, company_name)
    
    # Assert priority queries are domain-specific to reduce name collision
    assert len(queries) >= 3
    assert '"acmeelectric.com" site:linkedin.com/company/' in queries[0]
    assert '"acmeelectric.com"' in queries[1]
    assert 'site:linkedin.com/company/ "Acme Electric"' in queries[2]
```

**Step 2: Run test to verify it fails**

Run: `.venv/bin/python3 -m pytest tests/test_search_matrix.py`
Expected: FAIL with `ModuleNotFoundError: No module named 'utils.search_matrix'`

**Step 3: Write minimal implementation**

Create `Integrated/utils/search_matrix.py`:
```python
def generate_company_queries(domain: str, company_name: str) -> list[str]:
    clean_name = company_name.strip()
    return [
        f'"{domain}" site:linkedin.com/company/',
        f'"{domain}"',
        f'site:linkedin.com/company/ "{clean_name}"',
        f'"{clean_name}" (crunchbase OR zoominfo OR pitchbook)'
    ]
```

**Step 4: Run test to verify it passes**

Run: `.venv/bin/python3 -m pytest tests/test_search_matrix.py`
Expected: PASS

**Step 5: Commit**

```bash
git add Integrated/utils/search_matrix.py Integrated/tests/test_search_matrix.py
git commit -m "feat: implement domain-prioritized query matrix builder"
```

---

### Task 2: Multi-Factor Target Selector & Scoring Engine

**Files:**
- Create: `Integrated/utils/target_selector.py`
- Test: `Integrated/tests/test_target_selector.py`

**Step 1: Write the failing test**

Create `Integrated/tests/test_target_selector.py`:
```python
import pytest
from utils.target_selector import evaluate_candidate, select_best_candidate

def test_evaluate_candidate():
    domain = "acmeelectric.com"
    company_name = "Acme Electric"
    
    # 1. Perfect Match (Explicit domain and token overlap)
    good_cand = {"title": "Acme Electric: Overview | LinkedIn", "link": "https://www.linkedin.com/company/acme-electric", "snippet": "Acme Electric (acmeelectric.com) manufactures machinery."}
    score_good = evaluate_candidate(good_cand, domain, company_name)
    assert score_good >= 80
    
    # 2. Collision Match (Same name, wrong company/domain)
    bad_cand = {"title": "Acme Clothing: Overview | LinkedIn", "link": "https://www.linkedin.com/company/acme-clothing", "snippet": "Acme Clothing is a custom retail shirt shop."}
    score_bad = evaluate_candidate(bad_cand, domain, company_name)
    assert score_bad < 50

def test_select_best_candidate():
    domain = "acmeelectric.com"
    company_name = "Acme Electric"
    candidates = [
        {"title": "Acme Clothing", "link": "https://www.linkedin.com/company/acme-clothing", "snippet": "Clothing retail."},
        {"title": "Acme Electric: Overview", "link": "https://www.linkedin.com/company/acme-electric", "snippet": "Acme Electric (acmeelectric.com) tools."}
    ]
    
    best = select_best_candidate(candidates, domain, company_name)
    assert best["link"] == "https://www.linkedin.com/company/acme-electric"
```

**Step 2: Run test to verify it fails**

Run: `.venv/bin/python3 -m pytest tests/test_target_selector.py`
Expected: FAIL with `ModuleNotFoundError`

**Step 3: Write minimal implementation**

Create `Integrated/utils/target_selector.py`:
```python
import re

def evaluate_candidate(candidate: dict, domain: str, company_name: str) -> int:
    score = 0
    title_lower = candidate.get("title", "").lower()
    link_lower = candidate.get("link", "").lower()
    snippet_lower = candidate.get("snippet", "").lower()
    
    domain_clean = domain.lower().strip()
    core_domain = domain_clean.split(".")[0]
    
    # Factor 1: Explicit domain string match (+50 pts)
    if domain_clean in link_lower or domain_clean in title_lower or domain_clean in snippet_lower:
        score += 50
    elif core_domain in link_lower and len(core_domain) > 3:
        score += 20
        
    # Factor 2: Token match (cleansing company/domain extensions) (+30 pts max)
    name_clean = re.sub(r"\b(inc|llc|corp|co|ltd|limited)\b", "", company_name.lower()).strip()
    name_tokens = set(re.findall(r"\w+", name_clean))
    
    snippet_tokens = set(re.findall(r"\w+", snippet_lower + " " + title_lower))
    overlap = name_tokens.intersection(snippet_tokens)
    
    if name_tokens:
        overlap_ratio = len(overlap) / len(name_tokens)
        score += int(overlap_ratio * 30)
        
    return score

def select_best_candidate(candidates: list[dict], domain: str, company_name: str, threshold: int = 50) -> dict | None:
    scored_candidates = []
    for cand in candidates:
        score = evaluate_candidate(cand, domain, company_name)
        if score >= threshold:
            scored_candidates.append((score, cand))
            
    if not scored_candidates:
        return None
        
    # Return candidate with the highest score
    scored_candidates.sort(key=lambda x: x[0], reverse=True)
    return scored_candidates[0][1]
```

**Step 4: Run test to verify it passes**

Run: `.venv/bin/python3 -m pytest tests/test_target_selector.py`
Expected: PASS

**Step 5: Commit**

```bash
git add Integrated/utils/target_selector.py Integrated/tests/test_target_selector.py
git commit -m "feat: implement multi-factor target selection and validation engine"
```

---

### Task 3: LinkedIn Company Scraper & Website Cross-Verification

**Files:**
- Create: `Integrated/services/linkedin_company_scraper.py`
- Test: `Integrated/tests/test_linkedin_company_scraper.py`

**Step 1: Write the failing test**

Create `Integrated/tests/test_linkedin_company_scraper.py`:
```python
import pytest
from unittest.mock import patch, MagicMock
from services.linkedin_company_scraper import LinkedInCompanyScraper

@pytest.mark.asyncio
async def test_linkedin_company_scraping_and_website_check():
    enricher = LinkedInCompanyScraper(api_key="mock-proxycurl")
    mock_data = {
        "name": "Acme Electric",
        "description": "Manufacturer of industrial high-performance tools.",
        "website": "https://www.acmeelectric.com",
        "industry": "Electrical Manufacturing"
    }
    
    with patch("httpx.AsyncClient.get") as mock_get:
        mock_get.return_value = MagicMock(status_code=200, json=lambda: mock_data)
        profile = await enricher.scrape_company("https://www.linkedin.com/company/acme-electric")
        
        assert profile["website"] == "https://www.acmeelectric.com"
```

**Step 2: Run test to verify it fails**

Run: `.venv/bin/python3 -m pytest tests/test_linkedin_company_scraper.py`
Expected: FAIL with `ModuleNotFoundError`

**Step 3: Write minimal implementation**

Create `Integrated/services/linkedin_company_scraper.py`:
```python
import httpx
import os
import logging
import re
from utils.scraper import get_global_browser, html_to_markdown

class LinkedInCompanyScraper:
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("PROXYCURL_API_KEY", "")
        self.url = "https://nubela.co/api/v1/linkedin/company"
        
    async def scrape_company(self, company_url: str) -> dict:
        if self.api_key:
            headers = {"Authorization": f"Bearer {self.api_key}"}
            params = {"url": company_url}
            try:
                async with httpx.AsyncClient(timeout=30) as client:
                    resp = await client.get(self.url, headers=headers, params=params)
                    if resp.status_code == 200:
                        return resp.json()
            except Exception as e:
                logging.error(f"[COMPANY_SCRAPER] Proxycurl error: {e}")
                
        return await self._scrape_public_company(company_url)
        
    async def _scrape_public_company(self, company_url: str) -> dict:
        logging.info(f"[COMPANY_SCRAPER] Public Playwright scrape fallback for {company_url}")
        browser = await get_global_browser()
        ctx = await browser.new_context()
        page = await ctx.new_page()
        try:
            await page.goto(company_url, timeout=30000, wait_until="load")
            content = await page.content()
            title = await page.title()
            
            markdown = html_to_markdown(content)
            
            # Simple regex search to extract listed website from page contents
            website_match = re.search(r"website\s*:\s*(https?://[^\s'\"]+)", markdown, re.IGNORECASE)
            website = website_match.group(1) if website_match else ""
            
            return {
                "name": title.replace(" | LinkedIn", ""),
                "description": markdown[:4000],
                "website": website,
                "source": "Playwright Public Fallback"
            }
        except Exception as e:
            logging.error(f"[COMPANY_SCRAPER] Playwright fallback error: {e}")
        finally:
            await ctx.close()
        return {}
```

**Step 4: Run test to verify it passes**

Run: `.venv/bin/python3 -m pytest tests/test_linkedin_company_scraper.py`
Expected: PASS

**Step 5: Commit**

```bash
git add Integrated/services/linkedin_company_scraper.py Integrated/tests/test_linkedin_company_scraper.py
git commit -m "feat: implement company scraper with website extraction"
```

---

### Task 4: High-Fidelity Google Search Client

**Files:**
- Create: `Integrated/services/search_client.py`
- Test: `Integrated/tests/test_search_client.py`

**Step 1: Write the failing test**

Create `Integrated/tests/test_search_client.py` (Asserts Serper search execution and raw parsing).

**Step 2: Run test to verify it fails**

**Step 3: Implement SearchClient**

Create `Integrated/services/search_client.py` (Same clean HTTPX post request to Google/Serper search).

**Step 4: Run test to verify it passes**

**Step 5: Commit**

---

### Task 5: Raw Assembled Text Builder

**Files:**
- Create: `Integrated/utils/data_assembler.py`
- Test: `Integrated/tests/test_data_assembler.py`

**Step 1: Write the failing test**

Create `Integrated/tests/test_data_assembler.py` (Asserts correct construction of FALLBACK METADATA payload).

**Step 2: Run test to verify it fails**

**Step 3: Implement assemble_metadata_payload**

Create `Integrated/utils/data_assembler.py` (Combines validated search snippets and website-verified LinkedIn Company page description).

**Step 4: Run test to verify it passes**

**Step 5: Commit**

---

### Task 6: Fallback Pipeline & Verification Logic in ghost.py

**Files:**
- Modify: `Integrated/ghost.py:180-260`
- Test: `Integrated/tests/test_e2e_search_fallback.py`

**Step 1: Write the failing test**

Create `Integrated/tests/test_e2e_search_fallback.py` (Asserts that target validation operates cleanly: valid candidates are processed, and invalid ones are blocked with "BLOCK: NO_VALID_TARGET").

**Step 2: Run test to verify it fails**

**Step 3: Modify `Integrated/ghost.py`**

Modify the crawler worker loop:
```python
is_failed_scrape = not raw_content or raw_content.startswith("BLOCK:") or len(raw_content) < 300

if is_failed_scrape:
    logging.info(f"[ORCHESTRATOR] Archival crawl empty for {domain}. Running fallback target validation...")
    
    # 1. Generate domain-prioritized search queries
    queries = generate_company_queries(domain, company_name)
    candidates = []
    
    for q in queries[:2]:
        results = await self.search_client.search(q)
        candidates.extend(results)
        
    # 2. Apply strict Multi-Factor Target Selector
    best_candidate = select_best_candidate(candidates, domain, company_name, threshold=50)
    
    if not best_candidate:
        logging.warning(f"[ORCHESTRATOR] Mismatch/Junk detected. No candidate passed target verification for {domain}")
        raw_content = "BLOCK: NO_VALID_TARGET"
    else:
        # 3. Scrape verified candidate company page
        company_data = await self.company_scraper.scrape_company(best_candidate["link"])
        
        # 4. Check listed website matches domain (Bonus verification)
        profile_website = company_data.get("website", "").lower()
        if profile_website and domain.lower() not in profile_website:
            logging.warning(f"[ORCHESTRATOR] Website mismatch on page: {profile_website} vs target {domain}")
            # If search score was high but website explicitly mismatches, reject
            raw_content = "BLOCK: NO_VALID_TARGET"
        else:
            # 5. Assemble formatted markdown payload
            raw_content = assemble_metadata_payload(domain, [c["snippet"] for c in candidates[:4]], company_data)
            logging.info(f"[ORCHESTRATOR] Verified fallback data successfully scraped for {domain} ({len(raw_content)} chars)")
```

---

## Execution Handoff

After saving this plan, please choose an execution option:

**1. Subagent-Driven (this session)** - I dispatch a fresh browser/terminal subagent per task, review progress between tasks, and support fast TDD iterations.

**2. Parallel Session (separate)** - Open a new workspace session running in a clean worktree using the plan for batch execution.

Which approach would you like to take?
