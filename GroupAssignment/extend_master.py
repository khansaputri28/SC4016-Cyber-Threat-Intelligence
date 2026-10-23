"""
Add DLS #4 (DireWolf) and #5 (SETTRA) to the existing master.csv / master_datatypes.csv,
and rebuild the pending/countdown sheet (Chaos + SETTRA posts not yet published).

Inputs: master.csv (existing Play/Anubis/Chaos, built by build_master.py),
        direwolf.csv, SETTRA_victims.csv (SETTRA, hand-enriched replacement for leaksite_victims.csv),
        Chaos_Ransomware_Victims.xlsx ("Pending (Obfuscated)" sheet, for chaos countdown
        -- doesn't need chaos_dates.txt, that's only for published-Chaos post dates).
Outputs: master.csv (overwritten, now 5 groups), master_datatypes.csv (overwritten),
         pending_countdown.csv (Chaos + SETTRA posts still on countdown).
Run to_excel.py after this to rebuild DLS_master.xlsx.
"""
import re
import pandas as pd

COLUMNS = ["group", "victim_name", "domain", "post_date", "country", "industry",
           "revenue_band", "employee_band", "data_types_claimed", "data_size_gb",
           "status", "description", "recycled_flag", "source_url", "extra_notes"]
DATE_FROM, DATE_TO = pd.Timestamp("2026-01-01"), pd.Timestamp("2026-09-30")

COUNTRY_FIX = {"USA": "United States", "UK": "United Kingdom", "Unknown": "Unknown",
               "United States of America": "United States", "Turkiye": "Turkey",
               "Not confidently verified in sources reviewed": "Unknown"}


def clean_domain(s):
    if not isinstance(s, str) or not s.strip():
        return ""
    s = re.sub(r"^https?://", "", s.strip().lower())
    s = re.sub(r"^www\.", "", s)
    return s.split("/")[0]


TAG_RULES = [
    ("Medical/PHI", r"medical|patient|health|diagnos|treatment|medication|medicare|medicaid|insurance id|protected health"),
    ("PII", r"social security|ssn|date[s]? of birth|\bdob\b|passport|driver|personal (data|information|identification)|personal identifiers|names, |\bids?\b|military id|identification"),
    ("Financial", r"financ|bank|payment|card|accounting|tax|budget|payroll|invoice"),
    ("Employee/HR", r"employee|staff|hr\b|payroll"),
    ("Client/Customer", r"client|customer|patient data"),
    ("Legal", r"legal|estate records|law"),
    ("IP/Engineering", r"intellectual property|patent|drawing|engineering material|project|aerospace|military-related|tender|insider|source code|critical-infrastructure|safety plan"),
    ("Credentials", r"credential|password"),
    ("Contracts", r"\bcontracts?\b"),
]


def tag_data_types(text):
    t = (text or "").lower()
    tags = [name for name, pat in TAG_RULES if re.search(pat, t)]
    return ";".join(tags) if tags else "Unspecified"


def parse_size_gb(s):
    if not isinstance(s, str) or not s.strip():
        return None
    m = re.search(r"([\d.,]+)\s*(TB|GB)", s, re.I)
    if not m:
        return None
    num = m.group(1)
    num = num.replace(",", ".") if num.count(",") == 1 and "." not in num and len(num.split(",")[1]) != 3 else num.replace(",", "")
    val = float(num)
    return val * 1000 if m.group(2).upper() == "TB" else val


# ---------------- DIREWOLF (DLS #4) ----------------
DIREWOLF_INDUSTRY = {
    "Manufacturing": "Manufacturing", "Business Services": "Professional & Business Services",
    "Hospitals & Physicians Clinics": "Healthcare & Pharma", "Financial Software": "Technology & Telecom",
    "Healthcare": "Healthcare & Pharma", "Software": "Technology & Telecom",
    "Media": "Media, Publishing & Advertising", "Finance": "Financial Services & Insurance",
    "Logistics Services": "Transportation & Logistics", "Civil Engineering Construction": "Construction & Engineering",
    "Electronics": "Manufacturing", "Energy, Utilities & Waste": "Energy & Resources",
    "Architecture, Engineering & Design": "Construction & Engineering", "Healthcare Services": "Healthcare & Pharma",
    "Automotive Parts": "Automotive", "Food & Beverage": "Food & Beverage",
    "Data Collection & Internet Portals": "Technology & Telecom", "FinTech": "Financial Services & Insurance",
    "Retail Technology & SaaS": "Technology & Telecom", "Law Firms & Legal Services": "Legal Services",
    "HOA Management": "Real Estate", "Multimedia, Games": "Media, Publishing & Advertising",
    "Games": "Media, Publishing & Advertising", "Colleges, Universities": "Education",
    "Software Provider": "Technology & Telecom", "Engineering Software": "Technology & Telecom",
    "Insurance": "Financial Services & Insurance", "Corporate Wellness Services": "Professional & Business Services",
    "Freight & Logistics Services": "Transportation & Logistics",
}

dw = pd.read_csv("direwolf.csv")
dw_date = pd.to_datetime(dw["published_date_raw"].str.extract(r"Published:\s*(\d{4}-\d{2}-\d{2})")[0])
w = pd.DataFrame({
    "group": "DireWolf",
    "victim_name": dw["company name"].str.strip(),
    "domain": dw["company website"].map(clean_domain),
    "post_date": dw_date,
    "country": dw["country"].replace(COUNTRY_FIX),
    "industry": dw["industry"].str.strip().map(DIREWOLF_INDUSTRY).fillna("Unknown"),
    "revenue_band": "", "employee_band": "",
    "data_types_claimed": dw["leaked_data_types"].fillna("").map(tag_data_types),
    "data_size_gb": dw["file_size"].map(parse_size_gb),
    "status": "published",
    "description": dw["critical_data_summary"].fillna(dw["business description"]).fillna(""),
    "source_url": dw["url"],
})
w["extra_notes"] = ("raw industry: " + dw["industry"].fillna("Unknown")
                     + "; document_count " + dw["document_count"].fillna("").astype(str)
                     + "; http_status " + dw["http_status"].astype(str))

# ---------------- SETTRA (DLS #5) ----------------
# SETTRA_victims.csv is a hand-enriched replacement for the earlier leaksite_victims.csv scrape:
# same 76 victims/domains, but with real company names, industry, revenue/employee bands,
# itemized data_types_claimed and a description already filled in -- use directly, no inference.
SETTRA_INDUSTRY = {
    "Manufacturing": "Manufacturing", "Food & Beverage": "Food & Beverage",
    "Defense & Aerospace": "Defense & Aerospace", "Financial Services": "Financial Services & Insurance",
    "Retail & Wholesale": "Retail & Wholesale", "Marketing & Media": "Media, Publishing & Advertising",
    "Healthcare": "Healthcare & Pharma", "Technology & IT": "Technology & Telecom",
    "Automotive": "Automotive", "Construction & Real Estate": "Construction & Real Estate",
    "Transportation & Logistics": "Transportation & Logistics", "Hospitality & Entertainment": "Hospitality & Leisure",
    "Business Services": "Professional & Business Services", "Legal Services": "Legal Services",
    "Energy & Utilities": "Energy & Resources", "Mining & Resources": "Energy & Resources",
    "Telecommunications": "Technology & Telecom",
}

st = pd.read_csv("SETTRA_victims.csv")
st["post_date"] = pd.to_datetime(st["post_date"])
pub = st[st["status"] == "PUBLISHED"].copy()
s = pd.DataFrame({
    "group": "SETTRA",
    "victim_name": pub["victim_name"].str.strip(),
    "domain": pub["domain"].map(clean_domain),
    "post_date": pub["post_date"],
    "country": pub["country"].fillna("Unknown").replace(COUNTRY_FIX),
    "industry": pub["industry"].map(SETTRA_INDUSTRY).fillna("Unknown"),
    "revenue_band": pub["revenue_band"],
    "employee_band": pub["employee_band"].fillna(""),
    "data_types_claimed": pub["data_types_claimed"],
    "data_size_gb": pub["data_size_db"].map(parse_size_gb),
    "status": "published",
    "description": pub["description"],
    "source_url": "",
})
s["extra_notes"] = "raw industry: " + pub["industry"]

# ---------------- MERGE INTO EXISTING MASTER ----------------
BASE_GROUPS = ["Play", "Anubis", "Chaos"]
existing = pd.read_csv("master.csv", parse_dates=["post_date"], keep_default_na=False, na_values=[])
existing = existing[existing["group"].isin(BASE_GROUPS)].copy()  # idempotent: ignore any DLS#4/#5 rows from a prior run
existing["data_size_gb"] = pd.to_numeric(existing["data_size_gb"], errors="coerce")
existing = existing.drop(columns=["recycled_flag"])

new_rows = pd.concat([w, s], ignore_index=True)
for col in COLUMNS:
    if col not in new_rows:
        new_rows[col] = ""

dropped = new_rows[~new_rows["post_date"].between(DATE_FROM, DATE_TO)]
new_rows = new_rows[new_rows["post_date"].between(DATE_FROM, DATE_TO)].copy()

allrows = pd.concat([existing, new_rows], ignore_index=True)

# recompute recycled / repost flags over the full 5-group set
allrows["recycled_flag"] = ""
allrows.loc[allrows["victim_name"].str.contains(r"part 2|part ii", case=False), "recycled_flag"] = "repost (part 2)"
dom = allrows[allrows["domain"] != ""]
multi = dom.groupby("domain")["group"].nunique()
for d in multi[multi > 1].index:
    allrows.loc[allrows["domain"] == d, "recycled_flag"] = "claimed by multiple groups"
dup_same = dom[dom.duplicated(["group", "domain"], keep=False)]
allrows.loc[dup_same.index, "recycled_flag"] = "listed twice by same group"

allrows["post_date"] = allrows["post_date"].dt.strftime("%Y-%m-%d")
master = allrows.sort_values(["group", "post_date"])[COLUMNS]
master.to_csv("master.csv", index=False, encoding="utf-8")

for g, df in master.groupby("group"):
    df.to_csv(f"{g.lower()}_schema.csv", index=False, encoding="utf-8")

print("kept per group:\n", master["group"].value_counts())
print("\ndropped (new-group rows outside Jan-Sep 2026):\n", dropped.groupby("group").size() if len(dropped) else "none")
print("\nrecycled flags:\n", master[master.recycled_flag != ""][["group", "victim_name", "domain", "recycled_flag"]])

# long table for Q8: one row per (victim, data type)
dt = master[["group", "victim_name", "industry", "data_types_claimed"]].copy()
dt["data_type"] = dt["data_types_claimed"].str.split(r";\s*")
dt = dt.explode("data_type").drop(columns="data_types_claimed")
dt.to_csv("master_datatypes.csv", index=False, encoding="utf-8")
print("\ndatatype rows:", len(dt))

# ---------------- PENDING / COUNTDOWN (Chaos + SETTRA) ----------------
ch_pend = pd.read_excel("Chaos_Ransomware_Victims.xlsx", "Pending (Obfuscated)")
ch_pend = ch_pend[ch_pend["Status at Snapshot"] == "Pending"]
cp = pd.DataFrame({
    "group": "Chaos", "victim_name": "Undisclosed (countdown)",
    "data_size_gb": ch_pend["Claimed Size (GB)"].replace(0, None),
    "publish_deadline": pd.to_datetime(ch_pend["Publish Deadline (UTC)"]).dt.date,
    "source_url": ch_pend["Leak Post URL"],
})

settra_cd = st[st["status"] == "COUNTDOWN"].copy()
sp = pd.DataFrame({
    "group": "SETTRA", "victim_name": settra_cd["victim_name"],
    "data_size_gb": settra_cd["data_size_db"].map(parse_size_gb),
    "publish_deadline": settra_cd["post_date"].dt.date,
    "source_url": "",
})

pending = pd.concat([cp, sp], ignore_index=True)
pending.to_csv("pending_countdown.csv", index=False, encoding="utf-8")
print("\npending/countdown posts saved:", len(pending), "(Chaos", len(cp), "+ SETTRA", len(sp), ")")
