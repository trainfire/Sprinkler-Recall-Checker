# Changelog

## 1.4.0 - 2026-10-18
- Added `references/counterfeit-alerts.json`: 44 UL and FM Approvals alerts (38 counterfeit or unauthorized-mark product alerts, 6 falsified certificates or registrations), 2007-2026. Each original was downloaded and read on 2026-10-18. Records hold literal markings, issuer-stated external cues (one is enough for a suspect finding), supporting cues (lead only), removed-unit cues, stated non-discriminators, dated issuer statements with their strength, and links. No UL or FM files or images are bundled.
- New Alert line in the output template (suspect counterfeit features, counterfeit alert lead, certificate alert). Alerts never change the recall Result line, and a designation match alone stays silent.
- `scripts/lookup.py` adds a fourth section for alerts: full detail on a designation match, one pointer line per distinctive marking or bulb match (Job F5, YD05, ATOP5 and others; agency marks, years, K-factors and normal temperature pairs are ignored), record ids for brand-only input, and the FM NoC 1164 GL5651 date rule. Recall, Tyco index and O-ring output unchanged except that the no-match line now points to SKILL.md step 5 (the web check).
- Identification rules: new counterfeit and certification section (external cues only on installed units, literal markings, dated FM statements on O-ring seals and Job F5/YDϕ5 bulbs, certificate alerts, certification databases).
- Web budget: one fetch of an alert link for photo comparison; one extra UL/FM search in a no-recall check only when a counterfeit check applies.
- Sources: UL Public Notices, FM Product Alerts, UL Product iQ, FM Approval Guide and NFPA 25 page added; O-ring list provenance updated (UL-hosted copy, byte-identical); quick-check routing row for counterfeit checks; known gaps listed (UL 18PN-07, UL 15PN-21, FM GN5651 2006, pre-2018 UL notices). Em dashes removed from sources.md.
- Rechecked 2026-10-18: CPSC search (no new fire sprinkler recalls), CPSC 26-800, Tyco page, Reliable, Viking, Victaulic and NFSA pages. Notice summary for 26-800 adds the Fall River fire it cites.
- Added 18 screening scenarios (50 total). Disclaimer, notices, manifests, README and Codex prompt updated.

## 1.3.0 - 2026-10-14
- Bundled-first workflow: positive, potential and undetermined results no longer browse; a no-recall result needs at most two quick searches (CPSC site search plus current manufacturer source).
- Added `scripts/lookup.py` for offline lookup across the recall register, Tyco model index (seal styles, figure pages) and 2009 O-ring list, with a manufacture-year check.
- Added O-ring risk flag: O-ring construction plus visible corrosion at the seal area is flagged as the recall failure mechanism even when the model has no recall.
- Shorter output template (about 100 words), merged Source and Checked lines.
- Added rules for unopened photos, brand-only markings, removed or spare heads, mirror-reversed stamps, catalog images and uncertain 1998 boundary years.
- CPSC 03-116 (AHI) and 03-117 (SCM) full pages opened 2026-10-14; indexed-text limitation removed. Added current manufacturer source map.
- Added six screening scenarios (32 total).

## 1.2.0 - 2026-10-14
- Packaged for Claude and Codex: added `.claude-plugin/plugin.json`; kept Codex manifest and `agents/openai.yaml` unchanged in function.
- Added disclaimer and limitation of liability (DISCLAIMER.md), summarized in SKILL.md, plugin descriptions and README.
- Added a one-line screening note to the end of every result.
- Added MIT license for original content and NOTICE.md listing third-party files with owners and public sources.
- Added SKILL.md frontmatter fields: license, compatibility (web access requirement), metadata (author, version).
- Added README with install steps and package layout.
- No changes to recall records, identification rules, model index or bundled third-party files.

## 1.1.1 - 2026-10-13
- Added archived sprinklerreplacement.com provenance and six verified category-download crosswalks.
- Confirmed attached complete brochure matches existing text and all 27 rendered pages; retained canonical PDF without duplication.
- Added temperature-color/component/weep-hole cues and illustrated Gem/Star inscriptions to direct lookup references.
- Added source-specific pagination and guards against interpreting archive dates, subset omissions or old claim instructions as current recall evidence.
- No new recall populations or additional model rows found.

## 1.1.0 - 2026-10-13
- Added six omitted Central wet model names, completing the 48-name CPSC wet table.
- Added notice dates, hazards, program status/deadlines, updated related notices and explicit retrieval provenance to all nine population records.
- Added 76-row Tyco model/variant/figure/seal index and searchable extracts of existing bundled PDFs.
- Added factual notice summaries, Star date routing, replacement-guide context and expanded source/subpage directory.
- Added focused browsing workflow using bundled references first, retaining current verification and negative-clearance safeguards.
- Added 20 screening boundary scenarios; package checks cover data consistency and preserved assets, not end-to-end model behavior.
- Migrated to a portable root manifest while preserving the compatibility manifest, plugin identity, author, all three starter prompts, capabilities and original assets.
