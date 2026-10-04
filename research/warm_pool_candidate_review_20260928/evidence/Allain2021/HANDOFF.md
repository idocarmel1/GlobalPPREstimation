# Allain 2021 source retrieval handoff

2026-09-28. Remaining work transferred to the new end-to-end Pacific papers coordinator. No model extraction, diagnostics, central workbook, or regional workbook writes performed for this paper.

## Verified official metadata

- Title: Tuna fisheries bycatch and climate change in the western tropical Pacific Ocean.
- Authors from indexed official PDF cover: Allain, V.; Griffiths, S.; MacDonald, J.; Wabnitz, C.; Pilling, G.M.; Nicol, S.
- Symbol: SC17-EB-IP-11 / WCPFC-SC17-2021/EB-IP-11.
- Issue date: 5 July 2021.
- Meeting: Scientific Committee seventeenth regular session, electronic meeting, 11–19 August 2021.
- Official landing page: https://meetings.wcpfc.int/node/12403
- Landing page lists one PDF, 4.55 MB; no supplement/native model link is listed there.
- Official download: https://meetings.wcpfc.int/file/8826/download
- PDF viewer exposes underlying file: https://meetings.wcpfc.int/system/files/2021-07/SC17-EB-IP-11%20Tuna%20fisheries%20bycatch%20and%20climate%20change%20in%20the%20western%20tropical%20Pacific%20Ocean%20.pdf
- A later primary IATTC review bibliography cites this as four pages: https://www.iattc.org/GetAttachment/db9854d6-aadb-4b81-8a61-f06aa94dd0d8/WGEB-02-02_Review-of-T-RFMO-Ecosystem-research-to-inform-a-workplan-on-EcoCards-for-the-EPO.pdf . Page count has not yet been independently verified from the PDF bytes.

## Retrieval status and limits

The official metadata page and its viewer link were read successfully through web tools. Repeated official PDF web opens returned timeout, while opening the underlying URL returned inaccessible. Three Python requests (official endpoint, underlying URL, and trust_env=False) using default Python remained pending beyond expected timeouts; a fourth using explicit Python311 printed 'requests ready' then also remained pending. All four owned retrieval sessions were interrupted cleanly before handoff. No successful PDF bytes were saved; therefore no source hash, page text, spatial bounds, baseline, group count, or input completeness has been verified. No full parameter extraction can yet be claimed. This is a retrieval blocker, not proof that model inputs are absent from the source.

Do not import the 2015 or 2019 model as the 2021 model without explicit source evidence. The parent is handling geographic assignment; leave this paper staged until the actual domain is verified. For eventual supported inputs, requested diagnostics are direct PPRCalculator.diagnose_sppr(short=False, flat=False) for GE, TE, With Egestion only. No global option and no production selection.
