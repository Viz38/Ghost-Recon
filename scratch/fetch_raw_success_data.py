import sys
import os
import asyncio
import json

# Add project root and Integrated directories to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "Integrated"))

from services.google_sheet import GoogleSheetClient

async def main():
    p1_id = "1WvqHhXQcFSOuGnDW87J2Elv29uMEMAWiTknB4BWzlD4"
    p2_id = "15XDN7Jxh-o2KezhnqHnnSlWYILvRTW4HO0nki3RgWVA"
    
    print("Initializing GoogleSheetClient...")
    client = GoogleSheetClient(credentials_path="credentials.json")
    
    for sheet_id, name in [(p1_id, "Phase 1"), (p2_id, "Phase 2")]:
        print(f"\nFetching FULL raw data from {name} Sheet ({sheet_id})...")
        rows = await client.get_all_rows(sheet_id, "Console")
        if not rows:
            print(f"No rows returned for {name} sheet.")
            continue
        
        print(f"Total rows fetched: {len(rows)}")
        success_rows = []
        for idx, r in enumerate(rows[1:], start=2): # skip header
            if len(r) > 1:
                status = r[1].strip()
                if "SUCCESS" in status.upper():
                    domain = r[0] if len(r) > 0 else f"Row {idx}"
                    method = r[2] if len(r) > 2 else "N/A"
                    data = r[3] if len(r) > 3 else ""
                    total_hits = r[4] if len(r) > 4 else "N/A"
                    latest_ts = r[5] if len(r) > 5 else "N/A"
                    oldest_ts = r[6] if len(r) > 6 else "N/A"
                    length = r[7] if len(r) > 7 else len(data)
                    final_link = r[8] if len(r) > 8 else "N/A"
                    
                    success_rows.append({
                        "row": idx,
                        "domain": domain,
                        "status": status,
                        "method": method,
                        "length": length,
                        "raw_data": data,  # Full raw data, no truncation!
                        "total_hits": total_hits,
                        "latest_ts": latest_ts,
                        "oldest_ts": oldest_ts,
                        "final_link": final_link
                    })
        
        print(f"Found {len(success_rows)} SUCCESS rows.")
        
        # Save to scratch folder for analysis
        output_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), f"success_data_raw_{name.lower().replace(' ', '_')}.json")
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(success_rows, f, indent=2, ensure_ascii=False)
        print(f"Saved FULL raw SUCCESS rows to {output_file}")

if __name__ == "__main__":
    asyncio.run(main())
