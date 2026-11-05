"""Zip the SQLite database and every user's images, safe while Vertigo runs: python scripts/backup_data.py [out_dir]."""
import os
import shutil
import sqlite3
import sys
import tempfile
import zipfile
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import Config  # noqa: E402

DATABASE = 'vertigo.sqlite'
USERS_DIR = 'users'


def copy_database(source: str, target: str) -> None:
    with sqlite3.connect(source) as src, sqlite3.connect(target) as dst:
        src.backup(dst)


def main(argv) -> int:
    data_dir = Config.DATA_DIR
    database = os.path.join(data_dir, DATABASE)
    users = os.path.join(data_dir, USERS_DIR)
    if not os.path.isfile(database):
        print(f'No database at {database}; nothing to back up.')
        return 1

    out_dir = os.path.abspath(argv[1]) if len(argv) > 1 else os.getcwd()
    os.makedirs(out_dir, exist_ok=True)
    stamp = datetime.now().strftime('%Y%m%d-%H%M%S')
    archive = os.path.join(out_dir, f'vertigo-data-{stamp}.zip')

    with tempfile.TemporaryDirectory() as tmp:
        snapshot = os.path.join(tmp, DATABASE)
        copy_database(database, snapshot)
        files = 0
        with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED) as zf:
            zf.write(snapshot, DATABASE)
            for root, _, names in os.walk(users):
                for name in names:
                    if name.endswith('.part'):
                        continue
                    full = os.path.join(root, name)
                    zf.write(full, os.path.relpath(full, data_dir))
                    files += 1
    size = os.path.getsize(archive) / (1024 * 1024)
    print(f'Wrote {archive} ({size:.1f} MB): the database and {files} image files.')
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
