import os
import secrets

FILENAME = 'secret_key'


def load(data_dir):
    """The signing key kept in the data folder, created on first run."""
    path = os.path.join(data_dir, FILENAME)
    try:
        with open(path) as f:
            key = f.read().strip()
        if key:
            return key
    except FileNotFoundError:
        pass
    key = secrets.token_hex(32)
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, 'w') as f:
        f.write(key)
    return key
