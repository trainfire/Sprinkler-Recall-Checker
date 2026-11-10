---
name: check-sprinkler-recalls
description: Identify installed or removed fire sprinklers from phone photos, readable markings, sprinkler identification numbers (SINs) or records, check U.S. recalls and replacement warnings, and screen markings against UL and FM Approvals counterfeit and falsified-certificate alerts. Use when a user uploads a sprinkler photo, asks whether a sprinkler is recalled or counterfeit, asks if a UL or FM mark is genuine, requests identification of Central, Omega, Gem, Star, Globe, Tyco, Viking or other sprinklers, asks to distinguish O-ring and Belleville seals, asks about O-ring corrosion risk, or shares a sprinkler certificate. Return a short evidence-based screening result, flag O-ring corrosion risk and counterfeit-alert cues, and request specific missing views without guessing. Informational screening aid only, not an inspection, engineering opinion, product authentication or code compliance determination; see DISCLAIMER.md.
license: MIT for original content; bundled third-party reference files remain the property of their owners (see NOTICE.md)
compatibility: Works offline from bundled references for most results. A no-recall result needs one or two quick web searches (three when a counterfeit check applies); without web access the skill reports Unable to determine instead. Comparing photos with a counterfeit alert uses one fetch of the alert link. Uses Python for the lookup script and PDF page rendering when available.
metadata:
  author: Corey Kinsman
  version: "1.4.0"
---

# Sprinkler Recall Checker

## Disclaimer
This skill is a personal project by Corey Kinsman. It is not affiliated with or endorsed by any employer, sprinkler manufacturer, CPSC, UL, FM Approvals or NFSA. Results are AI-generated informational screening only and may be incomplete or wrong. They are not a fire protection engineering opinion, inspection, testing or maintenance report, code or standard compliance determination, product or certificate authentication, or certification of any sprinkler or system. Provided "as is" without warranty; see [DISCLAIMER.md](DISCLAIMER.md). End every result with the screening note in the template. Do not imply that the author, any employer, any manufacturer or any certification body reviewed a specific result.

## Fast path (bundled first)
The bundled references already hold the researched U.S. recall register, notice summaries, program status, the September 24, 2026 renewed CPSC warning, and 44 UL and FM counterfeit and falsified-certificate alerts. Most screenings need no web access. Work in this order and stop as soon as a conclusion is supported.

1. **Look at every photo.** If a photo will not open, say so and stop with "Unable to determine". Label multiple photos Photo 1, Photo 2. Transcribe only legible characters and use `[?]` for uncertain ones. Check for mirror-reversed text. Read wrench-boss text and bulb markings when legible. Do not infer a year from building age, temperature rating or bulb color, and do not invent a SIN. Do not call a head dry-type from a dry-pipe system, freezer location or a hole in the cap alone; ask for the barrel or records.
2. **Run the lookup** on every legible marking, including bulb text: `python scripts/lookup.py <markings> --year <YYYY>` (example: `python scripts/lookup.py GLOBE GL5651 --year 2024`). It returns matching recall-register records with a year check, Tyco model-index rows with seal styles and figure pages, hits on the 2009 O-ring list, and UL/FM counterfeit or certificate alerts that share a designation or marking. Without Python, read `references/recall-register.json`, search `references/tyco-model-index.json` for the model and search `references/counterfeit-alerts.json`.
3. **Read only what the candidate needs.** Use the matching section of [identification-rules.md](references/identification-rules.md). For Central/Gem/Star rows with a 1998 seal transition, compare the cap against `assets/tyco-seal-comparison-page-9.png` and, if needed, render the figure page the lookup lists from `assets/tyco-identification-guide.pdf`. For an alert hit, compare the photos with the record's `external_cues` and read the "Counterfeit and certification alerts" section of the rules. Use [notice-summaries.md](references/notice-summaries.md) only for wording of scope or program status. Other references (sources, archived brochure facts, replacement context, PDF text extracts) are for unusual cases and maintenance. Phone numbers, compensation offers and maintenance intervals in historical documents are not current advice.
4. **Decide** the recall conclusion and, separately, the Alert line.
5. **Web only when needed:**
   - Recall match, replacement warning, potential match, unable to determine: no browsing. Cite the bundled notice and its verification date. Browse only if the user asks for the latest remedy or contact.
   - Alert line raised: optionally one fetch of the alert's `source_url` to compare its photos with the user's. If it will not open, report the alert from the bundled cues and say the images were not compared.
   - Unknown model or SIN that the bundled files cannot identify: up to two targeted searches for a manufacturer datasheet.
   - **No matching recall:** required quick check of at most two searches: `site:cpsc.gov "<manufacturer> <model or SIN>" sprinkler`, and the current manufacturer source in the "Current manufacturer sources for a quick negative check" table in [sources.md](references/sources.md). Search results with no relevant notice are enough; open a page only for a result that looks relevant. Add a third search, `"<SIN>" sprinkler counterfeit (site:ul.com OR site:fmapprovals.com)`, only when the designation is in `counterfeit-alerts.json`, the unit was bought or installed outside the U.S., or the user raises a certification concern. If search is unavailable, report "Unable to determine: no match in the bundled register; current status not verified."

## Conclusions (recall status)
- **Recall match confirmed:** every criterion in the notice is established (manufacturer, exact model or variant, construction, year, and seal variant where the notice depends on it). A closed program does not clear the head.
- **Replacement warning confirmed:** same standard for a warning; name it as a warning. Example: SCM Star ME-1 dated 1983-1995 (CPSC 03-117).
- **Potential recall/warning match:** a plausible affected family or model with a criterion still missing; name what is missing. Also use when only the brand is legible and one of that brand's records could apply.
- **No matching recall or replacement warning found:** only after sufficient identification and the quick web check in step 5. It is a bounded search result, never proof of safety, authenticity or compliance.
- **Unable to determine:** photo unusable or not opened, manufacturer not established, or the needed check could not run. Never upgrade this to a negative result.

Keep recall status, warnings, counterfeit alerts and advisories distinct. Do not declare a whole brand recalled. O-ring construction, corrosion, obsolescence, an advisory listing or a counterfeit alert alone is not a recall.

## Counterfeit alert line
Recall status and alert status are independent. Report alerts on their own Alert line and never change the Result line because of one. Each alert record separates `external_cues` (issuer-stated differences from authentic units), `supporting_cues` (finish, color, font or identifying-marking observations) and `other_markings` (lookup keys that genuine units can share; a marking counts only when it also appears in a cue list).
- **Suspect counterfeit features:** the unit matches the alert's designation or brand and shows at least one of that alert's `external_cues`, or a cross-alert statement marked external applies (a GL5651 dated 2022 or later marked GLOBE; an ATOP, YD, YH-5 or CDGIX bulb on a Tyco, Globe or FM-marked unit; a Job F5 bulb on a model FM names as using Job G5).
- **Counterfeit alert lead:** the designation or brand matches and (a) only `supporting_cues` are seen, (b) a lead-level statement applies (for example a Job F5 bulb on an FM-marked unit of a model FM does not name), or (c) a provenance detail (a seller, country or project named in an alert, or a non-U.S. purchase) or the user's own authenticity concern applies and no cue can be checked from the photos.
- **Certificate alert:** a shared certificate matches a falsified certificate in the alerts, or the user relies on a certificate alone to prove approval. Route to the FM Approval Guide or UL Product iQ and to the issuer; a sprinkler photo cannot resolve it.
- **No Alert line:** a designation match with no cue, statement, provenance detail or concern; or the alert's external cues are clearly visible and none match. If the user raised the concern, say in Evidence that no listed cue was seen and that authenticity is not established. TY3151, TY5151, GL5651 and similar designations are widely copied and widely genuine.

Lookup hits on a marking only (a bulb or temperature text) are pointers to read that alert; they count only if the marking is one of its cues. Brand-only hits list record ids; read them only when a visible cue or the SIN points to one. Results of the step 5 counterfeit search never create an Alert line by themselves. Never state that a unit is counterfeit or authentic. Name the alert, the cue seen and what would resolve it. Where an alert was found neither confirms nor excludes a unit elsewhere.

## O-ring risk flag
When O-ring construction is indicated (2009 list hit, Tyco table row, literature or user confirmation) and the photo shows corrosion, deposits or contamination at the seal, cap, orifice or frame seat, add the Risk flag line. It states that this matches the failure mechanism in the O-ring recalls (CPSC 01-201: corrosion or contaminants can prevent activation), that this model has no recall, and that a qualified sprinkler professional should evaluate it promptly with replacement the prudent course. The Result line stays accurate. With O-ring construction but no visible corrosion, add a short note in Evidence instead. A counterfeit alert's statement that its counterfeits use O-rings does not establish O-ring construction for the unit in hand. Details are in identification-rules.md.

## Output template
Aim for about 100 words and stay under 170 even with a risk flag or alert; only several units justify more. Skip any line that has nothing to say. Apply the identification rules without explaining them. Do not repeat the full Star year table unless the year is the missing item.

**Result:** [conclusion]: [reason in 12 words or fewer]
**ID:** [manufacturer, model/SIN, orientation, year] ([confirmed / tentative])
**Evidence:** [up to three short items: decisive markings and the deciding fact; mark user-typed text as user-provided]
**Risk flag:** [only when triggered; two sentences]
**Alert:** [only when triggered: alert type, issuer and notice with its link, the cue seen; two sentences]
**Next:** [one or two specific photos, records or actions, one sentence each]
**Source:** [the decisive notice with one link, plus PDF page if used] | [bundled, verified YYYY-MM-DD / live check on today's date]
*AI screening aid only. Verify with a qualified fire sprinkler professional before acting.*

Add a one-line condition note for visible damage, corrosion, paint or loading only when the risk flag does not already cover it.

## Field limits
Do not direct anyone to remove, twist, scrape, clean, press, heat or disassemble an installed sprinkler, element, seal or cover plate. Suggest a safe close-up, maintenance records or a verified matching spare. A head already out of service may be rotated and photographed but not disassembled, and should not be reinstalled. A cover plate alone cannot identify the hidden sprinkler. Counterfeit alerts compare internal parts (seal, button, inlet, threads) and one describes a magnet check; none of these justify removing, opening or touching an installed sprinkler or taking off a concealed cover plate. For a confirmed recall, warning, risk flag or suspect counterfeit, recommend documenting the unit and location and arranging evaluation or replacement through a qualified sprinkler professional; for a suspect counterfeit, also suggest reporting it to the issuing body (UL or FM Approvals) and the named manufacturer, and keeping purchase and distributor records. Do not shut down systems, choose replacements by appearance, promise reimbursement, or expand into an NFPA 25 compliance assessment unless asked.

## Maintenance
The recall register is a researched U.S. starter set, last reviewed 2026-10-14, not every recall worldwide. The counterfeit-alert file holds 44 UL and FM alerts reviewed 2026-10-18 and lists its known gaps. Add or revise records only from opened authoritative sources, keeping scope, exceptions, source and dates, and keeping warnings, recalls and counterfeit alerts separate. `references/screening-checks.json` lists the expected boundary behavior for regression testing.
