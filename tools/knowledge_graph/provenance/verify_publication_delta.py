"""Verify the plan-scoped publication delta against its actual graph attributes."""
from pipeline import ROOT, GRAPH, PROV, load, save, sha, now, assert_sources

corpus = assert_sources()
source = 'explainers/plans/project_reorganization_plan.md'
release = '7b2989fa2afce05130a198f67901d94c48cf7eec'
thread = '01a104ef-49cc-7df1-9ed8-236969ab61b0'
remote = 'https://github.com/idocarmel1/GlobalPPREstimation.git'
text = (ROOT / source).read_text('utf-8')
assert release in text and thread in text and remote in text
graph = load(GRAPH / 'graph.json')
nodes = {n['id']: n for n in graph['nodes']}
checks = {
    'published_reorganization_first_release': [release, remote, 'exact local/remote-tip match'],
    'plan_and_implement_scoped_skill_efficiency': [thread, 'read-only planning barrier is not yet lifted',
        'independently replicated retained work distinguished from saved-output reuse/regeneration'],
    'pending_administrative_publication_closeout': ['remains to be pushed',
        'then lifts fresh chat', 'No self-referential SHA fabricated'],
    'task_15_verified_commit_push_handoff': [release, 'are still pending']
}
records = []
for suffix, required in checks.items():
    node = nodes['plans_project_reorganization_plan_' + suffix]
    assert node['source_file'] == source and node['source_sha256'] == corpus['sha256'][source]
    assert not node['historical'] and all(value in node['rationale'] for value in required)
    records.append({key: node[key] for key in ['id', 'label', 'source_location', 'source_sha256']})
result = {
    'checked_at': now(), 'pass': True, 'graph_sha256': sha(GRAPH / 'graph.json'),
    'plan_sha256': corpus['sha256'][source], 'first_release_sha': release,
    'verified_remote': remote, 'fresh_follow_up_thread': thread, 'first_release': 'published',
    'closing_administrative_commit': 'pending', 'read_only_barrier_lift': 'pending',
    'independent_replication_distinguished_from_saved_output_reuse': True,
    'current_plan_scoped_nodes': records,
    'limit': 'This checks actual plan-scoped semantic attributes and citations, not a second remote push or scientific run.'
}
save(PROV / 'publication_delta_verification.json', result)
print({'pass': True, 'nodes_checked': len(records), 'plan_sha256': result['plan_sha256'],
       'graph_sha256': result['graph_sha256'], 'first_release': 'published', 'closing_barrier': 'pending'})
