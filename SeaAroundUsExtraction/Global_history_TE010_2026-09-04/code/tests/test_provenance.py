from ppr_pipeline.provenance import unit_source_urls


def test_unit_source_urls_cover_catch_and_exploited_inputs():
    units = [
        {
            "unit_id": "LME_001",
            "sau_region": "lme",
            "sau_region_id": 1,
        },
        {
            "unit_id": "HS_071",
            "sau_region": "highseas",
            "sau_region_id": 71,
        },
    ]

    urls = unit_source_urls("https://api.seaaroundus.org/api/v1", units)

    assert set(urls) == {
        "LME_001-catch.zip",
        "LME_001-exploited.json",
        "HS_071-catch.zip",
        "HS_071-exploited.json",
    }
    assert "region_id=1" in urls["LME_001-catch.zip"]
    assert "/highseas/exploited-organisms/" in urls["HS_071-exploited.json"]
