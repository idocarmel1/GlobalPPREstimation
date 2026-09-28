# Expanded LME literature and file retrieval

Completed 4 September 2026. Counts describe verified files physically present in this delivery.

The exact workbook selection remains 167 ecosystems: 66 LMEs, 84 EEZs and 17 High Seas regions. The expanded LME pass added **60 distinct sources**, bringing the catalog to **155 sources** and **192 regional assignments**. The EEZ search and the original map design are retained.

## Actual retrieval results

The archive contains **150 unique verified PDFs** and **87 other verified files**. This is an increase of **172 unique files** over the previous delivery: **170 recovered from the public web** and **2 supplied by the user**. PDFs include articles, report volumes, theses, and supplementary PDFs; these are file counts, not publication counts.

Of the 60 added sources, 54 have a verified main PDF and 55 have at least one verified file. A main PDF may be an explicitly labeled manuscript or report version. Across all sources, 735 real retrieval attempts are recorded. Search queries and metadata-only API lookups are separate from download attempts.

All 317 article-folder file copies sit directly beside their article metadata under archive/regions/<ecosystem>/<article>/. The same source may appear in more than one ecosystem. Canonical copies are also retained in archive/files/. Every copy is checked against its SHA-256 hash. Short filenames keep current absolute delivery paths below the traditional Windows limit.

## What the stronger search recovered

- Southern North Sea native EwE databases and supporting CSV/R files in the Pint 2024 public model archive. Database presence is verified; successful import is not claimed.
- Red Sea, Iceland, Beaufort, Chukchi and Antarctic technical reports or theses with detailed parameterization.
- Whole Bay of Bengal technical documentation and the separate, verified Karim 2018 Bangladesh paper. The unresolved legacy BOB-2019 citation is not silently treated as that paper.
- Further Arabian Sea and South China Sea papers, including accessible publisher supplements.
- The 17-page Bacalso 2026 Visayan Sea article and its 26-page supplementary PDF, downloaded separately from the institutional repository and publisher.
- Exact-DOI supplements, spreadsheets, data tables and figures. The 36 TIFF figures are counted as supporting files, not as papers.

## Supplied examples and evidence corrections

The supplied Cheung 2007 thesis (369 pages) and CMFRI Bulletin 51 (151 pages) were incorporated as user-supplied files, not claimed as web downloads. Their basic input and numerical diet tables were inspected, and documentation assessments updated with page references. The Karnataka bulletin is dated 2008; its historical ARAB-2005 identifier remains for continuity. Neither study is treated as covering its entire LME. Unsupported approximate footprints were removed.

Other identity reviews distinguish exact articles from chapters inside report volumes, related theses, and dataset guides. No model was loaded into Ecopath during this work. Format validation, paper identity, input-table completeness and successful model loading remain distinct evidence levels.

## Remaining main-text gaps

**45 of the 155 cataloged sources still lack a verified main file**, including 6 of the newly added sources. Some have verified supplements or related model material. See [unretrieved_main_sources.csv](../data/unretrieved_main_sources.csv) for the complete list.

| Newly added source still missing its main text | Actual retrieval attempts | Outcome |
|---|---:|---|
| LME007-Buchheister-2017 | 2 | University HTTP/HTTPS routes timed out; exact report-title, funder and alternate-copy searches did not yield a file. |
| LME031-Wabnitz-2020 | 9 | Report, institutional and alternate-copy routes did not yield a verified file. |
| LME036-DeepSeep-2020 | 6 | Publisher/API, author and repository routes did not yield a verified PDF. |
| LME037-Bacalso-2014 | 5 | DOI, publisher PDF/API and ResearchGate attempts failed; author institution explicitly lists no full text. The 2016 and 2026 papers are separate sources. |
| LME047-Cheng-2009 | 8 | Publisher/API, author repositories, grant-report route, public archives and EcoBase checked; no verified PDF. |
| LME047-Li-2012 | 11 | Publisher and alternate routes returned landing/error pages. The publisher DOC supplement was recovered. |

A failed route does not prove a file is unavailable everywhere. Search-result snippets and working landing pages never count as downloaded PDFs. No paywall, login barrier or access restriction was bypassed.

## Audit files

- [Download attempts](../data/download_attempts.csv): requested URL, status, outcome and failure detail.
- [Files in article folders](../data/article_files.csv): paths, source URLs and hashes.
- [LME searches](../data/lme_searches.csv) and [EEZ searches](../data/eez_searches.csv).
- [Validation](../data/validation.json) and [summary counts](../data/lme_expansion_summary.json).
- research/lme_*.json: source descriptions, identity reviews and table/page audits.

The search is substantially expanded but is not an exhaustive bibliography of every Ecopath publication. Model extent and geographic applicability still require review before quantitative coverage analysis.
