# Source retrieval audit — 28 September 2026

The successful files are identified by SHA-256 and size in each regional paper's metadata.json. Incomplete earlier transfers remain staging artifacts and were not admitted as source PDFs. Main files were retrieved with bounded HTTP byte ranges, verified against Content-Range, assembled, parsed with Poppler, and checked against their titles. Each successful chunk's response headers remain in the staging download directories.

## Griffiths2019

- Main journal PDF: 19 pages, 2,084,098 bytes, SHA-256 `a9c407e6387799a4afa4a0b6a9f275d21ed49cdfd03c1ea4c77fdcf7d38a3456`. Retrieved from the BMIS author-paper attachment. Main Table1 on PDF pp5–6 inspected visually and extracted by word coordinates.
- Publisher DOI and supporting information listing identify `fog12389-sup-0001-AppendixS1-S4.docx` (3.9 MB).
- Publisher `action/downloadSupplement?doi=10.1111%2Ffog.12389&file=fog12389-sup-0001-AppendixS1-S4.docx` and `/doi/suppl/10.1111/fog.12389/supinfo/fog12389-sup-0001-appendixs1-s4.docx` requests returned HTTP403/challenge HTML. No usable DOCX bytes.
- Author-uploaded ResearchGate 68-page Appendix PDF is readable by the web text parser. Direct download URLs, including the data and links forms, returned HTTP403. The web parse confirms final TableS3 and catch TableS4, but runs blank table cells together and cannot identify predator/fleet columns reliably. These numbers were not assigned by guessing column positions. TableS2 is the initial diet, not the final model.
- The author-upload PDF: https://www.researchgate.net/profile/Shane-Griffiths/publication/325700136_Griffiths_FOG-17-1431_Early_View_Supp_Info/data/5b9feef0299bf13e6038a3f9/Warm-Pool-Ecopath-FAD-Griffiths-et-al-2018-APPENDICES.pdf
- Figshare public API lookup by exact DOI returned an empty article list. Exact DOI/filename/title searches found the publisher and author upload but no independently downloadable supplement.
- Zotero connector located the main article and its main PDF attachment; no supplement was identified. No Zotero library changes were made.
- No browser was available in this environment to inspect the publisher challenge interactively. No author contact was sent.

## Allain2021

- Official page https://meetings.wcpfc.int/node/12403 links one 4.55MB report. The exact download https://meetings.wcpfc.int/file/8826/download was successfully obtained: 4 pages, 4,769,209 bytes, SHA-256 `5cf178ced34dfd5d5d7377fa99453c953839f09d5611e8bd771be89f531dd31c`. Earlier streaming timeouts are superseded by this successful complete source.
- Read all four pages and visually inspected the map and Methods pages. This is a cover plus a three-page results leaflet, not a 65-group numerical appendix. No supplementary link appears on the official listing.
- Cited primary report https://meetings.wcpfc.int/node/11742 / https://meetings.wcpfc.int/file/7748/download (EcoSEA2020) downloaded and parsed: 24 PDF pages, 582,847 bytes. Section5 gives model-development context; its annexes are workshop participants, agenda and questionnaire. It does not give the final 65-group balanced numerical inputs.
- Focused searches of the paper title, 65-group model, SPC/IATTC and EcoSEA found no final native model or table supplement. This is a statement about this search, not proof that no such source exists.
- EcoBase's public catalog was inspected for Griffiths, Allain and Western Tropical Pacific. The Western Tropical Pacific entry is Godinot and Allain2003, model period1990–2001; the Griffiths2010 entry is eastern Australia. Neither establishes equivalence to the requested 2019 or 2021 model. Neither was substituted.

No model admission failure was inferred from a download timeout. Griffiths has a known but inaccessible coordinate-preserving supplement; Allain's complete retrieved publication does not print the required input set. The next sources needed are stated separately in each SOURCE_ADMISSION.md.
