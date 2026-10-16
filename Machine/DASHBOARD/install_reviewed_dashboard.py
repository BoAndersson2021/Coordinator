"""Owner-authorized adoption of the exact independently reviewed dashboard V2."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import shutil

BASE = Path(__file__).resolve().parent
ROOT = Path('/Users/boandersson/Desktop/Machine')
MANIFEST = BASE / 'REVIEW_MANIFEST_V2.json'
EXPECTED = 'aefb50e537af4942a4d72334b549aeb76caebcc825091efb5bead628f655e556'
assert hashlib.sha256(MANIFEST.read_bytes()).hexdigest() == EXPECTED
manifest = json.loads(MANIFEST.read_text())
candidate = Path(manifest['candidate_root'])
review = json.loads((BASE / 'INDEPENDENT_REVIEW_V2.json').read_text())
assert review['turn_id'] == '01a1431a-f02e-7a80-a2d6-fd95e853e7c6'
assert 'PASS for the exact dashboard V2' in '\n'.join(review['final'])
assert EXPECTED in '\n'.join(review['final'])
baseline = json.loads((BASE / 'BASELINE.json').read_text())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
private = lambda: {str(p.relative_to(ROOT)): sha(p) for p in (ROOT / '.machine').rglob('*') if p.is_file()}
for relative, digest in baseline['source'].items():
    assert sha(ROOT / relative) == digest, 'Installed source changed before adoption: ' + relative
assert private() == baseline['private'], 'Private state changed before adoption'
for relative, digest in manifest['files'].items():
    assert sha(candidate / relative) == digest, 'Candidate pin changed: ' + relative

installation = BASE / 'installation'
installation.mkdir()
previous = {}
for relative in manifest['files']:
    target = ROOT / relative
    if target.exists():
        saved = installation / 'previous' / relative
        saved.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(target, saved)
        previous[relative] = sha(target)
trusted = ROOT / '.git/machine-invariant-hooks/check_workflow_invariant.py'
assert trusted.is_file()
shutil.copy2(trusted, installation / 'previous-installed-verifier.py')
previous_verifier = sha(trusted)

for relative, digest in manifest['files'].items():
    target = ROOT / relative
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(candidate / relative, target)
    assert sha(target) == digest
shutil.copy2(candidate / 'scripts/check_workflow_invariant.py', trusted)
trusted.chmod(0o700)
assert private() == baseline['private'], 'Private state changed during adoption'
record = {'status': 'PASS', 'adopted_at': datetime.now(timezone.utc).isoformat(),
          'review_manifest_sha256': EXPECTED, 'review_turn_id': review['turn_id'],
          'files': manifest['files'], 'previous_source': previous,
          'previous_installed_verifier_sha256': previous_verifier,
          'installed_verifier_sha256': sha(trusted), 'private_files_preserved': len(baseline['private']),
          'workflow_execution': 'blocked', 'runtime_automation_qualified': False,
          'service_activation': 'Separate explicit Machine dashboard command after this source adoption'}
(installation / 'RESULT.json').write_text(json.dumps(record, indent=2) + '\n')
print(json.dumps({'status': 'PASS', 'adopted_files': len(manifest['files']),
                  'private_files_preserved': len(baseline['private']), 'workflow_execution': 'blocked'}))
