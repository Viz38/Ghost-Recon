# Ghost Hitrate Optimization Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Improve archival hit rate to >80% by implementing multi-page stitching, semantic scoring, and adversarial parking detection.

**Architecture:** Transition from a single-snapshot model to a "Synthetic Business Resume" model. We will score snapshots based on semantic density, detect sophisticated parking pages via network/DOM analysis, and stitch multiple sub-pages from the same "Golden Era" into a consolidated record.

**Tech Stack:** Python (Asyncio), Playwright (Camoufox), BeautifulSoup4, Internet Archive SDK.

---

### Task 1: Semantic Signal Density Scoring

**Files:**
- Modify: `Ghost P1/engine/forensics.py`
- Modify: `Ghost P2/engine/forensics.py`

**Step 1: Implement Signal Scoring Logic**
Add a helper to calculate text-to-link ratio and detect business entities (CEO, Founder, etc.) in the snapshot metadata and URL.

**Step 2: Update `_select_golden_era_snapshots`**
Integrate the new scoring into the quality analysis loop.

**Step 3: Verification**
Mock a CDX response with one "parked-lookalike" (high links) and one "business" snapshot (high text density) and ensure the business one is ranked higher.

---

### Task 2: Adversarial Parking Detection

**Files:**
- Modify: `Ghost P1/utils/scraper.py`
- Modify: `Ghost P2/utils/scraper.py`

**Step 1: Add Ad-Network Detection**
Implement a check in `scrape_url` to detect known parking ad networks (Sedo, Afternic, Bodis) in the page content and outgoing requests.

**Step 2: Implement Accessibility Tree Check**
Use `page.accessibility.snapshot()` to detect if the page is a "thin" parking wrapper.

**Step 3: Verification**
Test against a known parked domain snapshot.

---

### Task 4: Era-Synchronized Stitching

**Files:**
- Modify: `Ghost P1/ghost.py`
- Modify: `Ghost P1/utils/scraper.py`
- Modify: `Ghost P2/ghost.py`
- Modify: `Ghost P2/utils/scraper.py`

**Step 1: Implement Multi-Page Scrape**
Modify `scrape_url` to accept a list of related archival URLs and scrape them in parallel.

**Step 2: Update `_stage_archival_extraction`**
When a snapshot is selected, identify its "era" (year) and find snapshots for `/about` and `/products` from that same year.

**Step 3: Verification**
Run on a domain with known historical sub-pages and verify the final `raw_data` contains merged content.

---

### Task 5: Adaptive Re-Probing Loop

**Files:**
- Modify: `Ghost P1/ghost.py`
- Modify: `Ghost P2/ghost.py`

**Step 1: Implement Content Depth Check**
In the extraction loop, if the returned content is < 1000 characters, flag it as "Sparse".

**Step 2: Automatic Fallback**
If "Sparse", the engine must NOT stop but instead fetch the next 2-3 highest-ranked candidates and append their content.

**Step 3: Verification**
Verify that the engine continues to the 4th snapshot if the 1st one returns minimal text.

---

### Task 6: IA Item Fallback (Digital Brochure Recovery)

**Files:**
- Modify: `Ghost P1/engine/forensics.py`
- Modify: `Ghost P2/engine/forensics.py`

**Step 1: Implement IA Catalog Search**
Finalize the `search_ia_items` method using Lucene syntax to find non-snapshot files (PDFs, docs).

**Step 2: Integrate into Discovery**
If `forensic_results` from CDX is empty, trigger the IA Catalog search as a last-resort fallback.

**Step 3: Verification**
Test with a domain that has no snapshots but has uploaded items in IA.
