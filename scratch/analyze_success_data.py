import json
import os
import re

def analyze():
    filepath = os.path.join(os.path.dirname(os.path.abspath(__file__)), "success_data_phase_1.json")
    if not os.path.exists(filepath):
        print("Data file not found.")
        return
        
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    print(f"Analyzing {len(data)} SUCCESS rows from Phase 1...")
    
    # Common parked domain keywords/regexes to look for (including new ones)
    parked_keywords = [
        "domain is for sale", "domain name for sale", "buy this domain", 
        "huge domains", "hugedomains", "sedo", "namecheap", "godaddy",
        "domain is registered", "parked free", "expired on", "domain expired", 
        "related searches", "related links", "under construction", "coming soon",
        "dns parking", "parked domain", "domainparking", "parking page",
        "this domain is parked", "this page is parked", "parked page",
        "registered at", "this domain has expired", "domainhasexpired",
        "buy domain", "purchase this domain", "renew this domain", "renew domain",
        "domain registration", "whois", "domain name is available", "domain is available",
        "registrar", "backorder", "domain host", "parking services", "parked on",
        "adblock", "sponsored listings", "search ads", "sponsored links"
    ]
    
    suspects = []
    
    for item in data:
        content = item["data_sample"].lower()
        matched = []
        for kw in parked_keywords:
            if kw in content:
                matched.append(kw)
        
        # Check for structural patterns like list of links/searches with high frequency
        # often parked pages have "Related Searches" followed by a list of terms
        links_count = len(re.findall(r"\[.*?\]\(.*?\)", content))
        # Parked domains usually have very few words and lots of links or empty text
        word_count = len(content.split())
        
        is_suspect = len(matched) > 0 or (links_count > 5 and word_count < 100) or ("related searches" in content)
        
        if is_suspect:
            suspects.append({
                "domain": item["domain"],
                "row": item["row"],
                "matched_keywords": matched,
                "length": item["length"],
                "word_count": word_count,
                "links_count": links_count,
                "sample": item["data_sample"][:300]
            })
            
    print(f"\nFound {len(suspects)} suspected parked domains:")
    for s in suspects:
        print(f"\nDomain: {s['domain']} (Row {s['row']})")
        print(f"Matched Keywords: {s['matched_keywords']}")
        print(f"Content Length: {s['length']} | Words: {s['word_count']} | Links: {s['links_count']}")
        print(f"Sample:\n{s['sample'].strip()}")
        print("-" * 50)
        
    print(f"\nTotal suspects: {len(suspects)} out of {len(data)} SUCCESS rows.")

if __name__ == "__main__":
    analyze()
