"""Loading identity must not depend on renaming canonical model.json files."""
import json
from pathlib import Path
import sys

import numpy as np
import pandas as pd
import pytest

ENGINE = Path(__file__).resolve().parents[1]
PROJECT = ENGINE.parents[2]
sys.path.insert(0, str(ENGINE))
from ModelData import ModelData

TOY = PROJECT / "common_reference_data/ecobase_library/ToyModels/900_900_Multi_DET_Toy_(2026).json"


def write_model(tmp_path, relative_path, metadata=None):
    data = json.loads(TOY.read_text(encoding="utf-8"))
    if metadata:
        data.update(metadata)
    path = tmp_path / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data), encoding="utf-8")
    return str(path)


def test_canonical_parent_preserves_legacy_identity_and_ecological_data(tmp_path):
    legacy = ModelData(str(TOY))
    canonical = ModelData(write_model(tmp_path, "900_900_Multi_DET_Toy_(2026)/model.json"))
    assert (canonical.model_number, canonical.model_name, canonical.model_year) == (900, "Multi_DET_Toy", "2026")
    for attribute in ("groups_data", "DC", "det_fate"):
        pd.testing.assert_frame_equal(getattr(canonical, attribute), getattr(legacy, attribute))
    assert canonical.seq2name == legacy.seq2name


@pytest.mark.parametrize("relative_path,expected", [
    ("36_1_South_China_Sea_(2000s)/model.json", (1, "South_China_Sea", "2000s")),
    ("27_118_Northwest_Africa_(1987)_1883ddd3/model.json", (118, "Northwest_Africa", "1987")),
    ("regions/LME_022/models/22_20251890_East_Coast_of_Scotland_(1890-1895)/converter_normalized_diagnostics/model.json", (20251890, "East_Coast_of_Scotland", "1890-1895")),
])
def test_canonical_folder_layouts(tmp_path, relative_path, expected):
    model = ModelData(write_model(tmp_path, relative_path))
    assert (model.model_number, model.model_name, model.model_year) == expected


@pytest.mark.parametrize("section", ["metadata", "extraction_metadata", "source_metadata"])
def test_explicit_metadata_without_legacy_filename(tmp_path, section):
    model = ModelData(write_model(tmp_path, "export.json", {
        section: {"model_number": "HS_077_1", "model_name": "Eastern tropical Pacific", "model_year": "1993-1997"}
    }))
    assert (model.model_number, model.model_name, model.model_year) == ("HS_077_1", "Eastern tropical Pacific", "1993-1997")


@pytest.mark.parametrize("label,metadata,year", [
    ("CAL-2016_California_Current_2000-2014", {"source_metadata": {"model_id": "CAL-2016_California_Current_2000-2014", "period": "2000-2014"}}, "2000-2014"),
    ("Piroddi_2022_Mediterranean_1995", {"source_metadata": {"baseline_year": 1995}}, "1995"),
    ("PAT2024_FalklandShelf_2020_native", None, "2020"),
    ("Bacalso2026_Visayan_Sea_1997_baseline", None, "1997"),
    ("36_South_China_Sea_SCS-2007_Northern_South_China_Sea_(1970s)", None, "1970s"),
])
def test_non_numeric_layouts_preserve_period_without_inventing_number(tmp_path, label, metadata, year):
    model = ModelData(write_model(tmp_path, label + "/model.json", metadata))
    assert model.model_year == year
    if metadata and metadata.get("source_metadata", {}).get("model_id"):
        assert model.model_number == label
    else:
        assert np.isnan(model.model_number)
    assert model.model_name != "model"


def test_unknown_period_stays_unknown(tmp_path):
    model = ModelData(write_model(tmp_path, "unlabelled/model.json"))
    assert np.isnan(model.model_year)
    assert np.isnan(model.model_number)
    assert model.model_name == "unlabelled"


@pytest.mark.parametrize("overrides,expected", [
    ({"model_name": "Custom name", "model_year": "1995-1998"}, ("Custom name", "1995-1998")),
    ({"model_name": "Custom name"}, ("Custom name", "2026")),
    ({"model_year": 2001}, ("Multi_DET_Toy", "2001")),
])
def test_explicit_identity_parameters_override_inferred_fields(overrides, expected):
    model = ModelData(str(TOY), **overrides)
    assert (model.model_name, model.model_year) == expected
    assert model.model_number == 900


def test_explicit_identity_parameters_support_unlabelled_json(tmp_path):
    model = ModelData(write_model(tmp_path, "unlabelled/model.json"),
                      model_name="Northern South China Sea", model_year="2000s")
    assert (model.model_name, model.model_year) == ("Northern South China Sea", "2000s")
    assert np.isnan(model.model_number)


def test_legacy_filename_identity_takes_precedence(tmp_path):
    model = ModelData(write_model(tmp_path, "13_10013_Humboldt_Current_(1980).json", {
        "metadata": {"model_number": "different", "model_name": "different", "model_year": 2000}
    }))
    assert (model.model_number, model.model_name, model.model_year) == (10013, "Humboldt_Current", "1980")


def test_metadata_only_extraction_is_not_an_ecopath_model(tmp_path):
    path = tmp_path / "model.json"
    path.write_text(json.dumps({"metadata": {"model_name": "Extraction"}, "tables": {}}), encoding="utf-8")
    with pytest.raises(ValueError, match="group"):
        ModelData(str(path))


@pytest.mark.parametrize("path", sorted((PROJECT / "regions").glob("*/models/*/model.json")), ids=lambda p: p.parent.name)
def test_all_canonical_regional_models_load(path):
    model = ModelData(str(path))
    assert len(model.groups_data) == len(model.data_json["group"]) + 1
    assert model.DC.shape == (len(model.groups_data), len(model.groups_data))
    assert model.model_name and model.model_name != "model"
