#!/usr/bin/env python3
"""Offline lookup across the bundled sprinkler recall references.

Usage:
  python scripts/lookup.py TERM [TERM ...] [--year YYYY]
  Quote multi-word models, e.g. "ELO GB"; adjacent terms are also tried together.

TERM can be a manufacturer or frame marking (Central, CSC, Star, Gem, Globe,
Omega, Tyco, Viking), a model (GB, LF, ME-1, J, C-1A), a SIN (GL1401, TY5151)
or a bulb marking (Job F5, YD05, ATOP5). The script prints:
  1. recall-register records that match, with a year check when --year is given
  2. Tyco model-index rows (table, K-factor, orientation, seal style, figure pages)
  3. hits in the 2009 historical O-ring identification list
  4. UL/FM counterfeit and certification alerts (not recalls)
A hit is a lead for identification, not a recall or counterfeit determination.
The script reads only bundled files and never uses the network.
"""
import json
import re
import sys
from pathlib import Path

REF = Path(__file__).resolve().parent.parent / "references"

# Frame or logo markings that point to a manufacturer family (cue only).
ALIASES = {
    "CSC": "Central",
    "CENTRAL": "Central",
    "STAR": "Star",
    "GEM": "Gem",
    "GLOBE": "Globe",
    "OMEGA": "Omega",
}


def norm(s):
    return re.sub(r"[^A-Z0-9]", "", str(s).upper())


def years_in(scope):
    """Return (start, end) for scopes like '1989-2000' or 'mid-1970s through June 2001'."""
    nums = [int(n) for n in re.findall(r"(19\d\d|20\d\d)", scope)]
    if len(nums) >= 2:
        return nums[0], nums[-1]
    if len(nums) == 1 and "since" in scope.lower():
        return nums[0], None
    return None


def year_note(scope, year):
    rng = years_in(scope)
    if year is None or rng is None:
        return ""
    lo, hi = rng
    approx = "mid-" in scope or "through June" in scope or "since" in scope
    inside = year >= lo and (hi is None or year <= hi)
    tag = "IN SCOPE" if inside else "outside this record's years"
    if approx and (year in (lo, hi)):
        tag += " (boundary year; read the notice wording)"
    return f"  year {year}: {tag}"


def register_hits(terms, year):
    reg = json.loads((REF / "recall-register.json").read_text(encoding="utf-8"))
    out = []
    for r in reg["records"]:
        maker = r["manufacturer"]
        models = r.get("models", [])
        hit_models = []
        brand_hit = False
        for t in terms:
            nt = norm(t)
            fam = ALIASES.get(t.upper())
            if fam and fam.lower() in maker.lower():
                brand_hit = True
            if nt and nt in norm(maker):
                brand_hit = True
            hit_models += [m for m in models if norm(m) == nt]
        if hit_models or brand_hit:
            out.append((r, sorted(set(hit_models)), brand_hit))
    return reg.get("as_of", ""), out


def index_hits(terms):
    idx = json.loads((REF / "tyco-model-index.json").read_text(encoding="utf-8"))
    rows = idx["rows"]
    exact = []
    for t in terms:
        nt = norm(t)
        if not nt or t.upper() in ALIASES:
            continue
        for r in rows:
            nm = norm(r.get("model_as_printed", ""))
            if nt in (nm, nm[:-3] if nm.endswith("DRY") else None) and r not in exact:
                exact.append(r)
    return idx.get("seal_styles", {}), exact


def oring_hits(terms):
    lines = (REF / "o-ring-identification-list-2009.txt").read_text(encoding="utf-8").splitlines()
    hits = []
    current_list, current_maker = "", ""
    for line in lines:
        s = line.strip()
        if s.startswith("LIST A"):
            current_list = "List A (wet)"
        elif s.startswith("LIST B"):
            current_list = "List B (dry)"
        elif s and s == s.upper() and re.search(r"(CORP|INC|CO\.|COMPANY|SPRINKLER)", s):
            current_maker = s
        for t in terms:
            nt = norm(t)
            if len(nt) < 3 or t.upper() in ALIASES:
                continue
            tokens = [norm(x) for x in re.split(r"[,\s]+", s) if x]
            if nt in tokens:
                hits.append((t, current_list, current_maker, s))
    return hits


# Brand words used only by the counterfeit-alert section (section 4).
ALERT_BRANDS = {
    "TYCO": "TYCO", "TFP": "TFP", "GLOBE": "GLOBE", "VIKING": "Viking", "HD": "HD",
    "ANGUS": "ANGUS", "KARTAR": "KARTAR", "PROTECTOR": "PROTECTOR", "MAFCO": "MAFCO",
    "FIREX": "FIREX", "RELIABLE": "Reliable", "VICTAULIC": "Victaulic", "NANJING": "Nanjing",
    "FUJIAN": "Fujian", "XIAMEN": "Xiamen", "ANBER": "Anber Globe",
}


COUNTERFEIT_ONLY_BULBS = {"ATOP5", "YD5", "YH5", "CDGIX"}
GENERIC_MARKS = {"CULUS", "CUL", "UL", "FM", "LPCB", "LPC", "VDS", "ESFR", "SSU", "SSP", "SU", "SP",
                 "HSW", "TFP", "QR", "SR", "TYCO", "GLOBE"}


def bulb_canon(x):
    """Normalize bulb text: drop symbols and read a zero before the last digit (YD05) as YD5."""
    n = norm(x)
    n = re.sub(r"^([A-Z]+)0(\d)$", r"\1\2", n)
    return n


def temp_pair_consistent(n):
    """True for a normal Fahrenheit/Celsius pair such as 155F68C or 68C155F."""
    m = re.fullmatch(r"(\d{2,3})F(\d{2,3})C", n) or re.fullmatch(r"(\d{2,3})C(\d{2,3})F", n)
    if not m:
        return False
    a, b = int(m.group(1)), int(m.group(2))
    f, c = (a, b) if n.find("F") < n.find("C") else (b, a)
    return abs((f - 32) * 5 / 9 - c) <= 2


def strong_marking(n):
    """Match only distinctive markings. Skip agency marks, orientation codes, years,
    single temperatures, K-factors and normal temperature pairs, which genuine units share.
    A mismatched pair such as 155F168C still matches."""
    if n in GENERIC_MARKS:
        return False
    if re.fullmatch(r"\d{4}", n) or re.fullmatch(r"\d{2,3}[FC]", n) or re.fullmatch(r"K\d{1,3}", n):
        return False
    if temp_pair_consistent(n):
        return False
    return bool(len(n) >= 4 and re.search(r"\d", n) and re.search(r"[A-Z]", n)) or len(n) >= 6 or bool(re.fullmatch(r"\d+[FC]\d+[FC]", n))


def alert_hits(terms, year):
    path = REF / "counterfeit-alerts.json"
    if not path.exists():
        return None
    data = json.loads(path.read_text(encoding="utf-8"))
    recs = data["records"]
    nterms = {norm(t): t for t in terms if norm(t)}
    bterms = {bulb_canon(t): t for t in terms if norm(t)}
    desig, marks, brands, cross = [], [], {}, []
    for r in recs:
        d_hit = [d for d in r.get("copied_designations", []) if norm(d) in nterms]
        m_hit = []
        for m in r.get("other_markings", []):
            if norm(m) in nterms and strong_marking(norm(m)):
                m_hit.append(m)
        for b in r.get("bulb_markings", []):
            bc = bulb_canon(b)
            short = bc[3:] if bc.startswith("JOB") else None
            # bulb_markings hold only counterfeit-relevant bulb text, so an exact match is enough
            if bc in bterms or (short and short in bterms):
                m_hit.append(b)
        if d_hit:
            desig.append((r, d_hit, m_hit))
        elif m_hit:
            marks.append((r, m_hit))
        for t in terms:
            b = ALERT_BRANDS.get(t.upper())
            if b and any(norm(b) == norm(c) or norm(b) in norm(c) for c in r.get("claimed_brand", [])):
                brands.setdefault(b, set()).add(r["id"])
    keys = set(nterms) | set(bterms)
    for c in data.get("cross_alert_statements", []):
        if any(norm(tr) in keys for tr in c.get("triggers", [])):
            cross.append(c)
    rules = []
    for r, d_hit, _ in desig:
        rule = r.get("date_rule")
        if rule and norm(rule["designation"]) in {norm(x) for x in d_hit}:
            has_brand = norm(rule["brand"]) in nterms
            if year is not None and has_brand and year >= rule["year_from"]:
                rules.append("TRIGGERED: " + rule["note"])
            else:
                rules.append("Check: " + rule["note"])
    return data.get("as_of", ""), desig, marks, brands, cross, rules


def print_alerts(terms, year):
    res = alert_hits(terms, year)
    print("\n== Counterfeit / certification alerts (UL, FM; not recalls) ==")
    if res is None:
        print("counterfeit-alerts.json not found.")
        return
    as_of, desig, marks, brands, cross, rules = res
    print(f"(as of {as_of}) A hit means counterfeiters copied this designation or marking. "
          "Authentic products are not implicated. Report an Alert only when a listed cue, "
          "provenance detail or user concern applies.")
    if not (desig or marks or brands):
        print("No alert record matched. This does not authenticate the unit.")
    for line in rules:
        print("  " + line)
    for r, d_hit, m_hit in desig:
        nums = ", ".join(re.sub(r"^(UL|FM) ", "", n) for n in r.get("notice_numbers", [])) or "no number"
        extra = f"; also marking {m_hit}" if m_hit else ""
        kind = "CERTIFICATE ALERT" if r.get("alert_type", "").startswith("falsified") else "counterfeit alert"
        print(f"- {r['id']} [{kind}]: {r['issuer']} {nums} ({r['notice_date']}) | found: {r.get('found_in','')} | designation {d_hit}{extra}")
        if r.get("authentic_excluded"):
            print(f"  authentic: {r['authentic_excluded']}")
        if r.get("external_cues"):
            print("  external cues (one is enough for suspect): " + "; ".join(r["external_cues"]))
        if r.get("supporting_cues"):
            print("  supporting cues (lead only): " + "; ".join(r["supporting_cues"]))
        if r.get("document_cues"):
            print("  document cues: " + "; ".join(r["document_cues"]))
        if not (r.get("external_cues") or r.get("supporting_cues") or r.get("document_cues")):
            print("  no distinguishing cue published; matching markings alone are not a cue.")
        if r.get("removed_unit_cues"):
            print("  removed-unit cues only: " + "; ".join(r["removed_unit_cues"]))
        if r.get("non_discriminators"):
            print("  not cues: " + "; ".join(r["non_discriminators"]))
        print(f"  photo-resolvable: {r.get('photo_resolvable','')} | source: {r.get('source_url','')}")
        if r.get("limitation"):
            print(f"  limitation: {r['limitation']}")
    input_marks = {norm(t) for t in terms}
    tgf = input_marks & {"TYCO", "TFP", "GLOBE", "FM"}
    for r, m_hit in marks:
        nums = ", ".join(re.sub(r"^(UL|FM) ", "", n) for n in r.get("notice_numbers", [])) or "no number"
        des = ", ".join(r.get("copied_designations", [])) or "none stated"
        cb = {bulb_canon(m) for m in m_hit}
        if tgf and cb & COUNTERFEIT_ONLY_BULBS:
            label = "external cue: counterfeit-only bulb on a Tyco, Globe or FM-marked unit"
        else:
            label = "pointer only; read the record"
        print(f"- {r['id']}: marking {m_hit} | {r['issuer']} {nums} ({r['notice_date']}) | brand {r.get('claimed_brand', [])} | designations {des} | {label}")
    for b, ids in sorted(brands.items()):
        if not any(norm(b) == norm(c) for r, _, _ in desig for c in r.get("claimed_brand", [])):
            print(f"- brand {b} appears in {len(ids)} alert(s): {', '.join(sorted(ids))}. Not evidence; read a record only if a visible cue or the SIN points to it.")
    for c in cross:
        print(f"  {c['issuer']} statement: {c['statement']} Use: {c['use']}")


def main(argv):
    year = None
    terms = []
    i = 0
    while i < len(argv):
        if argv[i] == "--year" and i + 1 < len(argv):
            year = int(argv[i + 1])
            i += 2
            continue
        terms.append(argv[i])
        i += 1
    if not terms or terms[0] in ("-h", "--help"):
        print(__doc__)
        return 0
    # Multi-word models such as "ELO GB" or "GB QR": also try adjacent pairs joined.
    terms = terms + [terms[k] + " " + terms[k + 1] for k in range(len(terms) - 1)]

    as_of, reg = register_hits(terms, year)
    print(f"== Recall register (as of {as_of}) ==")
    if not reg:
        print("No register record matched. This is NOT clearance; see SKILL.md step 5.")
    for r, models, brand in reg:
        why = f"model match {models}" if models else "manufacturer/brand match only (model not matched)"
        print(f"- {r['id']}: {r['notice_type']} {r['notice_number']} ({r.get('notice_date','')}) | {r['manufacturer']} | {r['construction']} | made {r['manufacture_scope']} | {why}")
        yn = year_note(r["manufacture_scope"], year)
        if yn and models:
            print(yn)
        print(f"  needs: {r.get('required_evidence','')}")
        print(f"  status: {r.get('program_status','')}")
        print(f"  source: {r.get('source_url','')} | retrieval: {r.get('source_retrieval','')}")

    styles, rows = index_hits(terms)
    print("\n== Tyco model index (Central/Gem/Star tables) ==")
    if not rows:
        print("No exact model row.")
        idx_rows = json.loads((REF / "tyco-model-index.json").read_text(encoding="utf-8"))["rows"]
        near = sorted({r["model_as_printed"] for t in terms if len(norm(t)) >= 2 and t.upper() not in ALIASES
                       for r in idx_rows if norm(t) in norm(r["model_as_printed"])})
        if near:
            print("  models containing that text: " + ", ".join(near[:12]) + " (re-run with the exact model)")
    used = sorted({st for r in rows for st in (r.get("seal_style") or [])})
    for st in used:
        d = styles.get(st, {})
        print(f"  style {st}: O-ring = {d.get('o_ring')}; Belleville = {d.get('belleville')} (see assets/tyco-seal-comparison-page-9.png)")
    for r in rows:
        print(f"- Table {r['table']} {r['manufacturer']} {r['model_as_printed']} K={r.get('k_factor')} {r.get('orientation')} | element: {r.get('element')} | seal style {r.get('seal_style')} | 1998 transition: {r.get('seal_transition')} | figure {r.get('figure')} on PDF page(s) {r.get('figure_pages')}")

    hits = oring_hits(terms)
    print("\n== 2009 historical O-ring list (construction cue, not a recall list) ==")
    if not hits:
        print("No hit.")
    for t, lst, maker, line in hits:
        print(f"- {t}: {lst} | {maker} | \"{line}\"")

    print_alerts(terms, year)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
