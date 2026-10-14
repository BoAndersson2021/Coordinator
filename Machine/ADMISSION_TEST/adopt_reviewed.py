"""Owner-directed adoption of the exact independently reviewed eight-file candidate."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile

PROOF = Path(__file__).resolve().parent
manifest_bytes = (PROOF / 'CANDIDATE.json').read_bytes()
assert hashlib.sha256(manifest_bytes).hexdigest() == '6216b9eeee3be10a1f1c2985129dfd5843e9a26ac930ec4b63b7b3ea008b8791'
manifest = json.loads(manifest_bytes)
plan = json.loads((PROOF / 'ADOPTION_PLAN.json').read_text())
assert plan['adoption_eligible'] is True
review = json.loads((PROOF / 'REVIEW.json').read_text())
assert review['turns'][0]['id'] == '01a13832-8349-7ea0-81d8-158fd7d7f802'
assert review['turns'][0]['status'] == 'completed'
assert any(x.get('type') == 'agentMessage' and x.get('phase') == 'final_answer'
           and x['text'].startswith('**PASS for the stated local-operator scratch-init scope.')
           and manifest['source_head'] in x['text']
           for x in review['turns'][0]['items'])
root, candidate = Path(manifest['source_root']), Path(manifest['candidate_root'])
assert subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=root, text=True).strip() == manifest['source_head']
assert not subprocess.check_output(['git', 'status', '--porcelain'], cwd=root, text=True).strip()
baseline = json.loads((PROOF / 'PRE_ADOPTION.json').read_text())['files']
def files():
    return {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in root.rglob('*') if p.is_file() and '.git' not in p.relative_to(root).parts}
assert files() == baseline
for name, sha in manifest['files'].items():
    assert hashlib.sha256((candidate / name).read_bytes()).hexdigest() == sha
backup = Path(tempfile.mkdtemp(prefix='machine-admission-prior-', dir='/private/tmp'))
for name in manifest['files']:
    src = root / name
    if src.exists():
        (backup / name).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, backup / name)
(backup / 'manifest.json').write_text(json.dumps({'source_head': manifest['source_head'],
    'files': {name: baseline.get(name) for name in manifest['files']}}, indent=2) + '\n')
# Preserve prior source before replacing any file; no deletions or SQLite writes.
for name in manifest['files']:
    dest = root / name
    temporary = dest.with_name('.admission-adopt-' + dest.name)
    shutil.copy2(candidate / name, temporary)
    with temporary.open('rb') as stream:
        os.fsync(stream.fileno())
    os.replace(temporary, dest)
    fd = os.open(dest.parent, os.O_RDONLY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)
after = files()
expected = dict(baseline, **manifest['files'])
assert after == expected
result = {'status': 'adopted', 'owner_quote': plan['owner_quote'],
    'independent_review_turn': review['turns'][0]['id'], 'candidate_manifest_sha256': plan['candidate_manifest_sha256'],
    'backup_root': str(backup), 'files': manifest['files'], 'legacy_ledger_unchanged': True,
    'other_live_files_unchanged': True, 'committed': False}
(PROOF / 'ADOPTION.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps(result, indent=2))
