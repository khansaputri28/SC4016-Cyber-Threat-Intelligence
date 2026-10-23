import csv
import json
import time
from datetime import datetime, timezone
 
import requests
 
BASE_URL = "http://hptqq2o2qjva7lcaaq67w36jihzivkaitkexorauw7b2yul2z6zozpqd.onion"
API = BASE_URL + "/api"
 
PROXIES = {
    "http": "socks5h://127.0.0.1:9050",
    "https": "socks5h://127.0.0.1:9050",
}
 
START_DATE = datetime(2026, 1, 1, tzinfo=timezone.utc)
END_DATE = datetime(2026, 9, 30, 23, 59, 59, tzinfo=timezone.utc)
 
FETCH_DETAILS = True        
DETAIL_DELAY = 2           
OUTPUT_CSV = "chaos_victims.csv"
 
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; rv:115.0) Gecko/20100101 Firefox/115.0",
    "Accept": "application/json, text/plain, */*",
    "Content-Type": "application/json",
    "Origin": BASE_URL,
    "Referer": BASE_URL + "/",
}
 
EXCLUDE_KEYS = {"links", "linksHided", "sampleLink"}
DATE_HINTS = ("date", "time", "created", "publish", "added", "updated", "ts")
 
 
def api_post(session, path, data=None):
    """POST to the site's API with retries; unwraps a {"data": {...}} wrapper if present."""
    for attempt in range(1, 4):
        try:
            r = session.post(API + path, json=data or {}, timeout=90)
            if r.status_code == 200:
                j = r.json()
                if isinstance(j, dict) and isinstance(j.get("data"), (dict, list)) \
                        and "items" not in j and "title" not in j:
                    j = j["data"]
                return j
            print(f"  [!] HTTP {r.status_code} on {path} (attempt {attempt}): {r.text[:200]}")
        except (requests.RequestException, ValueError) as e:
            print(f"  [!] Error on {path} (attempt {attempt}): {e}")
        time.sleep(3 * attempt)
    return None
 
 
def to_dt(v):
    """Parse unix seconds/ms or common date strings into an aware datetime."""
    if v is None or v == "" or isinstance(v, bool):
        return None
    if isinstance(v, str) and v.strip().isdigit():
        v = int(v.strip())
    if isinstance(v, (int, float)):
        if v > 1e12:
            v = v / 1000
        if 1e9 < v < 2e10:
            return datetime.fromtimestamp(v, tz=timezone.utc)
        return None
    if isinstance(v, str):
        s = v.strip().replace("Z", "+00:00")
        try:
            dt = datetime.fromisoformat(s)
            return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)
        except ValueError:
            pass
        for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d", "%d.%m.%Y", "%d/%m/%Y", "%b %d, %Y"):
            try:
                return datetime.strptime(s, fmt).replace(tzinfo=timezone.utc)
            except ValueError:
                continue
    return None
 
 
def find_date(record):
    """Return (key, datetime) of the first date-like field (ignores countdown fields h/h2)."""
    for k, v in record.items():
        if k in ("h", "h2"):
            continue
        if any(hint in k.lower() for hint in DATE_HINTS):
            dt = to_dt(v)
            if dt:
                return k, dt
    return "", None
 
 
def main():
    s = requests.Session()
    s.proxies.update(PROXIES)
    s.headers.update(HEADERS)
 
    print("[+] Requesting victim list: POST /api/post/list")
    data = api_post(s, "/post/list")
    if data is None:
        print("[-] Could not fetch list. Check Tor (curl test) and that the site is up.")
        return
 
    with open("chaos_list_raw.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
 
    items = data.get("items", []) if isinstance(data, dict) else data
    print(f"  [✓] {len(items)} items returned (saved raw to chaos_list_raw.json)")
    if not items:
        print("  [!] Empty list - open chaos_list_raw.json to see what came back.")
        return
    print("  [i] Keys in list items:", sorted({k for it in items for k in it}))
 
    details = {}
    if FETCH_DETAILS:
        for i, it in enumerate(items, 1):
            h = it.get("hash")
            if not h:
                continue
            print(f"  [+] Detail {i}/{len(items)}: {it.get('title', '')[:50]}")
            d = api_post(s, "/post/get", {"id": h})
            if isinstance(d, dict):
                details[h] = d
            time.sleep(DETAIL_DELAY)
        with open("chaos_details_raw.json", "w", encoding="utf-8") as f:
            json.dump(details, f, indent=2, ensure_ascii=False)
        if details:
            print("  [i] Keys in detail records:", sorted({k for d in details.values() for k in d}))
 
    rows, skipped, undated = [], 0, 0
    for it in items:
        merged = dict(it)
        for k, v in details.get(it.get("hash"), {}).items():
            merged.setdefault(k, v)
 
        date_key, dt = find_date(merged)
        deadline = to_dt(merged.get("h")) or to_dt(merged.get("h2"))
 
        if dt:
            if not (START_DATE <= dt <= END_DATE):
                skipped += 1
                continue
        else:
            undated += 1
 
        row = {
            "ransomware_group": "Chaos",
            "victim_name": merged.get("title", ""),
            "website": merged.get("url", ""),
            "description": (merged.get("text") or "").replace("\n", " ").strip(),
            "leaked_size_gb": merged.get("leakedSize", ""),
            "views": merged.get("views", ""),
            "status": "countdown (unpublished)" if merged.get("h") else "published",
            "date": dt.strftime("%Y-%m-%d") if dt else "",
            "date_source_field": date_key,
            "publish_deadline_utc": deadline.strftime("%Y-%m-%d %H:%M") if deadline else "",
            "post_url": f"{BASE_URL}/{merged.get('hash', '')}/{merged.get('link', '')}",
        }
        for k, v in merged.items():
            if k in EXCLUDE_KEYS or isinstance(v, (list, dict)):
                continue
            if k not in ("title", "url", "text", "leakedSize", "views", "hash", "link"):
                row.setdefault(f"raw_{k}", v)
        rows.append(row)
 
    fieldnames = []
    for r in rows:
        for k in r:
            if k not in fieldnames:
                fieldnames.append(k)
    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)
 
    print(f"\n[★] {len(rows)} records saved to {OUTPUT_CSV}")
    print(f"    {skipped} outside {START_DATE.date()}..{END_DATE.date()} were excluded")
    if undated:
        print(f"    {undated} records had NO date field and were kept - check chaos_*_raw.json")
 
 
if __name__ == "__main__":
    main()
