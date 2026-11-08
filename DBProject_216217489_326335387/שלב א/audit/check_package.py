"""Verify the submission artifacts; does not claim unfinished tasks are done."""
import hashlib
import re
from pathlib import Path
from urllib.parse import unquote

stage = Path(__file__).resolve().parent.parent
root = stage.parent.parent
required = [
    'README.md', 'DataDictionary.md', 'RestoreOnPartnerComputer.md',
    'createTables.sql', 'dropTables.sql', 'insertTables.sql', 'selectAll.sql',
    'ERD/ERD.erdplus', 'ERD/approved-erd.jpeg', 'DSD/DSD.erdplus', 'DSD/approved-dsd.png',
    'SQLInsert/baseSeed.sql', 'SQLInsert/extendCatalog.sql',
    'Programing/generate_data.py', 'Programing/generated.sql', 'Programing/orders.csv',
    'DataImportFiles/import.sql', 'DataImportFiles/technicians.csv',
    'Backup/backup_initial_2026-11-08.dump', 'Backup/backup_cli_2026-11-08.dump',
    'Backup/backup_pgadmin_2026-11-08.dump', 'docker-compose.yml', '.env.example',
    'audit/final_validation.txt', 'audit/replay_from_scripts.txt',
    'audit/restore_cli.txt', 'audit/restore_pgadmin.txt', 'audit/diagrams_verification.txt',
    'screenshots/pgadmin-backup-details.jpg',
]
for name in required:
    assert (stage / name).is_file() and (stage / name).stat().st_size, name

checked = 0
for doc in [root / 'README.md', *stage.rglob('*.md')]:
    for target in re.findall(r'\]\(([^)]+)\)', doc.read_text(encoding='utf-8-sig')):
        if re.match(r'https?://|#', target):
            continue
        target = unquote(target.split('#')[0])
        resolved = (doc.parent / target).resolve()
        assert resolved.is_relative_to(root.resolve()) and resolved.exists(), (str(doc), target)
        checked += 1
print(f'PASS: {len(required)} required artifact paths and {checked} local Markdown links verified.')

assert (stage/'audit/original_fingerprints_before.txt').read_bytes() == (stage/'audit/original_fingerprints_after.txt').read_bytes()
print('PASS: all original-row fingerprints match before and after data additions.')
for name in ['backup_cli_2026-11-08.dump', 'backup_pgadmin_2026-11-08.dump']:
    data = (stage/'Backup'/name).read_bytes()
    assert data.startswith(b'PGDMP'), name
    hash_log = stage/'audit'/('backup_cli_sha256.txt' if '_cli_' in name else 'backup_pgadmin_sha256.txt')
    digest = hashlib.sha256(data).hexdigest()
    assert digest.upper() in hash_log.read_text(encoding='utf-8-sig'), name
    print(f'PASS: Custom backup header and recorded SHA-256 match: {name}')

secret_re = re.compile(r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----|github_pat_[A-Za-z0-9_]{20,}|gh[pousr]_[A-Za-z0-9]{20,}|sk-proj-[A-Za-z0-9_-]{20,}')
for path in stage.rglob('*'):
    if not path.is_file():
        continue
    assert path.name != '.env' and not (path.name.startswith('.env.') and path.name != '.env.example'), str(path)
    if path.suffix not in {'.dump', '.jpg', '.jpeg', '.png'}:
        assert not secret_re.search(path.read_text(encoding='utf-8-sig')), f'Credential-like content detected: {path.name}'
print('PASS: no populated .env file, private key or supported access-token pattern found in submission files.')
print('LIMITATION: this scan is not proof that every possible secret pattern is absent. File provenance was reviewed separately.')
print('OPEN ITEMS: partner-computer restore evidence; DATE-vs-TIMESTAMP lecturer clarification; remaining screenshots if not linked in README. AI Studio was excluded by user instruction.')
