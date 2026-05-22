import json
import os
import re

def analyze_quality():
    filepath = os.path.join(os.path.dirname(os.path.abspath(__file__)), "success_data_raw_phase_1.json")
    if not os.path.exists(filepath):
        print("Raw success data file not found.")
        return
        
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    print(f"============================================================")
    print(f"ANALYZING QUALITY OF {len(data)} SUCCESS ROWS FROM PHASE 1")
    print(f"============================================================\n")
    
    categories = {
        "ia_leak": [],       # Internet Archive Main Page leak
        "parked": [],        # Parked domain/For Sale/GoDaddy/Plesk
        "placeholder": [],   # Under construction/Coming soon/Maintenance
        "real": [],          # Plausible real content
    }
    
    ia_keywords = [
        "ask the publishers", "internet archive audio", "grateful dead", 
        "librivox", "netlabels", "78 rpms", "curated by the internet archive",
        "live music archive", "metropolitan museum"
    ]
    
    parked_keywords = [
        "domain is for sale", "domain name for sale", "buy this domain", "buy domain",
        "huge domains", "hugedomains", "sedo", "parked free", "expired on",
        "domain expired", "domain name expired", "this domain has expired",
        "dns parking", "parked domain", "domainparking", "parking page", "parked page",
        "this domain is parked", "this page is parked", "purchase this domain",
        "renew this domain", "renew domain", "domain name is available", "domain is available",
        "parking services", "parked on", "available for sale", "godaddy", "namecheap",
        "parallels plesk panel", "cpanel holding page", "zen internet | cpanel", "hosted by one.com"
    ]
    
    placeholder_keywords = [
        "coming soon", "under construction", "site is under construction",
        "website under construction", "check back soon", "launching soon",
        "new website coming soon", "will be back soon", "maintenance mode",
        "down for maintenance", "temporary maintenance", "check back later"
    ]
    
    for item in data:
        content = item["raw_data"].lower()
        domain = item["domain"]
        row = item["row"]
        method = item["method"]
        length = len(content)
        
        # Determine category
        is_ia = any(kw in content for kw in ia_keywords)
        is_parked = any(kw in content for kw in parked_keywords)
        is_placeholder = any(kw in content for kw in placeholder_keywords)
        
        if is_ia:
            categories["ia_leak"].append(item)
        elif is_parked:
            categories["parked"].append(item)
        elif is_placeholder:
            categories["placeholder"].append(item)
        else:
            categories["real"].append(item)
            
    # Print results
    print(f"Summary Statistics:")
    print(f"-------------------")
    print(f"Total SUCCESS Rows: {len(data)}")
    print(f"1. Internet Archive Library Page Leaks: {len(categories['ia_leak'])} ({len(categories['ia_leak'])/len(data)*100:.1f}%)")
    print(f"2. Parked / Expired / Domain For Sale: {len(categories['parked'])} ({len(categories['parked'])/len(data)*100:.1f}%)")
    print(f"3. Placeholders (Coming soon/Under construction): {len(categories['placeholder'])} ({len(categories['placeholder'])/len(data)*100:.1f}%)")
    print(f"4. Plausible Real Business Content: {len(categories['real'])} ({len(categories['real'])/len(data)*100:.1f}%)")
    print(f"============================================================\n")
    
    if categories["ia_leak"]:
        print(f"--- 1. INTERNET ARCHIVE LIBRARY PAGE LEAKS ({len(categories['ia_leak'])} rows) ---")
        for x in categories["ia_leak"]:
            print(f"Row {x['row']} | Domain: {x['domain']} | Method: {x['method']} | Len: {x['length']}")
            print(f"  URL: {x['final_link']}")
            print(f"  Sample: {x['raw_data'][:300].strip().replace(chr(10), ' ')}")
            print("-" * 60)
        print("\n")
        
    if categories["parked"]:
        print(f"--- 2. PARKED / EXPIRED / FOR SALE PAGES ({len(categories['parked'])} rows) ---")
        for x in categories["parked"]:
            print(f"Row {x['row']} | Domain: {x['domain']} | Method: {x['method']} | Len: {x['length']}")
            print(f"  URL: {x['final_link']}")
            print(f"  Sample: {x['raw_data'][:300].strip().replace(chr(10), ' ')}")
            print("-" * 60)
        print("\n")
        
    if categories["placeholder"]:
        print(f"--- 3. PLACEHOLDERS ({len(categories['placeholder'])} rows) ---")
        for x in categories["placeholder"]:
            print(f"Row {x['row']} | Domain: {x['domain']} | Method: {x['method']} | Len: {x['length']}")
            print(f"  URL: {x['final_link']}")
            print(f"  Sample: {x['raw_data'][:300].strip().replace(chr(10), ' ')}")
            print("-" * 60)
        print("\n")
        
    if categories["real"]:
        print(f"--- 4. PLAUSIBLE REAL BUSINESS CONTENT ({len(categories['real'])} rows) ---")
        for x in categories["real"]:
            print(f"Row {x['row']} | Domain: {x['domain']} | Method: {x['method']} | Len: {x['length']}")
            print(f"  URL: {x['final_link']}")
            print(f"  Sample: {x['raw_data'][:300].strip().replace(chr(10), ' ')}")
            print("-" * 60)
        print("\n")

if __name__ == "__main__":
    analyze_quality()
