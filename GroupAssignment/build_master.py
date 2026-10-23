"""
Convert each group's raw scrape into the shared schema and merge into master.csv.
Inputs: play_raw.csv, anubis_raw.csv, chaos.xlsx, chaos_dates.txt (post dates from ransomware.live)
"""
import re
import pandas as pd

COLUMNS = ["group", "victim_name", "domain", "post_date", "country", "industry",
           "revenue_band", "employee_band", "data_types_claimed", "data_size_gb",
           "status", "description", "recycled_flag", "source_url", "extra_notes"]
DATE_FROM, DATE_TO = pd.Timestamp("2026-01-01"), pd.Timestamp("2026-09-30")

COUNTRY_FIX = {"USA": "United States", "UK": "United Kingdom", "Unknown": "Unknown",
               "Not confidently verified in sources reviewed": "Unknown"}


def clean_domain(s):
    if not isinstance(s, str) or not s.strip():
        return ""
    s = re.sub(r"^https?://", "", s.strip().lower())
    s = re.sub(r"^www\.", "", s)
    return s.split("/")[0]


# ---------------- data-type tagging (from post / breach descriptions) ----------------
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
    """'82 GB / 304,667 files' -> 82.0 ; '3,4 TB' -> 3400"""
    if not isinstance(s, str) or not s.strip():
        return None
    m = re.search(r"([\d.,]+)\s*(TB|GB)", s, re.I)
    if not m:
        return None
    num = m.group(1)
    num = num.replace(",", ".") if num.count(",") == 1 and "." not in num and len(num.split(",")[1]) != 3 else num.replace(",", "")
    val = float(num)
    return val * 1000 if m.group(2).upper() == "TB" else val


# ---------------- PLAY ----------------
PLAY_INDUSTRY = {
 "hurleyco.net": "Unknown", "metallco.com": "Manufacturing", "barrettmahony.com": "Construction & Engineering",
 "inglewoodgolfclub.ca": "Hospitality & Leisure", "vistahelps.com": "Manufacturing", "grunthalwelding.com": "Manufacturing",
 "sys-kool.com": "Construction & Engineering", "gtdist.com": "Retail & Wholesale", "redstaroil.com": "Energy & Resources",
 "meteor.de": "Manufacturing", "krcmachinetoolsolutions.com": "Manufacturing", "figginsfamily.com": "Food & Beverage",
 "mobiliermeq.com": "Manufacturing", "latoplast.com": "Manufacturing", "woodhavenassociation.com": "Non-profit & Religious",
 "marconi-spa.com": "Construction & Engineering", "helis.com": "Unknown", "mie-solutions.com": "Technology & Telecom",
 "platinum-grp.com": "Unknown", "gcatstx.com": "Financial Services & Insurance", "signatureservices.net": "Professional & Business Services",
 "preferredfinancial.com": "Financial Services & Insurance", "first-tek.com": "Technology & Telecom", "cambridgemgmt.net": "Real Estate",
 "sigmaplasticsgroup.com": "Manufacturing", "thebutcherbrotherscorp.com": "Food & Beverage", "debrulerco.com": "Real Estate",
 "restaurantdepot.com": "Retail & Wholesale", "recordrentacar.com": "Transportation & Logistics", "kreysler.com": "Manufacturing",
 "tax-mt.com": "Professional & Business Services", "sdr.se": "Media, Publishing & Advertising", "andorralife.com": "Unknown",
 "agscholtes.nl": "Unknown", "wringgroup.co.uk": "Manufacturing", "betcorp.com": "Construction & Engineering",
 "unitedinfrastructure.com": "Construction & Engineering", "kblaa.com": "Professional & Business Services",
 "preneed.net": "Financial Services & Insurance", "silvestriandassociates.com": "Financial Services & Insurance",
 "locatiarchitects.com": "Construction & Engineering", "wciboise.com": "Construction & Engineering", "kuhnline.com": "Unknown",
 "europtimum.com": "Unknown", "itc4u.com": "Technology & Telecom", "destinlegal.com": "Legal Services",
 "rainbowdistributorsusa.com": "Retail & Wholesale", "mundtinc.com": "Construction & Engineering", "pearsonford.com": "Automotive",
 "corleymfg.com": "Manufacturing", "thechapel.com": "Non-profit & Religious", "dallislawfirm.com": "Legal Services",
 "hightowernc.com": "Technology & Telecom", "digitallgraphics.ca": "Media, Publishing & Advertising",
 "dewaardtransport.nl": "Transportation & Logistics", "mypillow.com": "Manufacturing", "legendnt.com": "Technology & Telecom",
 "rhcountryclub.com": "Hospitality & Leisure", "nlfisher.com": "Construction & Engineering", "gwmechanical.com": "Construction & Engineering",
 "z-h.de": "Unknown", "durand-wayland.com": "Manufacturing", "ashcrofthomes.ca": "Construction & Engineering",
 "goiwc.com": "Food & Beverage", "acc-construction.com": "Construction & Engineering", "northernmc.com": "Construction & Engineering",
 "towncarinternational.com": "Transportation & Logistics", "imsmars.com": "Technology & Telecom", "emaengineer.com": "Construction & Engineering",
 "aolaml.com": "Manufacturing", "kedistributing.com": "Retail & Wholesale", "sokolin.com": "Retail & Wholesale",
 "barnessolicitors.co.uk": "Legal Services", "wittukgroup.co.uk": "Manufacturing", "valleyplatinginc.com": "Manufacturing",
 "dockprosinc.com": "Construction & Engineering", "kivells.com": "Real Estate", "specflue.com": "Manufacturing",
 "wkclaw.net": "Legal Services", "lucky-look-media.de": "Media, Publishing & Advertising", "colorado-group.com": "Construction & Engineering",
 "brokk.com": "Manufacturing", "teamtpis.com": "Construction & Engineering", "wddcfl.com": "Retail & Wholesale",
 "blockeng.com": "Construction & Engineering", "capital-drug.com": "Healthcare & Pharma", "ascentasset.com": "Financial Services & Insurance",
 "aretsifl.com": "Real Estate", "smokerschoiceusa.com": "Retail & Wholesale", "gsolutionz.com": "Technology & Telecom",
 "knightsservices.com": "Construction & Engineering", "executive-aviation.com": "Transportation & Logistics",
 "eagleie.com": "Retail & Wholesale", "circlefloors.com": "Construction & Engineering", "southern-concrete.com": "Construction & Engineering",
 "facilitiesusa.com": "Professional & Business Services", "helenkaminski.com": "Retail & Wholesale", "serrano-ind.com": "Manufacturing",
 "infinity-tx.com": "Technology & Telecom", "garlandwilliamscpa.com": "Professional & Business Services",
 "dfwaero.com": "Transportation & Logistics", "selecttool.com": "Manufacturing", "designtoprint.com": "Media, Publishing & Advertising",
 "donebowerinc.com": "Construction & Engineering", "tasolberg.com": "Retail & Wholesale", "gapvax.com": "Manufacturing",
 "flgch.com": "Legal Services", "wcctechgroup.com": "Technology & Telecom", "goprofessionalcases.com": "Manufacturing",
 "projectconsulting.com": "Construction & Engineering", "cobblestonecreekcc.com": "Hospitality & Leisure",
 "lraconstructors.com": "Construction & Engineering", "ohklegal.com": "Legal Services", "gordoncliffordmanagement.com": "Real Estate",
 "ibcaz.com": "Construction & Engineering", "btrefservices.com": "Construction & Engineering", "landmarkrehabgroup.com": "Healthcare & Pharma",
 "chemcomp.com": "Technology & Telecom", "gulfstreamservices.com": "Energy & Resources", "hendrickconstruction.com": "Construction & Engineering",
 "faulknerlocke.com": "Unknown", "atlanticcompanies.com": "Construction & Engineering", "springbrookcc.net": "Hospitality & Leisure",
 "aane.com": "Automotive", "okaex.com": "Automotive", "icefriday.com": "Automotive", "arizonalightingsales.com": "Retail & Wholesale",
 "tropictoolandmold.com": "Manufacturing", "kirbor.com": "Construction & Engineering", "paisley.ca": "Manufacturing",
 "sikatech.co.nz": "Manufacturing", "branaghinc.com": "Construction & Engineering", "lusamerica.com": "Food & Beverage",
 "hmapr.com": "Unknown", "unifiedengineering.com": "Construction & Engineering", "ucgassociates.com": "Unknown",
 "heartlandtitleco.com": "Real Estate", "makivik.org": "Government & Public Sector", "bscatcpa.com": "Professional & Business Services",
 "milwaukeeforge.com": "Manufacturing", "kaiserair.com": "Transportation & Logistics", "ralcompanies.com": "Construction & Engineering",
 "bloombus.com": "Transportation & Logistics", "ildertoncontracting.com": "Construction & Engineering", "essmetron.com": "Manufacturing",
 "degruyterbrill.com": "Media, Publishing & Advertising", "carltonscale.com": "Manufacturing", "woodfieldinc.com": "Unknown",
 "cbhhomes.com": "Construction & Engineering", "deatak.com": "Unknown", "sdplotkin.com": "Real Estate", "barsinc.net": "Energy & Resources",
 "christinelondonltd.com": "Retail & Wholesale", "aquaticcontrol.com": "Professional & Business Services",
 "allmaxnutrition.com": "Manufacturing", "fbmfg.com": "Manufacturing", "encoreroofing.com": "Construction & Engineering",
 "californiataxdata.com": "Professional & Business Services", "cemtech-corp.com": "Manufacturing", "ceelectronics.com": "Manufacturing",
 "easternice.net": "Food & Beverage", "dennysbakery.com": "Food & Beverage", "launiemarino.com": "Professional & Business Services",
 "duedoyle.com": "Legal Services", "auto-pichel.de": "Automotive", "benise-dowling.com": "Construction & Engineering",
 "lakesidetitle.com": "Real Estate",
}

play = pd.read_csv("play_raw.csv")
p = pd.DataFrame({
    "group": "Play",
    "victim_name": play["victim_name"].str.strip(),
    "domain": play["website"].map(clean_domain),
    "post_date": pd.to_datetime(play["added_date"]),
    "country": play["country"].replace(COUNTRY_FIX),
    "revenue_band": "", "employee_band": "",
    "data_types_claimed": "Not captured",
    "data_size_gb": None,
    "status": "published",
    "description": "",
    "source_url": "",
})
p["industry"] = p["domain"].map(PLAY_INDUSTRY).fillna("Unknown")
p["extra_notes"] = ("Play status: " + play["status"].str.title()
                    + "; publication_date " + play["publication_date"]
                    + "; views " + play["views"].astype(str) + "; industry inferred from company name/site")

# ---------------- ANUBIS ----------------
def anubis_industry(s):
    t = s.lower()
    rules = [("health|medical|dental|pediatric|orthop|ob-gyn|hospital|orthotic|care services", "Healthcare & Pharma"),
             ("law|legal", "Legal Services"),
             ("accounting|bookkeep|cpa|tax", "Professional & Business Services"),
             ("financ|fintech|investment|mortgage", "Financial Services & Insurance"),
             ("real estate", "Real Estate"),
             ("grocery|retail", "Retail & Wholesale"),
             ("food|beverage|dairy", "Food & Beverage"),
             ("manufactur|packaging|machinery", "Manufacturing"),
             ("engineering|construction|electrical installation", "Construction & Engineering"),
             ("aviation|aerospace|port authority|maritime", "Transportation & Logistics"),
             ("energy|fuel|mining", "Energy & Resources"),
             ("it services|technology|telecom|cloud|it /", "Technology & Telecom"),
             ("hotel|hospitality", "Hospitality & Leisure"),
             ("staffing|human capital|business services|advertising", "Professional & Business Services")]
    for pat, ind in rules:
        if re.search(pat, t):
            return ind
    return "Other"

an = pd.read_csv("anubis_raw.csv")
a = pd.DataFrame({
    "group": "Anubis",
    "victim_name": an["Victim Name"].str.strip(),
    "domain": an["Website"].map(clean_domain),
    "post_date": pd.to_datetime(an["Date Posted"], format="%d/%m/%Y"),
    "country": an["Country"].replace(COUNTRY_FIX),
    "industry": an["Industry"].map(anubis_industry),
    "revenue_band": "", "employee_band": "",
    "data_types_claimed": an["Type of Data Stolen"].map(tag_data_types),
    "data_size_gb": an["Anubis Claimed Leak Size / Files"].map(parse_size_gb),
    "status": "published",
    "description": an["Type of Data Stolen"],
    "source_url": an["Source URL(s)"],
})
files = an["Anubis Claimed Leak Size / Files"].fillna("").str.extract(r"/\s*([\d,]+)\s*files", flags=re.I)[0]
a["extra_notes"] = "industry detail: " + an["Industry"] + files.map(lambda f: f"; files {f}" if isinstance(f, str) else "")
a.loc[a["victim_name"] == "A J Taylor Electrical", "data_types_claimed"] = "IP/Engineering"

# ---------------- CHAOS ----------------
CHAOS_INDUSTRY = {"Business & Professional Services": "Professional & Business Services",
                  "Retail & Consumer": "Retail & Wholesale", "Technology": "Technology & Telecom",
                  "Chemicals": "Manufacturing", "Energy & Materials": "Energy & Resources",
                  "Non-profit": "Non-profit & Religious"}
CHAOS_OVERRIDE = {"horizonmedia.com": "Media, Publishing & Advertising",
                  "milespartnership.com": "Media, Publishing & Advertising",
                  "sleemanbreweries.ca": "Food & Beverage", "singleton.com": "Legal Services", "farmerbros.com": "Food & Beverage"}

dates = {}
for line in open("chaos_dates.txt"):
    k, v = [x.strip() for x in line.split("|")]
    dates[clean_domain(k) or k.lower()] = v

ch = pd.read_excel("chaos.xlsx", "Published Victims")
c = pd.DataFrame({
    "group": "Chaos",
    "victim_name": ch["Victim"].str.strip(),
    "domain": ch["Domain"].map(lambda d: clean_domain(d) if isinstance(d, str) and "." in d else ""),
    "country": ch["Country (inferred)"].replace(COUNTRY_FIX),
    "industry": ch["Sector (inferred)"].replace(CHAOS_INDUSTRY),
    "revenue_band": "", "employee_band": "",
    "data_types_claimed": "Not stated in post",
    "data_size_gb": ch["Claimed Leak Size (GB)"].replace(0, None),
    "status": "published",
    "description": ch["Leak Post Description (excerpt)"],
    "source_url": ch["Leak Post URL"],
})
c["industry"] = c["domain"].map(CHAOS_OVERRIDE).fillna(c["industry"])
c["post_date"] = pd.to_datetime([dates.get(d) or dates.get(n.lower())
                                  for d, n in zip(c["domain"], c["victim_name"])])
c["extra_notes"] = ("views " + ch["Site Views"].astype(str)
                    + "; post date from ransomware.live (Chaos API has no dates); sector/country inferred")

# Chaos pending (countdown) posts: victim hidden, kept in a separate file
pend = pd.read_excel("chaos.xlsx", "Pending (Obfuscated)")
pend = pend[pend["Status at Snapshot"] == "Pending"]
cp = pd.DataFrame({"group": "Chaos", "victim_name": "Undisclosed (countdown)", "status": "countdown",
                   "data_size_gb": pend["Claimed Size (GB)"].replace(0, None),
                   "publish_deadline": pd.to_datetime(pend["Publish Deadline (UTC)"]).dt.date,
                   "source_url": pend["Leak Post URL"]})
cp.to_csv("chaos_countdown_posts.csv", index=False)

# ---------------- MERGE ----------------
allrows = pd.concat([p, a, c], ignore_index=True)
for col in COLUMNS:
    if col not in allrows:
        allrows[col] = ""

dropped = allrows[~allrows["post_date"].between(DATE_FROM, DATE_TO)]
master = allrows[allrows["post_date"].between(DATE_FROM, DATE_TO)].copy()

# recycled / repost flags
master["recycled_flag"] = ""
master.loc[master["victim_name"].str.contains(r"part 2|part ii", case=False), "recycled_flag"] = "repost (part 2)"
dom = master[master["domain"] != ""]
multi = dom.groupby("domain")["group"].nunique()
for d in multi[multi > 1].index:
    master.loc[master["domain"] == d, "recycled_flag"] = "claimed by multiple groups"
dup_same = dom[dom.duplicated(["group", "domain"], keep=False)]
master.loc[dup_same.index, "recycled_flag"] = "listed twice by same group"

master["post_date"] = master["post_date"].dt.strftime("%Y-%m-%d")
master = master.sort_values(["group", "post_date"])[COLUMNS]
master.to_csv("master.csv", index=False, encoding="utf-8")

for g, df in master.groupby("group"):
    df.to_csv(f"{g.lower()}_schema.csv", index=False, encoding="utf-8")

print("kept per group:\n", master["group"].value_counts())
print("\ndropped (outside Jan–Sep 2026 or no date):\n", dropped.groupby("group").size())
print("\nno-date chaos:", dropped[(dropped.group == "Chaos") & dropped.post_date.isna()]["victim_name"].tolist())
print("\nrecycled flags:\n", master[master.recycled_flag != ""][["group", "victim_name", "recycled_flag"]])
print("\ncountdown posts saved:", len(cp))

# long table for Q8: one row per (victim, data type)
dt = master[["group", "victim_name", "industry", "data_types_claimed"]].copy()
dt["data_type"] = dt["data_types_claimed"].str.split(";")
dt = dt.explode("data_type").drop(columns="data_types_claimed")
dt.to_csv("master_datatypes.csv", index=False, encoding="utf-8")
print("datatype rows:", len(dt))
