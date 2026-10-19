#!/usr/bin/env python3
"""Install the one CodeExp2 overlay; preserve global config and old overlay."""
import argparse
import datetime
import hashlib
import os
from pathlib import Path
import shutil
import tempfile


def install(config_home):
    root = Path(__file__).resolve().parent
    source = root / 'valhalla.config.toml'
    payload = source.read_bytes()
    destination = config_home / 'valhalla.config.toml'
    config_home.mkdir(parents=True, exist_ok=True)
    if destination.is_symlink():
        raise SystemExit('Refusing redirected Valhalla profile: ' + str(destination))
    if destination.exists() and destination.read_bytes() == payload:
        print('PASS: Valhalla profile already matches ' + str(destination))
        return
    backup = None
    if destination.exists():
        stamp = datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')
        backup_root = root / 'build' / 'valhalla-profile-backups'
        backup_root.mkdir(parents=True, exist_ok=True)
        backup_root = Path(tempfile.mkdtemp(prefix=stamp + '-', dir=backup_root))
        backup = backup_root / destination.name
        shutil.copy2(destination, backup)
    descriptor, temporary = tempfile.mkstemp(prefix='.valhalla-', dir=config_home)
    try:
        with os.fdopen(descriptor, 'wb') as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
            os.fchmod(handle.fileno(), 0o600)
        os.replace(temporary, destination)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)
    print('Installed: ' + str(destination))
    print('SHA256: ' + hashlib.sha256(payload).hexdigest())
    if backup:
        print('Previous profile preserved: ' + str(backup))
    print('Global config.toml was not changed.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config-home', type=Path,
                        default=Path(os.environ.get('CODEX_HOME', str(Path.home() / '.codex'))))
    arguments = parser.parse_args()
    if not arguments.config_home.is_absolute():
        parser.error('--config-home / CODEX_HOME must be an absolute directory')
    install(arguments.config_home)
