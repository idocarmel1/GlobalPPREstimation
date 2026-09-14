import json
import zipfile

import ppr_pipeline.download as download_module
from ppr_pipeline.download import (
    catch_url,
    download_unit_inputs,
    exploited_url,
    load_units_from_spatial_index,
    regions_url,
)


BASE = "https://api.seaaroundus.org/api/v1"


def test_catch_url_matches_sea_around_us_csv_endpoint():
    assert catch_url(BASE, "lme", 13) == (
        "https://api.seaaroundus.org/api/v1/lme/tonnage/taxon/"
        "?format=csv&limit=10&sciname=false&region_id=13"
    )


def test_exploited_url_matches_region_endpoint():
    assert exploited_url(BASE, "highseas", 71) == (
        "https://api.seaaroundus.org/api/v1/highseas/exploited-organisms/"
        "?region_id=71"
    )


def test_regions_urls_distinguish_spatial_from_nonspatial():
    assert regions_url(BASE, "lme", spatial=False) == (
        "https://api.seaaroundus.org/api/v1/lme/?nospatial=true"
    )
    assert regions_url(BASE, "highseas", spatial=True) == (
        "https://api.seaaroundus.org/api/v1/highseas/"
    )


def test_load_units_from_spatial_index_includes_lmes_and_high_seas(tmp_path):
    index = tmp_path / "spatial_units.csv"
    index.write_text(
        "unit_id,name,type,sau_region,sau_region_id,is_pilot\n"
        "LME_001,East Bering Sea,LME,lme,1,True\n"
        'HS_071,"Pacific, Western Central",High Seas,highseas,71,True\n',
        encoding="utf-8-sig",
    )
    units = load_units_from_spatial_index(index)
    assert units == [
        {
            "unit_id": "LME_001",
            "name": "East Bering Sea",
            "sau_region": "lme",
            "sau_region_id": 1,
        },
        {
            "unit_id": "HS_071",
            "name": "Pacific, Western Central",
            "sau_region": "highseas",
            "sau_region_id": 71,
        },
    ]


def test_download_unit_inputs_uses_stable_unit_filenames(tmp_path, monkeypatch):
    def fake_download(session, url, destination, *, overwrite):
        if destination.suffix == ".zip":
            with zipfile.ZipFile(destination, "w") as zf:
                zf.writestr("catch.csv", "year,tonnes\n2019,1\n")
        else:
            destination.write_text(json.dumps({"data": []}), encoding="utf-8")
        return True

    monkeypatch.setattr(download_module, "_download", fake_download)
    outputs = download_unit_inputs(
        [{"unit_id": "LME_001", "sau_region": "lme", "sau_region_id": 1, "name": "East Bering Sea"}],
        BASE,
        tmp_path,
    )
    assert [path.name for path in outputs] == ["LME_001-catch.zip", "LME_001-exploited.json"]
    assert zipfile.is_zipfile(outputs[0])
