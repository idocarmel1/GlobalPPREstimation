"""Coordinator-only negative review batch. Dry preflight by default.
Requires installation of proposed shared patch and review_candidates.py.
Never runs scientific coverage, arithmetic, selection or full HTML build.
"""
import argparse
import json
import shutil
import sys
from datetime import datetime
from pathlib import Path
ROOT=next(p for p in Path(__file__).resolve().parents if (p/'Project.xlsx').exists())
sys.path.insert(0,str(ROOT))
RUN=Path(__file__).resolve().parents[1]
from tools.project_core.registry.discovery import region_directory, resolve_model
from tools.project_core.validation.researcher_review import read_report, sha, _register_review
PAIRS=[('LME_024','Hernvann_2020_Celtic_Sea_1985'),('LME_026','Piroddi_2022_Mediterranean_1995'),('LME_026','Piroddi_2022_Mediterranean_1995_Pooled_Detritus_20261114')]
EXPECTED=[('b4ba75b14c47a23b2b97aaacdc4b392f2183679e201942c35f36b910c92b63cf','cf2c5d6e37ae4747a7fea9ef098ab3f036081965bb4d574667779823dd7af782'),('f038707bf7837962933eec3e6daeae53eb0b9a7f48837763b0ce621edcdc3a9e','092dafe37aa0125198f63b61da8d41f88e30fe9a87d675f0109327f886fef0a5'),('281d8543a165bf67652168cbc47f09db224e51bddb6768e9365f8c52d03ac956','337ef70efe2a1f904505728208e2041eb8ab9457c16e3784c4c08e64ba16c64d')]

def preflight():
    reports=[];protected={}
    for (unit,model),(model_hash,report_hash) in zip(PAIRS,EXPECTED):
        source=resolve_model(region_directory(ROOT,unit),model)
        report=source.parent/'model_validation/validation.docx'
        if sha(source)!=model_hash or sha(report)!=report_hash:raise ValueError('Signed source changed: '+model)
        name,date,summary=read_report(ROOT,report,model)
        if (name,date,summary.get('status'))!=('Ido Carmel','2026-11-14','Disqualified by researcher'):raise ValueError('Signed identity changed')
        if summary.get('sections'):raise ValueError('A rejection cannot transfer positive sections')
        reports.append(report)
        for path in [source,report,region_directory(ROOT,unit)/(unit+'.xlsx')]:protected[str(path)]=sha(path)
    proposal_path=RUN.parent/'2026-11-14_201300_disqualification_binding/outputs/proposed_central_metadata.json'
    if sha(proposal_path)!='2f2ef664114ce0025eade85e168fdf115e78e44bf0a1515e0832fb621e64ad67':raise ValueError('Exact authorized candidate metadata changed')
    proposal=json.loads(proposal_path.read_text())
    notes=resolve_model(region_directory(ROOT,'LME_026'),PAIRS[-1][1]).parent/'model_notes.md'
    if sha(notes)!=proposal['provenance']['model_notes_sha256']:raise ValueError('Candidate provenance changed')
    protected[str(proposal_path)]=sha(proposal_path);protected[str(notes)]=sha(notes)
    return reports,protected,[{'row':proposal['row'],'canonical_sha256':EXPECTED[-1][0]}]

def main(execute=False):
    reports,protected,candidates=preflight()
    if not execute:
        print(json.dumps({'preflight':'passed','pairs':PAIRS,'shared_mutations':False},indent=2));return
    from tools.project_core.registry.writes import central_lock
    from tools.project_core.registry.publication import publication_transaction
    from tools.project_core.registry.review_candidates import add_review_candidate
    from tools.project_core.maps.build_html import _refresh_reviews
    project=ROOT/'Project.xlsx'
    with central_lock(ROOT):
        reports,protected,candidates=preflight()
        receipt_dir=RUN/'outputs'/datetime.now().strftime('%Y%m%d_%H%M%S')
        receipt_dir.mkdir()
        previous=receipt_dir/'Project_before_registration.xlsx'
        shutil.copyfile(project,previous)
        with publication_transaction(ROOT) as publication:
            for item in candidates:
                add_review_candidate(project,ROOT,item['row'],item['canonical_sha256'])
                publication.checkpoint([project])
            for (unit,model),report in zip(PAIRS,reports):
                _register_review(project,report,unit,model,[])
                publication.checkpoint([project])
            kwargs={'model_pairs':PAIRS,'candidate_rows':candidates}
            _refresh_reviews(project,previous,[],publish=False,**kwargs)
            if any(sha(Path(path))!=digest for path,digest in protected.items()):raise ValueError('Protected source changed')
            _refresh_reviews(project,previous,[],**kwargs)
            if any(sha(Path(path))!=digest for path,digest in protected.items()):raise ValueError('Protected source changed')
            (receipt_dir/'registration_receipt.json').write_text(json.dumps({'before_project':sha(previous),'after_project':sha(project),'pairs':PAIRS,'protected':protected,'candidate_rows':candidates},indent=2),encoding='utf-8')
        print(str(receipt_dir))

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--execute',action='store_true');args=parser.parse_args();main(args.execute)

