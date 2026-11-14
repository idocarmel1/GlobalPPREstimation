"""Explicit reproduction of this retained package; does not adopt regional results.

The canonical source remains unchanged. Unknown diet imports are assigned zero
only in the ephemeral loaded diet, preserving the historical audited assumption.
Use construct_calculator() for a loader-only check. Running the command requires
--output and performs the three explicitly configured diagnostic calculations.
"""
from pathlib import Path
import argparse, hashlib, importlib.util, json, sys, warnings

PACKAGE=Path(__file__).resolve().parent
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def construct_calculator():
    configuration=json.loads((PACKAGE/'configuration.json').read_text(encoding='utf-8'))
    source=next(p/'model.json' for p in PACKAGE.parents if (p/'model.json').is_file())
    if sha(source)!=configuration['canonical_model_sha256']:
        raise ValueError('Canonical source differs from the authenticated execution')
    for name,expected in configuration['engine_hashes'].items():
        if sha(PACKAGE/'executed_code'/name)!=expected:
            raise ValueError('Executed engine source changed: '+name)
    sys.path.insert(0,str(PACKAGE/'executed_code'))
    from ModelData import ModelData
    from PPRCalculator import PPRCalculator
    import pandas as pd
    md=ModelData(str(source),model_name='Visayan_Sea_Bacalso_baseline',model_year='1997')
    import_id=next(k for k,v in md.seq2name.items() if v=='diet_import')
    assert import_id==34
    md.DC.loc[:,import_id]=0.0
    historical_routing=configuration['input_transformations']['single_detritus_routing']['source_group_fractions']
    md.det_fate=pd.DataFrame({33:{int(k):float(v) for k,v in historical_routing.items()}}).sort_index(ascending=False)
    calc=PPRCalculator.from_modeldata(md,**configuration['constructor'])
    assert calc.ee_floor_info['affected_groups']==[1]
    return calc,configuration

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--output',type=Path,required=True,help='New model-local work directory for reproduced full returns')
    args=ap.parse_args()
    output=args.output.resolve()
    if output==PACKAGE or output.is_relative_to(PACKAGE):
        raise ValueError('Use a separate work directory, preserving the retained evidence')
    output.mkdir(parents=True,exist_ok=True)
    if any(output.iterdir()):raise ValueError('Reproduction output directory must be empty')
    calc,config=construct_calculator()
    spec=importlib.util.spec_from_file_location('package_runtime_codec',PACKAGE/'runtime_codec.py')
    codec=importlib.util.module_from_spec(spec);spec.loader.exec_module(codec)
    for option,stem in [('GE','GE'),('TE','TE'),('With Egestion','With_Egestion')]:
        result=calc.diagnose_sppr(TE_option=option,short=False,flat=False,return_sppr=True,**config['diagnostics'])
        (output/(stem+'_full_return.json')).write_text(json.dumps(codec.encode(result),ensure_ascii=False,allow_nan=False),encoding='utf-8')
    print(output)

if __name__=='__main__':main()
