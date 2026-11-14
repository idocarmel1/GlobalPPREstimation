"""Read saved scientific evidence and calculate report-only geographic overlaps."""
from pathlib import Path
import hashlib
import json
import math
from collections import Counter
from datetime import datetime, timezone

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from shapely.geometry import shape, mapping, box
from shapely.geometry.polygon import orient
from shapely.ops import unary_union, transform
from pyproj import Geod, Transformer

ROOT = Path(__file__).resolve().parents[6]
RUN = ROOT / "regions/LME/LME_022/work/2026-11-14_160000_validation"
MODEL = ROOT / "regions/LME/LME_022/papers/ICES-WGSAM-2015/models/ICES_WGSAM2015_North_Sea_1991"
EV = MODEL / "extracted_tables/evidence"
GEO = MODEL / "model_validation/evidence/geography"
NS = ROOT / "regions/LME/LME_022/papers/NS-2025/models/22_20251990_East_Coast_of_Scotland_(1991-1995)"

def read(p):
    return json.loads(p.read_text(encoding="utf-8-sig"))

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def rel(p):
    return p.relative_to(ROOT).as_posix()

geod = Geod(ellps="WGS84")
def area(geom):
    if geom.is_empty:
        return 0.0
    if geom.geom_type == "Polygon":
        return abs(geod.geometry_area_perimeter(orient(geom, 1))[0]) / 1e6
    return sum(area(g) for g in geom.geoms)

def measures(r, s):
    overlap = r.intersection(s)
    a_r, a_s, a_i = area(r), area(s), area(overlap)
    return {"target_area_km2": a_r, "study_area_km2": a_s,
            "intersection_km2": a_i, "A_percent": a_i / a_r * 100,
            "B_percent": a_i / a_s * 100}

GEO.mkdir(parents=True, exist_ok=True)
(RUN / "outputs").mkdir(parents=True, exist_ok=True)
target_path = ROOT / "common_reference_data/geography/boundaries/LMEs.geojson"
land_path = ROOT / "common_reference_data/geography/basemaps/ne_50m_land.geojson"
feature = next(f for f in read(target_path)["features"] if f["properties"]["region_id"] == 22)
r = shape(feature["geometry"])
official = read(GEO / "ices_divisions_IVa_IVb_IVc.geojson")
assert sorted(f["properties"]["Area_Full"] for f in official["features"]) == ["27.4.a", "27.4.b", "27.4.c"]
s = unary_union([shape(f["geometry"]) for f in official["features"]])
assert r.is_valid and s.is_valid
# Clip land before union for a bounded, efficient operation.
frame = box(-9, 49, 16, 64)
land = unary_union([shape(f["geometry"]).intersection(frame) for f in read(land_path)["features"]])
rm, sm = r.difference(land), s.difference(land)
raw, masked = measures(r, s), measures(rm, sm)
(GEO / "target_region.geojson").write_text(json.dumps(feature), encoding="utf-8")
(GEO / "study_area_union.geojson").write_text(json.dumps({"type": "Feature", "properties": {
    "method": "union of official ICES division polygons 27.4.a, 27.4.b, 27.4.c",
    "interpretation": "geographic proxy from the report's declared ICES divisions, not a recovered native model grid"},
    "geometry": mapping(s)}), encoding="utf-8")

projection = Transformer.from_crs("EPSG:4326", "EPSG:3035", always_xy=True).transform
def parts(g):
    return [g] if g.geom_type == "Polygon" else list(g.geoms)

def draw(ax, geom, color, edge="none", alpha=1, lw=0.5):
    for poly in parts(transform(projection, geom).simplify(150)):
        if poly.geom_type != "Polygon":
            continue
        x, y = poly.exterior.xy
        ax.fill(x, y, facecolor=color, edgecolor=edge, alpha=alpha, linewidth=lw)

def setup(ax):
    ax.set_facecolor("#f4f8fb")
    draw(ax, land, "#e7e6df", "#a4a49b", lw=.4)
    bounds = transform(projection, box(-6, 50, 14, 63)).bounds
    ax.set_xlim(bounds[0], bounds[2]); ax.set_ylim(bounds[1], bounds[3])
    ax.set_aspect("equal"); ax.set_axis_off()
    for name, lon, lat in [("Scotland",-4.8,56.5),("England",-3,53),("Norway",8.5,61),
                            ("Denmark",9.3,55.8),("Netherlands",5.5,52),("Skagerrak",9.6,58.1)]:
        x,y=projection(lon,lat);ax.text(x,y,name,fontsize=8,color="#353f44",ha="center")

fig, axes=plt.subplots(1,2,figsize=(10,6.7))
for ax in axes:setup(ax)
draw(axes[0],r,"#74a9cf", "#22567b",.55, .9)
draw(axes[0],land,"#e7e6df","#a4a49b",lw=.4)
axes[0].set_title("Target: North Sea LME (LME_022)",fontsize=12)
draw(axes[1],r,"none","#22567b",1,1.3)
draw(axes[1],s,"#e9a45e","#9b541c",.6,.7)
draw(axes[1],land,"#e7e6df","#a4a49b",lw=.4)
axes[1].set_title("Study proxy: ICES IVa + IVb + IVc",fontsize=12)
for label,lon,lat in [("IVa",1,59.7),("IVb",3,55.7),("IVc",3.8,52.3)]:
    x,y=projection(lon,lat);axes[1].text(x,y,label,fontsize=12,fontweight="bold",color="#723c18")
fig.legend(handles=[Patch(facecolor="#74a9cf",edgecolor="#22567b",label="North Sea LME"),
                    Patch(facecolor="#e9a45e",edgecolor="#9b541c",label="ICES division union")],
           loc="lower center",ncol=2,bbox_to_anchor=(.5,.07),frameon=False)
fig.text(.5,.035,"Geographic reconstruction from declared divisions; not an original article figure.\n"
         "Same European equal-area projection. ICES official boundaries; repository LME and Natural Earth coast.",
         ha="center",fontsize=9)
fig.subplots_adjust(left=.02,right=.98,top=.94,bottom=.16,wspace=.03)
fig.savefig(GEO / "target_and_study_overlap.png",dpi=200,facecolor="white");plt.close(fig)

identities=[]
for p, expected in [(MODEL/"model.json","450e0f43822a34a02d4d26ad71358aeef32af8daaff7fcf07cd95ef2131cf97a"),
                    (MODEL/"inputs/native/rpath_port/NorthSeaModel.RData","661ac1fc2ad94c946561e37e8512560f416906265eb2df36a80ffc61107d87bc"),
                    (MODEL/"inputs/native/rpath_port/NorthSeaModel_config.R","22a88832aa54a72512c1dd5b0a172bc60b9b184f4282e8ad63fa9b28df5ea9c9")]:
    identities.append({"path":rel(p),"sha256":sha(p),"expected_sha256":expected,"match":sha(p)==expected})
assert all(x["match"] for x in identities)
loader=read(EV/"source_load_check.json")
extraction=read(EV/"extraction_check.json")
budget=read(EV/"physical_budget_check.json")
ns_matrices=read(NS/"model_validation/evidence/source_review/matrix_inspection.json")
ns_checks=[]
for method in ns_matrices["methods"]:
    if method["method"] not in ["GE","TE"]:continue
    matrix=method["source_matrix"]
    assert len(matrix["row_ids"])==len(set(matrix["row_ids"]))==len(matrix["values"])
    assert len(matrix["column_ids"])==len(set(matrix["column_ids"]))==3
    negatives=[]; nonfinite=[]
    for i,row in enumerate(matrix["values"]):
        assert len(row)==3
        for j,value in enumerate(row):
            if not math.isfinite(value):nonfinite.append([i,j])
            elif value<0:negatives.append({"source_id":matrix["column_ids"][j],"source_name":matrix["column_names"][j],
                                          "group_id":matrix["row_ids"][i],"group_name":matrix["row_names"][i],"sppr_value":value})
    ns_checks.append({"method":method["method"],"status":method["overall_status"],"checked_entries":78,
                      "negative_pairs":negatives,"negative_source_columns":len(set(v["source_id"] for v in negatives)),
                      "nonfinite":nonfinite,"rho_living":method["rho_living"],"b":method["b"],
                      "detritus_sppr":method["detritus_sppr"],"configuration":method["configuration"]})

geo={"target":"LME_022", "study_proxy":"ICES divisions IVa, IVb, IVc",
     "source_passage":"ICES WGSAM Report 2015 Annex 6, printed p.102 / PDF p.104: Area structure North Sea ICES division IVa,b,c",
     "area_method":"WGS84 ellipsoidal polygon area; oriented rings; intersection of official coast-clipped ICES union with canonical target",
     "digital_boundary_comparison":raw,"common_land_mask_sensitivity":masked,
     "report_A":"approximately 87%", "report_B":"approximately 99-100%",
     "interpretation":"Broad whole-North-Sea coverage, larger than East Coast Scotland subset. Residual differences reflect domain limits and independently generalized coastlines.",
     "qualifications":["Report divisions identify the footprint; this is not a recovered native model spatial grid.",
                       "Official GIS was downloaded on the review date; no archived 1991/model-specific polygon is available.",
                       "A single common Natural Earth 1:50m land mask produces A=87.14%, B=99.63%; raw official coast-clipped comparison gives A=86.53%, B=98.86%.",
                       "Ranges reflect rounded boundary/coastline interpretation, not statistical confidence intervals.",
                       "The declared footprint pertains to the source model lineage. Material port parameter differences prevent assuming accepted native Key Run numerical equivalence.",
                       "Annex text search found declared divisions and a temperature-input bounding box, but no study-boundary map; source passage and explicitly labelled digital reconstruction retained."],
     "official_metadata_url":"https://gis.ices.dk/geonetwork/srv/api/records/c784a0a3-752f-4b50-b02f-f225f6c815eb?language=all",
     "official_query_url":"https://gis.ices.dk/gis/rest/services/ICES_reference_layers/ICES_Areas/MapServer/0/query?f=geojson&where=SubArea%3D%274%27&outFields=%2A&outSR=4326&returnGeometry=true",
     "assets":[{"path":rel(p),"sha256":sha(p)} for p in [target_path,land_path,GEO/"ices_divisions_IVa_IVb_IVc.geojson",GEO/"target_region.geojson",GEO/"study_area_union.geojson",GEO/"target_and_study_overlap.png",GEO/"source_report_page104.png",GEO/"source_area_passage.txt"]]}
(GEO/"geographic_assessment.json").write_text(json.dumps(geo,indent=2),encoding="utf-8")
result={"review_date":datetime.now(timezone.utc).isoformat(),"model_id":MODEL.name,
        "scope":"Saved evidence review plus report geography arithmetic; no extraction, ModelData, calculator, solver, Rpath or SPPR execution",
        "identities":identities,"diagnostics":[{"method":method,"status":"NOT_RUN","negative_source_group_pairs":None,
          "rho_living":None,"b":None,"detritus_sppr":{"DetritusDOMWaterColumn":None,"DetritusPOMSediment":None,"Discards":None},
          "reason":"Matching saved matrix and direct diagnostic absent; evidence index methods=[] and calculator_constructed=false"} for method in ["GE","TE"]],
        "calculator_configuration":{"effective_flags":None,"use_ee_floor":None,"det_collapse":None,"engine_identity":None,
                                     "reason":"No calculator execution exists; loader-only code/settings are not calculator provenance"},
        "saved_physical_budget":budget,"source_loading":{"loader":loader["loader"],"source_groups":69,"loaded_groups":70,
         "changed_field_counts":dict(Counter(x["field"] for x in loader["field_ledger"] if x.get("changed"))),
         "changed_detritus_fate":[x for x in loader["field_ledger"] if x.get("changed") and x["field"]=="detritus_fate"],
         "metadata":loader["loaded_metadata_observations"]},
        "source_fidelity":{"canonical_identity_verified":True,"independent_new_cellwise_extraction":False,
          "saved_source_reconciliation":read(EV/"source_to_canonical_check.json"),"saved_roundtrip":read(EV/"SOURCE_FIDELITY_CHECK.json"),
          "estimated_missing_native_inputs":extraction["model_estimated_roles"],"printed_report_comparison":extraction["native_report_basic_comparison"],
          "import_validation":"Three all-zero detritus-fate rows 67–69 violate generic sum=1 validator; source zeros and unknown export retained.",
          "native_equivalence":"Published Rpath port materially differs from accepted ICES native database, which remains unavailable.",
          "provenance_note":"inputs/provenance.json says equivalence not audited, superseded in detail by current model_notes and 276-cell comparison demonstrating material non-equivalence."},
        "geography":geo,
        "modern_scotland_comparison":{"model_id":NS.name,"canonical_sha256":sha(NS/"model.json"),
          "matrix_record_canonical_identity_matches":ns_matrices["canonical_sha256"]==sha(NS/"model.json"),
          "saved_matrix_path":rel(NS/"model_validation/evidence/source_review/matrix_inspection.json"),
          "methods":ns_checks,"geographic_assessment":read(NS/"model_validation/evidence/source_review/geography/geographic_assessment.json"),
          "scope":"Independent sign scan of retained 26x3 labelled matrices; historical direct-return/configuration attribution retained, no new run."},
        "recommended_next_step":"Audit source-to-runtime detrital routing and explicitly choose constructor flags/EE-floor assumption, then authorize exact GE/TE (standalone default also With Egestion) diagnostics retaining full labelled matrices and before/after runtime identities. Review-only retention, without input repair or regional adoption, unless separately authorized.",
        "report_ready":{"GE":"Not run. Negative source–group entries, rho_living, recycling parameter b and detritus-pool SPPR are unavailable for this port.",
                        "TE":"Not run. Negative source–group entries, rho_living and detritus-pool SPPR are unavailable for this port.",
                        "geography":"A (region covered by study): approximately 87%. B (study covered by region): approximately 99–100%.",
                        "temporal":"The deposited static base state represents 1991; source time-series calibration spans 1991–2013. Application to 2019 catch is a 28-year baseline transfer, not a calibrated 2019 food web.",
                        "extraction":"The 69-group, 11-fleet Rpath snapshot preserves deposited source inputs and estimated outputs for missing fields. It differs materially from the accepted ICES native Key Run. Retained source/roundtrip checks pass within stated tolerances, while three source-zero detritus-routing rows fail the generic importer rule. Static source budgets balance; GE/TE diagnostics remain unrun."}}
(RUN/"outputs/diagnostics_geography.json").write_text(json.dumps(result,indent=2,ensure_ascii=False),encoding="utf-8")
print(json.dumps({"output":rel(RUN/"outputs/diagnostics_geography.json"),"geography":raw,"masked":masked,"figure":rel(GEO/"target_and_study_overlap.png")},indent=2))
