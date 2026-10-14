"""Copy exact key-run source bytes into regional paper/model source packages.

This operation does not extract model parameters, write a canonical model.json,
register Project.xlsx records, change selections, or publish the map.
"""
from pathlib import Path
import csv
import hashlib
import io
import json
import shutil
import zipfile

ROOT = Path(__file__).resolve().parents[4]
STUDY = ROOT / "research/agents/ewe_key_run_inventory_20261014"
DATE = "2026-10-14"


def digest(data):
    return hashlib.sha256(data).hexdigest()


def save_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def exact_write(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and path.read_bytes() != data:
        raise RuntimeError(f"Refusing to overwrite different existing bytes: {path}")
    if not path.exists():
        path.write_bytes(data)
    assert path.read_bytes() == data


PACKAGES = [
    dict(unit="LME_022", region="North Sea", paper="ICES-WGSAM-2015",
         model="ICES_WGSAM2015_North_Sea_1991", year=2016, run_year=2015,
         title="Report of the Working Group on Multispecies Assessment Methods (WGSAM), 9–13 November 2015",
         doi=None, url="https://www.ices.dk/community/groups/Pages/WGSAM.aspx",
         period="1991–2013", groups=69, footprint="ICES divisions IVa, IVb and IVc",
         report="ICES_WGSAM_2015.pdf", annex="Annex 6, printed pp. 102–206; accepted native database listed on pp. 172 and 196",
         archive="EwE-NS_KeyRun 2015 Outputs.zip", port="NorthSeaModel",
         related=["Mackinson_2018_North_Sea_plan.pdf"],
         database="Keyrun 2015_NorthSea1991_12Jan16.eweaccdb",
         coverage="whole North Sea model footprint; exact overlap with LME boundary not measured"),
    dict(unit="LME_023", region="Baltic Sea", paper="ICES-WGSAM-2016",
         model="ICES_WGSAM2016_Baltic_Proper_2004", year=2017, run_year=2016,
         title="Report of the Working Group on Multispecies Assessment Methods (WGSAM), 10–14 October 2016",
         doi="10.17895/ices.pub.8534", url="https://doi.org/10.17895/ices.pub.8534",
         period="2004–2013", groups=22, footprint="Baltic Proper, approximately ICES subdivisions 25–29 excluding 28-1 (Gulf of Riga)",
         report="ICES_WGSAM_2016.pdf", annex="Annex 3, printed pp. 46–94; native database identity on printed p. 83",
         archive="EwE_BS_KeyRun 2016 Outputs.zip", port="BalticSeaModel",
         related=["Bauer_2019_future_Baltic_Sea.pdf"],
         database="Baltic2004_keyrun65.eweaccdb",
         coverage="subregional Baltic Proper model; not the whole Baltic LME; overlap not measured"),
    dict(unit="LME_024", region="Celtic-Biscay Shelf", paper="ICES-WGSAM-2019-Irish-Sea",
         model="ICES_WGSAM2019_Irish_Sea_1973", year=2019, run_year=2019,
         title="Working Group on Multispecies Assessment Methods (WGSAM)",
         doi="10.17895/ices.pub.5758", url="https://doi.org/10.17895/ices.pub.5758",
         period="1973–2016", groups=41, footprint="Irish Sea, ICES division VIIa / 7.a",
         report="ICES_WGSAM_2019.pdf", annex="Section 2.2, printed p. 13 approval; Annex 3, printed pp. 37–109 documentation",
         archive=None, port=None,
         related=["IrishSea_key_run_technical_report_2019.pdf", "Bentley_2021_refining_fisheries_advice.pdf"],
         database=None,
         coverage="Irish Sea subregion within Celtic-Biscay Shelf; not a whole-LME model; overlap not measured"),
]


def main():
    source_manifest_path = STUDY / "evidence/source_manifest.json"
    manifest = json.loads(source_manifest_path.read_text(encoding="utf-8"))
    sources = {Path(x["path"]).name: x for x in manifest["source_files"]}
    retrieval = json.loads((STUDY / "evidence/related_paper_retrieval_20261014.json").read_text(encoding="utf-8"))
    for item in retrieval:
        if item["status"] != "downloaded":
            continue
        path = STUDY / "inputs" / item["name"]
        data = path.read_bytes()
        assert data.startswith(b"%PDF")
        sources[item["name"]] = dict(path="inputs/" + item["name"], role="related_journal_paper",
            download_url=item["url"], retrieved_date=DATE, bytes=len(data), sha256=digest(data))
    manifest["source_files"] = list(sources.values())
    save_json(source_manifest_path, manifest)

    role_path = ROOT / "common_reference_data/provenance/paper_file_roles.json"
    roles = json.loads(role_path.read_text(encoding="utf-8"))
    role_keys = {(x["path"], x["sha256"]) for x in roles["files"]}
    packages = []
    csv_inspection = []
    for cfg in PACKAGES:
        paper = ROOT / "regions/LME" / cfg["unit"] / "papers" / cfg["paper"]
        model = paper / "models" / cfg["model"]
        if (model / "model.json").exists():
            raise RuntimeError("Source preparation must not overwrite a canonical model")
        entries = []

        def copy_source(name, destination, role):
            src = sources[name]
            data = (STUDY / src["path"]).read_bytes()
            assert digest(data) == src["sha256"], name
            exact_write(destination, data)
            row = dict(path=destination.relative_to(paper).as_posix(), role=role,
                       bytes=len(data), sha256=digest(data), source_url=src["download_url"],
                       research_source=(STUDY / src["path"]).relative_to(ROOT).as_posix(),
                       verification="exact source bytes preserved", numerical_use="not used in project calculations")
            entries.append(row)
            if role in ("context", "published_rpath_port", "published_rpath_configuration"):
                key = (destination.relative_to(ROOT).as_posix(), row["sha256"])
                if key not in role_keys:
                    roles["files"].append(dict(path=key[0], sha256=key[1], role="context",
                        file_label=name, evidence="Related publication or Rpath port; not the reviewed native EwE database. Paper-local source_manifest.json records exact identity and role."))
                    role_keys.add(key)
            return row

        copy_source(cfg["report"], paper / "sources" / cfg["report"], "main_review_report")
        for name in cfg["related"]:
            copy_source(name, paper / "sources/context" / name, "context")
        native = []
        if cfg["port"]:
            for suffix, role in [(".RData", "published_rpath_port"), ("_config.R", "published_rpath_configuration")]:
                name = cfg["port"] + suffix
                row = copy_source(name, model / "inputs/native/rpath_port" / name, role)
                native.append(row)
        csv_count = 0
        xlsx_count = 0
        if cfg["archive"]:
            copy_source(cfg["archive"], paper / "sources/supplements" / cfg["archive"], "official_key_run_output_archive")
            archive_path = STUDY / sources[cfg["archive"]]["path"]
            with zipfile.ZipFile(archive_path) as archive:
                assert archive.testzip() is None
                for info in archive.infolist():
                    if info.is_dir():
                        continue
                    relative = Path(info.filename)
                    if relative.is_absolute() or ".." in relative.parts:
                        raise RuntimeError("Unsafe archive member")
                    destination = paper / "sources/supplements/key_run_outputs" / relative
                    data = archive.read(info)
                    exact_write(destination, data)
                    entries.append(dict(path=destination.relative_to(paper).as_posix(), role="official_model_output",
                        bytes=len(data), sha256=digest(data), source_archive=cfg["archive"], archive_member=info.filename,
                        numerical_use="output evidence only; not an Ecopath import or project calculation input"))
                    if relative.suffix.lower() == ".csv":
                        csv_count += 1
                        text = data.decode("utf-8-sig", errors="strict")
                        rows = list(csv.reader(io.StringIO(text)))
                        assert rows, info.filename
                        csv_inspection.append(dict(unit_id=cfg["unit"], path=destination.relative_to(ROOT).as_posix(),
                            rows=len(rows), first_row=rows[0], source_bytes_preserved=True))
                    elif relative.suffix.lower() == ".xlsx":
                        xlsx_count += 1
        metadata = dict(article_id=cfg["paper"] + "__" + cfg["unit"], source_article_id=cfg["paper"],
            unit_id=cfg["unit"], region_name=cfg["region"], authors="ICES", publication_year=cfg["year"],
            title=cfg["title"], doi=cfg["doi"], landing_page=cfg["url"], model_years=cfg["period"],
            functional_groups=cfg["groups"], key_run_year=cfg["run_year"], modeled_footprint=cfg["footprint"],
            coverage_note=cfg["coverage"], target_coverage_ratio=None,
            extraction_readiness="source package prepared; canonical model extraction not performed",
            model_file_status="accepted native EwE database not obtained",
            proposed_model_id=cfg["model"], central_registration_status="not applied; stop before map requested",
            main_file_status="verified full PDF bytes", related_material_role="contextual, not automatically identical parameterization",
            source_locators=cfg["annex"])
        save_json(paper / "sources/metadata.json", metadata)
        save_json(paper / "source_manifest.json", dict(schema_version=1, paper_folder_id=cfg["paper"],
            date=DATE, stage="source preparation only", publication=metadata, files=entries,
            missing_material=[dict(role="accepted_native_ewe_database", filename=cfg["database"], availability="missing",
                reason="Not located in public sources; official output archives do not contain a native database")],
            project_numerical_use="none", researcher_approval="not conferred by source acquisition"))
        if native:
            save_json(model / "inputs/provenance.json", dict(schema_version=1, model_id=cfg["model"],
                stage="source preparation only", native_ewe_database_available=False,
                rpath_sources=[dict(path=Path(x["path"]).relative_to(Path("models")/cfg["model"]/"inputs").as_posix(),
                    sha256=x["sha256"], role=x["role"], source_url=x["source_url"]) for x in native],
                equivalence_to_accepted_ewe="not audited", simulations_executed=False))
        model.mkdir(parents=True, exist_ok=True)
        (model / "model_notes.md").write_text(
            f"# {cfg['model']} source package\n\n"
            f"## Source identity\n\nICES WGSAM {cfg['run_year']} key-run documentation; {cfg['annex']}. "
            f"See [source manifest](../../source_manifest.json).\n\n"
            f"## Modeled period and area\n\n{cfg['period']}; {cfg['footprint']}. {cfg['coverage']}.\n\n"
            "## Departures from the publication\n\nNo scientific parameters have been extracted or modified. "
            "The accepted native EwE database is unavailable. "
            + ("The retained Rpath files are published ports in another software framework; identity with the accepted EwE configuration has not been audited.\n\n" if cfg['port'] else "No runnable model file or author input CSV was obtained for this package.\n\n")
            + "## Evidence links\n\n[Regional source package](../../README.md). "
            "No canonical model.json has been created. This folder is not currently a selectable project model, "
            "and does not inherit existing results or researcher approval.\n", encoding="utf-8")
        related_links="\n".join(f"- [{name}](sources/context/{name})" for name in cfg["related"])
        (paper / "README.md").write_text(
            f"# {cfg['footprint']} key-run sources\n\n"
            f"Prepared {DATE}. Key run {cfg['run_year']}; publication {cfg['year']}; modeled period {cfg['period']}; {cfg['groups']} functional groups.\n\n"
            f"[Primary ICES report](sources/{cfg['report']}), {cfg['annex']}.\n\n"
            f"[Model source package](models/{cfg['model']}/model_notes.md). "
            + (f"Published Rpath model and configuration are retained under `models/{cfg['model']}/inputs/native/rpath_port/`. " if cfg["port"] else "The Irish Sea accepted model database has not been obtained. ")
            + "A Rpath port is not the accepted native EwE software configuration.\n\n"
            + (f"The original ICES output ZIP is retained in `sources/supplements/`, with {csv_count} exact CSV files and {xlsx_count} Excel output workbooks unpacked in `sources/supplements/key_run_outputs/`. These are simulation outputs, not model-input import tables.\n\n" if cfg["archive"] else "No official model-input or model-output CSV bundle was located for the Irish Sea; none was invented from unrelated data.\n\n")
            + f"Related publications retained as context:\n\n{related_links}\n\n"
            + "[Metadata](sources/metadata.json) and [source manifest](source_manifest.json) record citations, roles and SHA-256 hashes. "
            + "Source preparation only: Project.xlsx, regional workbook selections, scientific inputs and generated map pages remain unchanged.\n",encoding="utf-8")
        packages.append(dict(unit_id=cfg["unit"], region=cfg["region"], paper_path=paper.relative_to(ROOT).as_posix(),
            proposed_model_id=cfg["model"], source_files=len(entries), csv_files=csv_count, xlsx_files=xlsx_count,
            rpath_files=len(native), canonical_model_available=False, native_ewe_database_available=False,
            researcher_verified_existing_model=False, publication_pending=True))
    save_json(role_path, roles)
    save_json(STUDY / "evidence/region_preparation_inventory.json", dict(date=DATE,
        stage="prepared sources; stopped before canonical extraction, registry, selections or map publication", packages=packages))
    save_json(STUDY / "evidence/regional_csv_inspection.json", csv_inspection)
    print(json.dumps(packages, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
