# Finding missing model data online

Use this reference when the local source bundle lacks diets, parameters, taxonomy, fleet catches, routing, a native model, or a compatible model version. Source discovery is part of extraction: do not stop at a missing local attachment when authorized online research can resolve it. Preserve useful extraction work while searching.

## Search in evidence order

1. Identify the exact article from its title page, authors and DOI. Record publication year, baseline year, survey period and simulation interval separately. A folder name or repository filename is not authoritative.
2. Inventory all local PDFs, Word/Excel files, ZIP contents and native EwE databases first. Determine the exact missing table/field and model version before searching. Compare main-paper and supplement descriptions; an attachment may contain several initial, final or dynamic states.
3. Browse the publisher article and supporting-information pages. Inspect accessible article XML, attachment metadata and links. Search the exact DOI/title with the missing item, such as "diet matrix", "supplement", "supporting information", "Ecopath", "model data" or the attachment filename.
4. Check the publisher's official data repository/API and linked deposits, such as Figshare, Zenodo or an institutional archive. Search the exact parent DOI and verify the returned article/attachment relationship. For a Figshare deposit, the public API can expose files omitted by the publisher's attachment interface; use documented repository endpoints and metadata, not guessed download identities.
5. Check the authors' public repositories, theses, accepted manuscripts and cited model reports. Follow explicitly cited predecessor models when diets or parameters were inherited. A matching region or group count alone does not establish compatibility.
6. Search EcoBase or a native model deposit where relevant. Treat the retrieved model as a separate numerical variant until groups, parameters, diet, catches, period and units have been compared with the article. Record accession and version.

Use legitimate public or already-authorized access. Do not bypass access controls, purchase access or contact authors without authorization. A failed publisher request is not evidence that the data do not exist anywhere. Distinguish "not found after these searches", "identified but inaccessible", "downloaded but incomplete" and "downloaded and verified".

## Verify before using

- Validate file type, nonzero byte count, complete page/table coverage, title and attachment identity. A saved HTML challenge page is not a PDF. For partial/range retrieval, verify range coverage, total length and final document integrity; do not call partial text an archived original.
- Retain source URL, repository record, access date, original filename, SHA-256 and any publisher checksum. Keep original bytes under the paper folder; record missing or failed retrievals separately. Recovered attachments need their own provenance.
- Preserve table geometry. Flattened web text that drops blank cells cannot determine diet predator/prey positions or fleet assignments. Verify against the original spreadsheet, Word structure or rendered pages before transcription.
- To reuse predecessor inputs, require explicit lineage plus a group/parameter crosswalk and a check of period, area basis, diets, catches and stage structure. Demonstrate habitat-area conversions and avoid applying them twice. Preserve conflicting statements.
- A dynamic endpoint table is not a complete Ecopath model. Require matching realized diets/flows, BA and sufficiently precise state inputs. Do not silently reuse baseline diets when endpoint trophic levels or structure differ.
- Reopen the relevant blocked stage when new supplements arrive. Keep earlier search reports as dated history and point to the current evidence; do not overwrite historical conclusions as if the source had always been available.

## Search stop and handoff

Use a bounded search: after publisher attachments, official repositories, author/institutional sources and explicit predecessors have been checked, record the queries, sources, outcomes and exact missing inputs. Do not repeatedly retry the same access failure without a new route. Continue source-faithful extraction where possible, and issue NOT_RUN for calculations whose prerequisites remain absent. Ask the user only for a decision that actually blocks the next step, such as whether to obtain an author export or authorize a stated assumption variant.

Never fill a missing diet, fate matrix, catch, biomass or year-specific version merely to finish the pipeline. A budget residual is not recovered source data. Describe a proposed correction or pooling experiment separately, preserving any authorization already given in the conversation.
