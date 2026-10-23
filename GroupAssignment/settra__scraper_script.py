#!/usr/bin/env python3

#-------------------------------------------------------------------------------------#
# Initial methodology:
# My first attempt at Settra used an automated script that requested the site over Tor, as I did for the other leak sites.
# However, this method failed as the site was protected by a bot check as I was unable to obtain any useful data from the site.

# Solution:
# Therefore, I decided to use a different approach my manually accessing the Sterra [.]onion site over Tor Browser.
# This allow me to pass the check as a normal user & from there, I navigated to the Data Leaks page.
# After entering the page, below are the steps I took to extract the [.]js file from the page: 

# Step 1: Open the browser's developer tools (F12) and navigate to the Network tab.
# Step 2: Ensure that the "Disable cache" option is checked.
        # (Note: This is important as it ensures that the browser will download the latest version
        #  of the page and its resources, rather than using cached versions.)
# Step 3: Refresh the page to capture the network requests.
# Step 4: In the list of network requests, add a "js" filter.
# Step 5: Right click the [.]js file and click "Save Response As..." to save the file to your local machine.
        # (The file size should be of about 4 MB as it is the first clue that it contained the site's content and not just interface code)
        # (You may also want to check the file's content to ensure that it contains the expected data, such as the breach articles in Markdown format.)

# Inspection Process:
# 2 things were observed in the [.js] file:
    # 1. Application code:
        #  Strings such as the React Router warning ("Please change the parent <Route path=...>") shows that the site is a React single-page application.
        #  The page HTML is mostly an empty shell, and the browser builds the victim cards at load time from data inside the bundle.
        #  A conventional scraper that downloads the HTML and parses it would find almost no victim data.
    # 2. Victim data:
        # The same file contained the breach articles in Markdown,
        # such as the "PROLOGUE" section and the company description visible along with the structured post fields.
# These factors thus made it clear why earlier attempts to scrape the site failed as data was not in the HTML but in a [.]js file.

# Parse Methodology:
# Step 1: The [.js] file contains 2 main blocks of data:
        # 1. The `posts` block:
            # This block contains a list of posts, each with a unique identifier (uid) &
            # various fields such as site, content, publishedAt, revenue, cap, and timerDeadline.
        # 2. The `details` block:
            # This block contains a mapping of uid to additional details for each post, such as site, content, revenue, and cap.
# Step 2: Merging, posts & details are matched by uid. Posts are the primary source of data, while details provide additional information.
# Step 3: The rest of the script is then derived by pattern matching based on the column names we require in the final CSV output.

#-------------------------------------------------------------------------------------#

import argparse, csv, html, json, re
from datetime import datetime, timezone
from pathlib import Path

COLUMNS = ["victim_name", "domain", "post_date", "country", "industry", "revenue_band",
           "employee_band", "data_types_claimed", "data_size_db", "status", "description"]

# JS parsing
TPL = r"`((?:\\.|[^`\\])*)`"          # a complete JS template literal (backticks)

def js_unescape(s):
    
    # Decode escapes inside a JS template literal.
    simple = {"n": "\n", "t": "\t", "r": "\r", "b": "\b", "f": "\f", "v": "\v", "0": "\0"}
    def rep(m):
        c = m.group(1)
        if c in simple: return simple[c]
        if c == "\n": return ""
        if c.startswith("u{"): return chr(int(c[2:-1], 16))
        if c[0] == "u" and len(c) == 5: return chr(int(c[1:], 16))
        if c[0] == "x" and len(c) == 3: return chr(int(c[1:], 16))
        return c                       # \\ \` \$ \" \' -> the char itself
    return re.sub(r"\\(u\{[0-9a-fA-F]+\}|u[0-9a-fA-F]{4}|x[0-9a-fA-F]{2}|\n|.)", rep, s, flags=re.S)

def parse_posts_block(text):

    # Return list of dicts from the `posts:[{uid:`..`,...},...]` JS literal.
    start = text.find("posts:[{uid:`")
    if start == -1:
        return []
    end = text.find("details:JSON.parse(`", start)
    block = text[start: end if end != -1 else len(text)]
    starts = [m.start() for m in re.finditer(r"\{uid:`", block)]
    out = []
    for a, b in zip(starts, starts[1:] + [len(block)]):
        chunk = block[a:b]
        rec = {}
        for key, val in re.findall(r"(?:^\{|,)(\w+):" + TPL, chunk, flags=re.S):
            rec[key] = js_unescape(val)
        for key, val in re.findall(r"(?:^\{|,)(\w+):(-?\d+(?:\.\d+)?)(?=[,}])",
                                   re.sub(TPL, "``", chunk, flags=re.S)):
            rec[key] = val
        if rec.get("uid"):
            out.append(rec)
    return out

def parse_details_block(text):

    # Return {uid: dict} from `details:JSON.parse(`...`)`.
    m = re.search(r"details:JSON\.parse\(" + TPL + r"\)", text, flags=re.S)
    if not m:
        return {}
    try:
        return json.loads(js_unescape(m.group(1)), strict=False)
    except json.JSONDecodeError:
        return {}

# Helpers
def clean_domain(site):
    s = re.sub(r"^https?://", "", (site or "").strip().lower()).split("/")[0]
    return re.sub(r"^www\.", "", s)

def to_dt(s):
    try:
        return datetime.fromisoformat(s.replace("Z", "+00:00")) if s else None
    except ValueError:
        return None

def money(s):
    try: return float(re.sub(r"[^\d.]", "", s or ""))
    except ValueError: return None

def revenue_band(s):
    v = money(s)
    if v is None: return ""
    for limit, label in [(10e6, "<$10M"), (50e6, "$10M-$50M"), (250e6, "$50M-$250M"),
                         (1e9, "$250M-$1B")]:
        if v < limit: return label
    return ">$1B"

def employee_band(n):
    for limit, label in [(10, "1-10"), (50, "11-50"), (200, "51-200"), (500, "201-500"),
                         (1000, "501-1000"), (5000, "1001-5000")]:
        if n <= limit: return label
    return "5000+"

def md_to_text(md):
    t = html.unescape(md)
    t = re.sub(r"```.*?```", " ", t, flags=re.S)
    t = re.sub(r"!\[[^\]]*\]\([^)]*\)", " ", t)
    t = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", t)
    return t

def squash(s):
    return re.sub(r"\s+", " ", re.sub(r"[#*_`>|]+", " ", s)).strip()

# Victim name
LEAD_NOISE = re.compile(r"^(documents?|internal documents?( of)?|investigation|exposure of massive "
                        r"data breach|the complete digital archive of|how|the)\s*[:\-]?\s*", re.I)

def domain_name(domain):
    base = domain.split(".")[0]
    return base.replace("-", " ").title()

def victim_name(content, domain):
    
    # Best-effort legal/brand name from the article headline, else the domain.
    title = ""
    for line in html.unescape(content or "").splitlines():
        line = line.strip()
        if line.startswith("#"):
            title = line.lstrip("#").strip(); break
    title = re.sub(r"[*_`]", "", title)
    dom_key = re.sub(r"[^a-z0-9]", "", domain.split(".")[0])
    cands = []
    m = re.match(r"^Documents?:?\s+(.+?)(?:\s+[\u2014-]\s+Complete.*)?$", title, re.I)
    if m: cands.append(m.group(1))
    m = re.match(r"^EXPOSURE OF MASSIVE DATA BREACH:\s*(.+)$", title, re.I)
    if m: cands.append(m.group(1))
    m = re.match(r"^(.+?):\s", title + " ")
    if m: cands.append(m.group(1))
    m = re.match(r"^(.+?)\s+(?:Documents|Archives?)$", title, re.I)
    if m: cands.append(m.group(1))
    m = re.match(r"^(?:Internal Documents of )(.+)$", title, re.I)
    if m: cands.append(m.group(1))
    # bold "The company is called **X**" / "Investigation: X"
    m = re.search(r"Investigation:\s*(.+)$", title)
    if m: cands.append(m.group(1))
    for c in cands:
        c = squash(c).strip(" .:-")
        words = len(c.split())
        if c and words <= 8 and len(c) <= 70 and not re.search(r"\b(how|what|why|archive of|inside)\b", c, re.I):
            return c
    for c in cands:        # any candidate whose letters overlap the domain
        k = re.sub(r"[^a-z0-9]", "", c.lower())
        if dom_key and dom_key[:5] in k:
            return squash(c)
    return domain_name(domain)

# Country
CCTLD = {"uk": "United Kingdom", "nl": "Netherlands", "mx": "Mexico", "at": "Austria",
         "au": "Australia", "jp": "Japan", "ec": "Ecuador", "de": "Germany", "pt": "Portugal",
         "us": "United States", "ca": "Canada", "fr": "France", "es": "Spain", "it": "Italy",
         "ch": "Switzerland", "be": "Belgium", "se": "Sweden", "no": "Norway", "dk": "Denmark",
         "fi": "Finland", "ie": "Ireland", "pl": "Poland", "br": "Brazil", "ar": "Argentina",
         "cl": "Chile", "co": "Colombia", "in": "India", "sg": "Singapore", "my": "Malaysia",
         "hk": "Hong Kong", "nz": "New Zealand", "za": "South Africa", "kr": "South Korea",
         "tw": "Taiwan", "cn": "China", "tr": "Turkey", "la": "Laos"}

COUNTRY_TERMS = {
    "United States": ["united states", "u.s.", "american", "usa", "america", "federal", "irs", "ssn"],
    "United Kingdom": ["united kingdom", "british", "england", "scotland", "wales", "london", "leeds", "companies house", "hmrc"],
    "Canada": ["canada", "canadian", "ontario", "quebec", "alberta", "british columbia"],
    "Germany": ["germany", "german", "deutsche"], "France": ["france", "french", "paris"],
    "Netherlands": ["netherlands", "dutch"], "Austria": ["austria", "austrian"],
    "Australia": ["australia", "australian", "new south wales", "victoria, australia", "sydney", "melbourne"],
    "Mexico": ["mexico", "mexican"], "Ecuador": ["ecuador", "ecuadorian"],
    "Japan": ["japan", "japanese", "tokyo"], "Portugal": ["portugal", "portuguese"],
    "Spain": ["spain", "spanish"], "Italy": ["italy", "italian"], "Belgium": ["belgium", "belgian"],
    "Hong Kong": ["hong kong"], "Laos": ["laos", "lao pdr"], "China": ["china", "chinese"],
    "India": ["india", "indian"], "Denmark": ["denmark", "danish"], "Sweden": ["sweden", "swedish"],
    "Switzerland": ["switzerland", "swiss"], "South Africa": ["south africa"],
    "Singapore": ["singapore"], "Brazil": ["brazil", "brazilian"], "Argentina": ["argentina"],
}
US_STATES = ("Alabama Alaska Arizona Arkansas California Colorado Connecticut Delaware Florida Georgia "
             "Hawaii Idaho Illinois Indiana Iowa Kansas Kentucky Louisiana Maine Maryland Massachusetts "
             "Michigan Minnesota Mississippi Missouri Montana Nebraska Nevada Ohio Oklahoma Oregon "
             "Pennsylvania Tennessee Texas Utah Vermont Virginia Wisconsin Wyoming "
             "New York|New Jersey|New Mexico|New Hampshire|North Carolina|South Carolina|North Dakota|"
             "South Dakota|West Virginia|Rhode Island|Washington State").replace("|", " ").split(" ")
US_STATE_RE = re.compile(r"\b(?:Alabama|Alaska|Arizona|Arkansas|California|Colorado|Connecticut|Delaware|"
    r"Florida|Georgia|Hawaii|Idaho|Illinois|Indiana|Iowa|Kansas|Kentucky|Louisiana|Maine|Maryland|"
    r"Massachusetts|Michigan|Minnesota|Mississippi|Missouri|Montana|Nebraska|Nevada|Ohio|Oklahoma|Oregon|"
    r"Pennsylvania|Tennessee|Texas|Utah|Vermont|Wisconsin|Wyoming|New York|New Jersey|New Hampshire|"
    r"North Carolina|South Carolina|West Virginia|Rhode Island|NYC)\b")

def country(domain, text):
    tld = domain.rsplit(".", 1)[-1]
    head = text[:3500].lower()
    scores = {}
    for c, terms in COUNTRY_TERMS.items():
        n = sum(len(re.findall(r"(?<![a-z])" + re.escape(t) + r"(?![a-z])", head)) for t in terms)
        if n: scores[c] = n
    n_states = len(US_STATE_RE.findall(text[:3500]))
    if n_states: scores["United States"] = scores.get("United States", 0) + n_states * 2
    if tld in CCTLD and tld not in ("co", "in", "it", "no", "la", "be", "at", "ch", "my", "se"):
        return CCTLD[tld]
    if tld in CCTLD and (tld not in ("co", "in")):       # ambiguous words, but still a ccTLD here
        if domain.endswith((".at", ".be", ".ch", ".it", ".no", ".se", ".my", ".la")):
            return CCTLD[tld]
    if scores:
        return max(scores, key=scores.get)
    return ""

# Industry
INDUSTRY = [
 ("Legal Services", r"law firm|attorney|law llp|\blaw\b|solicitor|legal practice|p\.a\.\b"),
 ("Financial Services", r"cash advance|lender|lending|bank|insurance|broker|financing|mortgage|tax (?:consult|return)|accounting|investment|portfolio|registrar|credit agreement|fund(?:ing)?\b"),
 ("Healthcare", r"hospital|clinic|patient|medical|pharma|doctors|health system"),
 ("Construction & Real Estate", r"construction|builds homes|homebuilder|real estate|realty|lumber|demolition|housing|landscap|contractor|building materials"),
 ("Manufacturing", r"manufactur|steel|polymers|pumps|valves|foundry|factory|fabricat|glass|dye|chemical|components|luminaires|equipment|machinery|safes?\b|tresor"),
 ("Transportation & Logistics", r"freight|truck|logistics|shipping|auto shippers|carrier|fleet|vehicle|transport"),
 ("Automotive", r"auto group|dealership|automotive|car dealer"),
 ("Food & Beverage", r"poultry|beverage|beer|grain|food|restaurant|dining|farm|agricultur|brewery|distributor of"),
 ("Retail & Wholesale", r"retail|stores|wholesale|collectables|jewel|supermarket"),
 ("Technology & IT", r"software|\bit company|information technology|saas|cloud|data cent|cyber|telematics|systems, inc"),
 ("Telecommunications", r"telecom|cell towers|wireless|carrier network"),
 ("Energy & Utilities", r"hydropower|oil and gas|oilfield|production solutions|energy|electric utility|well\b"),
 ("Mining & Resources", r"diamond|mining|mine\b|mineral"),
 ("Hospitality & Entertainment", r"hotel|resort|venue|entertainment|arena|ski\b|hospitality|stadium|club members"),
 ("Marketing & Media", r"marketing|public relations|\bpr agency|advertis|photograph|portrait|media"),
 ("Business Services", r"cleaning|janitorial|staffing|consult|facility services|outsourc|clearinghouse"),
 ("Defense & Aerospace", r"defen[cs]e|military|aerospace|semiconductor|boeing"),
]

def industry(domain, text):
    head = (domain + " " + text[:2500]).lower()
    best, best_n = "", 0
    for name, pat in INDUSTRY:
        n = len(re.findall(pat, head))
        if n > best_n: best, best_n = name, n
    return best

# Data types
DATA_TYPES = [
 ("Financial records", r"bank (?:account|statement|detail)|invoice|payroll|tax return|general ledger|bookkeeping|accounting|financial (?:statement|record|document)|balance sheet|wire|credit card"),
 ("Employee/HR data", r"employee|salar(?:y|ies)|\bhr\b|human resources|direct-deposit|personnel|workers' compensation|performance review|severance"),
 ("PII (SSN/ID/passport)", r"\bssn\b|social security|passport|driver'?s licen[cs]e|birth certificate|national id|\bdni\b|\bcurp\b|date of birth|home address"),
 ("Customer/client data", r"customer (?:list|data|database|record)|client (?:data|file|list|record)|patient|policyholder"),
 ("Contracts & legal", r"contract|agreement|nda\b|lawsuit|litigation|court|legal (?:document|file)|settlement"),
 ("Emails", r"\be-?mails?\b|mailbox|\.pst\b|correspondence"),
 ("Credentials", r"password|credential|login|vpn|api key|token"),
 ("Technical/IP/engineering", r"drawing|blueprint|specification|trade secret|source code|cad\b|engineering|schematic|patent|network diagram|infrastructure"),
 ("Insurance records", r"insurance polic|claim file|auto-insurance|insurance claim"),
 ("Medical/health data", r"medical record|health record|diagnos|prescription|medical"),
]

def data_types(text):
    low = text.lower()
    found = [(len(re.findall(p, low)), n) for n, p in DATA_TYPES]
    return "; ".join(n for c, n in sorted(found, reverse=True) if c >= 2)

# ----------------------------------------------------------------- size & employees
def data_size(cap, text):
    cap = (cap or "").strip()
    if cap and not cap.upper().startswith("N/A"):
        return re.sub(r"\s+", "", cap)
    m = re.search(r"(\d[\d,.]*)\s?(gigabytes?|GB|terabytes?|TB)\b", text, re.I)
    if m:
        unit = "TB" if m.group(2).lower().startswith(("t",)) else "GB"
        return f"{m.group(1).replace(',', '')}{unit}"
    return ""

EMP_PATTERNS = [
    r"(?:employs|employing|workforce of|headcount of|team of|staff of)\s+(?:about |around |approximately |roughly |~)?([\d,]{1,7})\b",
    r"\b(?:approximately |about |around |roughly |~)?([\d,]{2,7})\s+(?:full-time\s+)?(?:employees|staff members|people on (?:the )?payroll)\b[^.]{0,40}(?:company|firm|business|group|in total|on the payroll)",
    r"\b(?:company|firm|group|business|it)\s+(?:has|with)\s+(?:about |around |approximately |roughly |~)?([\d,]{2,7})\s+employees",
    r"\bof\s+([\d,]{2,7})\s+employees on the payroll",
    r"\|\s*([\d,]{1,6})\s+employees\b",
]
def employees(text):
    for p in EMP_PATTERNS:
        m = re.search(p, text, re.I)
        if m:
            try:
                n = int(m.group(1).replace(",", ""))
            except ValueError:
                continue
            if 1 <= n <= 500000: return employee_band(n)
    return ""

# Description
def description(content, limit):
    if limit <= 0 or not content or content.startswith("[REDACTED"):
        return ""
    paras = re.split(r"\n\s*\n", html.unescape(content))
    for para in paras:
        p = para.strip()
        if not p or p.startswith(("#", "---", "|")) or re.match(r"^\*{0,2}[A-Za-z .,&-]+ \u00b7 ", p):
            continue
        p = squash(re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", p))
        if len(p) < 40: continue
        return p if len(p) <= limit else p[:limit].rsplit(" ", 1)[0] + "..."
    return ""

# Main
def main():
    ap = argparse.ArgumentParser(description="leak-site index.js -> CSV")
    ap.add_argument("input_file", nargs="?", default="index_redacted.js")
    ap.add_argument("-o", "--output", default="victims.csv")
    ap.add_argument("--start-date"); ap.add_argument("--end-date")
    ap.add_argument("--desc-len", type=int, default=250, help="max description chars (0 = blank)")
    args = ap.parse_args()

    text = Path(args.input_file).read_text(encoding="utf-8", errors="replace")
    posts = {p["uid"]: p for p in parse_posts_block(text)}
    details = parse_details_block(text)
    print(f"[i] posts block: {len(posts)} | details block: {len(details)}")
    if not posts and not details:
        raise SystemExit("[-] No post data found in this file.")

    start = datetime.strptime(args.start_date, "%Y-%m-%d").date() if args.start_date else None
    end = datetime.strptime(args.end_date, "%Y-%m-%d").date() if args.end_date else None
    now = datetime.now(timezone.utc)

    rows, seen = [], set()
    for uid in list(posts) + [u for u in details if u not in posts]:
        p, d = posts.get(uid, {}), details.get(uid, {})
        site = clean_domain(p.get("site") or d.get("site"))
        if not site or site in seen: continue
        seen.add(site)
        content = p.get("content") or ""
        if not content or content.startswith("[REDACTED"):
            c2 = d.get("content") or ""
            content = content or ("" if c2.startswith("[REDACTED") else c2)
        body = md_to_text(content)

        pub = to_dt(p.get("publishedAt")) or to_dt(p.get("createdAt")) or to_dt(d.get("timerDeadline"))
        post_date = pub.date() if pub else None
        if (start and (not post_date or post_date < start)) or (end and (not post_date or post_date > end)):
            continue
        deadline = to_dt(p.get("timerDeadline") or d.get("timerDeadline"))
        status = ("PUBLISHED" if deadline and deadline <= now else "COUNTDOWN") if deadline else ""

        rows.append({
            "victim_name": victim_name(content, site),
            "domain": site,
            "post_date": post_date.isoformat() if post_date else "",
            "country": country(site, body),
            "industry": industry(site, body),
            "revenue_band": revenue_band(p.get("revenue") or d.get("revenue")),
            "employee_band": employees(body),
            "data_types_claimed": data_types(body),
            "data_size_db": data_size(p.get("cap") or d.get("cap"), body),
            "status": status,
            "description": description(content, args.desc_len),
        })

    rows.sort(key=lambda r: r["post_date"], reverse=True)
    with open(args.output, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=COLUMNS)
        w.writeheader(); w.writerows(rows)

    print(f"[+] Wrote {len(rows)} rows to {args.output}")
    for col in COLUMNS[1:]:
        print(f"    {col:<20} filled: {sum(bool(r[col]) for r in rows)}/{len(rows)}")

if __name__ == "__main__":
    main()
