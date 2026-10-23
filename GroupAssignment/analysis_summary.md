# DLS Analysis Summary — Working Draft
Generated 2026-10-05 from `DLS_master.xlsx` (master sheet, 287 rows, groups Play/Anubis/Chaos, Jan–Sep 2026).

## ⚠️ Status / blockers — read first

1. **Only 3 of the required 5 DLS groups are in the data.** Play, Anubis, Chaos are built; raw files/scripts for DLS #4 and #5 have not been added to the folder yet. All numbers below are 3-group numbers and will shift once #4/#5 are merged in.
2. **The pipeline is currently not re-runnable as-is.** `build_master.py` expects `play_raw.csv`, `anubis_raw.csv`, `chaos.xlsx`, `chaos_dates.txt`, but the folder has `play_victims_all_pages.csv`, `anubis_victims.csv`, `Chaos_Ransomware_Victims.xlsx`, and **no `chaos_dates.txt`**. The existing `master.csv` / `DLS_master.xlsx` are valid, current outputs (287 rows matches your description), but re-running the script today would fail until the filenames are updated in the script and `chaos_dates.txt` is supplied. I have not renamed your originals, per your instructions. **I need `chaos_dates.txt` from you before I can extend the pipeline for DLS #4/#5** (step 2 of your task list).
3. **`revenue_band` and `employee_band` are empty for all 287 rows.** Q6 ("does company size/revenue affect risk?") currently cannot be answered quantitatively from this dataset — see Q6 section below for options.
4. **Data-type tags (Q8) are only real for Anubis (65 victims / 97 tag-rows).** Play's `data_types_claimed` is "Not captured" for all 167 rows (scraper didn't capture it) and Chaos's is "Not stated in post" for all 55 rows. The Q8 breakdown below is therefore effectively an Anubis-only breakdown, not a 3-group one — flag this limitation explicitly in the report.
5. **Play has only 2 victims in April 2026** vs 36–41 in Feb/Mar and 13–17 in May/Jun — consistent with a scraper page gap, not a real slowdown. Recommend re-checking the Play scrape for April before finalizing Q3 trend charts (see Sanity Checks).

---

## Data overview

| group | victims | date range |
|---|---|---|
| Play | 167 | 2026-01 to 2026-09 |
| Anubis | 65 | 2026-01 to 2026-09 |
| Chaos | 55 | 2026-01 to 2026-09 |
| **Total** | **287** | **2026-01-02 to 2026-09-29** |

---

## Sanity checks

**Duplicates:** 0 exact duplicate rows (same group + victim_name + domain).

**Cross-group overlaps (same victim claimed by ≥2 groups):** 0 found, by domain match and by normalized victim-name match (strips "Part 2"/"Part II" and punctuation). Within this 3-group dataset there is no evidence of the same company being posted by more than one of Play, Anubis, or Chaos.

**Within-group reposts:** 1 — Anubis relisted one victim as a "Part 2" post (same company, same group, ~weeks apart), flagged `recycled_flag = "repost (part 2)"`.

**Unknown / unmapped country:** 10 rows (Anubis 8, Chaos 2) — 3.5% of 287.

**Unknown industry:** 13 rows, all Play (Play industry is inferred from company name/domain by a lookup table; 13 companies didn't match any pattern).

**Month-gap check (possible scraper misses):**

| month | Anubis | Chaos | Play | Total |
|---|---|---|---|---|
| 2026-01 | 4 | 2 | 17 | 23 |
| 2026-02 | 11 | 3 | 36 | 50 |
| 2026-03 | 8 | 6 | 41 | 55 |
| **2026-04** | 8 | 3 | **2** | 13 |
| 2026-05 | 3 | 8 | 17 | 28 |
| 2026-06 | 9 | 5 | 13 | 27 |
| 2026-07 | 9 | 14 | 15 | 38 |
| 2026-08 | 7 | 6 | 17 | 30 |
| 2026-09 | 6 | 8 | 9 | 23 |

Play April 2026 (2 victims) is the one clear outlier against its own neighboring months — flagged as a likely scraper gap, not real behavior. Anubis and Chaos show no comparable gaps.

---

## Q1 — What countries are most targeted?

| country | victims | % of 287 |
|---|---|---|
| United States | 206 | 71.8% |
| Canada | 26 | 9.1% |
| United Kingdom | 12 | 4.2% |
| Unknown | 10 | 3.5% |
| Germany | 7 | 2.4% |
| Italy | 3 | 1.0% |
| Netherlands | 3 | 1.0% |
| New Zealand | 2 | 0.7% |
| South Korea | 2 | 0.7% |
| France | 2 | 0.7% |
| Australia | 2 | 0.7% |
| Sweden | 2 | 0.7% |
| (12 more countries) | 1 each | 0.3% each |

US + Canada = 81% of all victims in this dataset. 19 countries total appear.

**Tableau steps:**
- New worksheet, connect to `DLS_master.xlsx` → `master` sheet.
- **Columns:** `CNT(victim_name)` (or just drag `victim_name` to Rows/Columns — Tableau will aggregate as COUNT by default for a dimension; to be explicit, create a calculated field `Victim Count = COUNT([victim_name])`).
- **Rows:** `country` (sorted descending by the count measure — click the sort icon, or Analysis → Sort).
- **Marks:** Bar chart (horizontal bar). Color = `country` or leave default; Label = the count.
- **Filter:** Top N filter on `country` by `Victim Count` (e.g. Top 10) to keep the chart readable, with an "Unknown" exclusion toggle if you want a clean version.
- Alternative: a filled **map** — drag `country` to the view (Tableau auto-geocodes), `Victim Count` to Color. Good as a second, complementary visual.

---

## Q2 — Why are some countries more targeted than others?

This is a reasoning question, not a pure count — but the data gives three grounded angles to argue from (don't present these as proven causes, present as "patterns consistent with"):

1. **English-language, high-digitization economies dominate.** US/Canada/UK/Australia/NZ together = ~85% of victims — all are large, highly digitized economies with large populations of small-to-mid-size firms running internet-facing infrastructure (RDP, VPNs) that RaaS affiliates commonly exploit. Cross-reference this claim in your report text against a public source (e.g. ransomlook.io's own country stats) rather than asserting it from this dataset alone.
2. **US size effect, not necessarily higher per-capita risk.** The US has the largest base rate of mid-market companies globally, so raw victim counts there are partly just a denominator effect. If you want a stronger Q2 answer, consider normalizing (e.g. victims per capita, or per $ of GDP) using an external population/GDP reference table — flag this as a stretch goal given the timeline.
3. **Industry mix by country** (supporting cut): cross-tab `country` x `industry` in Tableau to see if the same industries (Manufacturing, Construction & Engineering — see Q7) are disproportionately hit in the top 2 countries, which would support "targeted sector concentration" as a secondary explanation. Build this as a filled-map-plus-tooltip or a stacked bar (Columns = country (top 6 + Other), Rows = CNT, Color = industry).

**Tableau steps (supporting chart — country × industry):**
- **Columns:** `country` (filtered to Top 6 via Top-N filter).
- **Rows:** `Victim Count` (COUNT of victim_name).
- **Marks:** Stacked bar. **Color:** `industry`.
- **Filter:** Top N on country as above.

---

## Q3 — Which ransomware group is the most prolific?

**Total victims (Jan–Sep 2026), 3 groups currently in scope:**

| group | victims | % of 287 |
|---|---|---|
| **Play** | **167** | **58.2%** |
| Anubis | 65 | 22.6% |
| Chaos | 55 | 19.2% |

**By raw count, Play is the most prolific by a wide margin** — nearly 3x Anubis and Chaos combined is not quite right (Anubis+Chaos=120, Play=167, so Play ≈ 1.4x the other two combined). Caveat: once DLS #4/#5 are added this ranking could change, and the April Play dip (sanity check above) means the true Play total may be understated by a handful of victims if that's a scraper gap.

**Per month (same table as Sanity Checks, repeated for convenience):**

| month | Anubis | Chaos | Play |
|---|---|---|---|
| 2026-01 | 4 | 2 | 17 |
| 2026-02 | 11 | 3 | 36 |
| 2026-03 | 8 | 6 | 41 |
| 2026-04 | 8 | 3 | 2 |
| 2026-05 | 3 | 8 | 17 |
| 2026-06 | 9 | 5 | 13 |
| 2026-07 | 9 | 14 | 15 |
| 2026-08 | 7 | 6 | 17 |
| 2026-09 | 6 | 8 | 9 |

Play leads in every month except April (its likely scraper-gap month) and is roughly tied with Anubis+Chaos combined in Sep. Chaos trends upward over the year (2 → 14 → 8), the only group with a visible growth trend; Anubis is roughly flat; Play is front-loaded into Feb–Mar then declines.

**"Most successful" (secondary angle, supports Q4 too):** median actor-claimed leak size is larger for Chaos (400 GB) than Anubis (199 GB); Play doesn't disclose leak size at all but its posts draw a much higher "views" counter on the DLS itself (median ~33,600 unverified views per Play post) — i.e. three different groups are "winning" on three different axes (volume, leak size, site traffic), which is itself a Q9-worthy insight.

**Tableau steps — total by group:**
- **Columns:** `group`. **Rows:** `Victim Count` (COUNT of victim_name).
- **Marks:** Bar chart, Color = `group`, Label = count. Sort descending.

**Tableau steps — per-month trend:**
- **Columns:** `MONTH(post_date)` (continuous, green pill — right-click `post_date` → choose the continuous month, not the discrete date part) or `post_date` truncated to month.
- **Rows:** `Victim Count`.
- **Marks:** Line chart. **Color:** `group` (3 lines).
- **Filter:** `post_date` restricted to 2026-01-01 .. 2026-09-30 (belt-and-braces even though the data is pre-filtered).

---

## Q5 — Is it common for actors to "re-brand"/repost older leaks?

**Within this 3-group dataset: no.** 0 of 287 victims were found listed by more than one of the three groups (checked by domain match and by normalized victim name, stripping "Part 2/II" suffixes). The only repost found is a **single within-group** case — Anubis relisted one victim as a follow-up "Part 2" post roughly weeks after the original listing, most likely because the victim didn't pay by the original deadline (common RaaS pressure tactic), not a cross-group rebrand.

**Honest framing for the report:** this dataset does not show evidence of cross-group rebranding/repurposing — but that's a meaningful finding in itself (worth stating as "no evidence found in-sample" rather than "it doesn't happen," since: (a) we only have 3 of 5 groups so far, (b) confirming true rebranding of *older public breaches* would require checking post content/dates against breach-aggregator timelines, which is out of scope per your no-onion/no-source-url-fetch rule, and (c) company name variations (abbreviations, rebrands, acquisitions) could hide a match that simple domain/name matching misses). Recommend saying this plainly rather than forcing a stronger conclusion than the data supports — re-check once DLS #4/#5 are in, since a 5-group dataset is much more likely to surface a real overlap.

**Tableau steps:**
- Simplest honest visual: a single stat tile / KPI showing count of `recycled_flag != ""` (1) vs total (287), or a short table: `recycled_flag`, `Victim Count`.
- **Columns:** `recycled_flag` (blank vs "repost (part 2)"). **Rows:** `Victim Count`. **Marks:** Bar. Keep this chart small — it's a supporting visual, not a headline one, since the finding is "didn't find much."

---

## Q6 — Does company size/revenue affect risk?

**Cannot currently be answered quantitatively** — `revenue_band` and `employee_band` are blank for all 287 rows in `master.csv`/`DLS_master.xlsx`. None of the three raw sources (Play, Anubis, Chaos scrapes) captured this field.

Options, in order of effort:
1. **Lowest effort / recommended given the deadline:** answer Q6 qualitatively using `industry` and `description`/`extra_notes` text as a size proxy (e.g. note how many victim names/domains read as small local/regional firms vs. recognizable larger brands), and be explicit in the report that structured revenue/employee data wasn't available from the DLS posts themselves — most ransomware leak sites don't publish this, which is itself a defensible finding ("DLS posts rarely disclose victim revenue/headcount, making this dimension hard to study directly from leak-site data alone").
2. **Medium effort:** if time allows before the deadline, a very small manual sample (e.g. 20–30 victim domains) could be size-banded using public employee-count estimates (LinkedIn company page headcount, Crunchbase) — but this is extra scraping work NTU's brief doesn't require and risks going out of scope this close to the deadline. Not recommended given ~1 day left.
3. Given the time left, I'd suggest going with option 1 and spending remaining hours on Q8/Q9 instead, where you have real data.

**Tableau:** no chart possible without the data. If you go with option 1, the only "visual" is a text/insight box in the report, not a Tableau sheet — that's fine, the brief only requires visuals where you have supporting data.

---

## Q7 — Which industries are more prone to ransomware threats?

| industry | victims | % of 287 |
|---|---|---|
| Manufacturing | 56 | 19.5% |
| Construction & Engineering | 48 | 16.7% |
| Healthcare & Pharma | 29 | 10.1% |
| Retail & Wholesale | 18 | 6.3% |
| Technology & Telecom | 17 | 5.9% |
| Professional & Business Services | 17 | 5.9% |
| Legal Services | 16 | 5.6% |
| Transportation & Logistics | 15 | 5.2% |
| Unknown | 13 | 4.5% |
| Financial Services & Insurance | 12 | 4.2% |
| Energy & Resources | 9 | 3.1% |
| Real Estate | 9 | 3.1% |
| Food & Beverage | 8 | 2.8% |
| Media, Publishing & Advertising | 7 | 2.4% |
| Automotive | 6 | 2.1% |
| Hospitality & Leisure | 4 | 1.4% |
| Non-profit & Religious | 2 | 0.7% |
| Government & Public Sector | 1 | 0.3% |

**Industry × group breakdown** (shows this isn't uniform — each group has a different industry signature):

| industry | Anubis | Chaos | Play |
|---|---|---|---|
| Manufacturing | 7 | 17 | 32 |
| Construction & Engineering | 6 | 6 | 36 |
| Healthcare & Pharma | 17 | 10 | 2 |
| Legal Services | 8 | 1 | 7 |
| Retail & Wholesale | 3 | 3 | 12 |
| Technology & Telecom | 4 | 3 | 10 |
| Financial Services & Insurance | 6 | 1 | 5 |
| Transportation & Logistics | 4 | 4 | 7 |
| (remaining industries: 9 or fewer each) | | | |

Why (grounded reasoning, same caveat as Q2 — state as interpretation, not fact): Manufacturing and Construction & Engineering together are 36% of all victims and both sectors are known for (a) OT/IT-converged environments with legacy, hard-to-patch systems, (b) high operational-downtime cost, which raises ransom-payment likelihood/urgency — a common actor targeting rationale — and (c) lower average security maturity/budget than finance or tech. Healthcare & Pharma is disproportionately an **Anubis** target (17 of Anubis's 65 victims, 26%), noticeably more than its share of Play's or Chaos's victims — worth calling out as an Anubis-specific targeting pattern rather than an industry-wide one.

**Tableau steps:**
- **Columns:** `industry`. **Rows:** `Victim Count`. **Marks:** Bar, sorted descending. **Filter:** Top N (e.g. Top 10) to keep labels legible.
- Second view for the group breakdown: **Columns:** `industry` (Top 8, Top-N filtered), **Rows:** `Victim Count`, **Marks:** stacked or side-by-side bar, **Color:** `group`.

---

## Q8 — What kinds of data do actors target, by industry?

**Important caveat to put directly in the report:** this breakdown is effectively **Anubis-only** (65 victims, 97 tag-rows since victims can have multiple tags). Play's `data_types_claimed` is "Not captured" for all 167 rows and Chaos's is "Not stated in post" for all 55 rows — neither scrape captured real data-type detail, so they're excluded from this cut rather than shown as misleading zeros.

**Tag frequency (Anubis, 97 tag-rows across 65 victims):**

| data type | count |
|---|---|
| Unspecified | 20 |
| Client/Customer | 17 |
| Medical/PHI | 14 |
| PII | 11 |
| Financial | 10 |
| Employee/HR | 10 |
| IP/Engineering | 8 |
| Legal | 5 |
| Credentials | 1 |
| Contracts | 1 |

**Industry × data type (Anubis only):**

| industry | Client/Cust | Contracts | Credentials | Employee/HR | Financial | IP/Eng | Legal | Medical/PHI | PII | Unspecified |
|---|---|---|---|---|---|---|---|---|---|---|
| Construction & Engineering | 1 | 1 | 1 | 2 | 1 | 4 | 0 | 0 | 1 | 1 |
| Energy & Resources | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 3 |
| Financial Services & Insurance | 3 | 0 | 0 | 0 | 2 | 0 | 0 | 0 | 1 | 1 |
| Food & Beverage | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 |
| Healthcare & Pharma | 4 | 0 | 0 | 3 | 3 | 0 | 0 | 14 | 4 | 2 |
| Legal Services | 5 | 0 | 0 | 1 | 0 | 1 | 5 | 0 | 4 | 0 |
| Manufacturing | 0 | 0 | 0 | 1 | 0 | 1 | 0 | 0 | 0 | 5 |
| Professional & Business Services | 2 | 0 | 0 | 1 | 4 | 0 | 0 | 0 | 0 | 1 |
| Retail & Wholesale | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 1 | 2 |
| Technology & Telecom | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 2 |
| Transportation & Logistics | 0 | 0 | 0 | 1 | 0 | 2 | 0 | 0 | 0 | 2 |

Clear pattern: **Healthcare & Pharma → Medical/PHI dominates (14 of 29 Healthcare tag-rows)**, exactly as you'd expect given HIPAA-protected records. **Legal Services → Legal + PII + Client/Customer** dominate (14 of 15 tag-rows across those 3 types) — consistent with case files and client personal data being the valuable assets in that sector. Construction/Engineering skews toward **IP/Engineering** (drawings, project data) more than any other industry.

**Tableau steps:**
- Build this as a **heatmap**: **Columns:** `data_type` (from the `data_types` sheet — note: connect this worksheet to the `data_types` tab of the workbook, not `master`, since it's already one-row-per-tag). **Rows:** `industry`. **Marks:** Square/heatmap mark type, **Color:** `CNT(data_type)` using a sequential color palette, **Label:** the count.
- **Filter:** exclude `data_type` = "Not captured" / "Not stated in post" (and optionally exclude `group` ≠ Anubis, or just filter data_type to those two values out — same effect), and add a text box/caption on the dashboard noting the Anubis-only caveat so it's visible on the visual itself, not just in your write-up.

---

## Q9 — Candidate insights (pick 3 of these 5)

1. **Each group "wins" on a different axis.** Play dominates by volume (167 victims, 58% of total) but discloses neither leak size nor data type; Chaos has the largest median claimed leak size (400 GB vs Anubis's 199 GB) and a rising monthly trend (2→14→8 victims Jan→Jul→Sep); Play posts draw far higher claimed site-traffic (~33,600 median "views" per post) than the other two disclose. "Most successful" depends entirely on which metric you pick — worth making this the center of your Q3/Q4 narrative rather than picking one winner.
2. **Healthcare targeting is an Anubis-specific pattern, not an industry-wide one.** Healthcare & Pharma is 26% of Anubis's victims (17/65) vs 18% of Chaos's (10/55) and just 1% of Play's (2/167) — the same industry is targeted very differently by different actors, suggesting affiliate/group-level specialization rather than a universal "healthcare is the top target" story.
3. **Manufacturing + Construction & Engineering = over a third of all victims (36.2%), overwhelmingly via Play** (32 and 36 of their respective totals come from Play alone) — these look like Play's preferred hunting ground specifically, more than a general ransomware-wide pattern, since Anubis and Chaos's combined share of those two industries (13+6=19, 13+6=19) is much smaller relative to their own totals.
4. **No confirmed cross-group victim overlap found in 287 records** (see Q5) — at odds with the "rebranding is common" narrative sometimes claimed in industry reporting; worth noting as a finding that complicates, not confirms, the premise of Q5, pending the DLS #4/#5 data.
5. **DLS posts rarely carry structured victim metadata.** None of the three scraped sources captured revenue or employee-count bands, and two of three (Play, Chaos) didn't capture data-type detail either — only Anubis's free-text "Type of Data Stolen" field was granular enough to tag. This is itself a methodological finding worth stating: DLS operators format their "shaming" posts very differently, which limits what a comparative study across groups can measure consistently (ties directly into Q10, "lessons learnt").

---

## Next steps / what I need from you

- **`chaos_dates.txt`** — needed to make the pipeline re-runnable (it's missing from the folder; without it I can't rebuild Chaos post dates even for the current 3 groups).
- **Raw files for DLS #4 and #5** — not yet in the folder; task 2 (extending `build_master.py`) is blocked until these arrive.
- Everything above is built from the **existing 3-group `DLS_master.xlsx`** and will need re-running once #4/#5 land — I'll re-generate this file and all the numbers at that point.
