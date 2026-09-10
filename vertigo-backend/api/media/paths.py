import os

from flask import current_app

USERS_DIR = "users"

AVATAR_DIR = "avatar"
SERIES_DIR = "series"
ISSUES_DIR = "issues"
ENTITIES_DIR = "entities"
ENTITY_KINDS = ("publisher", "creator", "character")


def data_dir() -> str:
    return current_app.config["DATA_DIR"]


def user_root(user_id) -> str:
    return os.path.join(data_dir(), USERS_DIR, str(user_id))
import os


def series_dir(series_id) -> str:
    return f"{SERIES_DIR}/{series_id}"


def issues_dir(series_id) -> str:
    return f"{SERIES_DIR}/{series_id}/{ISSUES_DIR}"


def entity_dir(kind: str) -> str:
    if kind not in ENTITY_KINDS:
        raise ValueError(f"unknown entity kind {kind!r}")
    return f"{ENTITIES_DIR}/{kind}"


def init_user_dirs(user_id) -> str:
    root = user_root(user_id)
    for rel in (AVATAR_DIR, SERIES_DIR, *(entity_dir(k) for k in ENTITY_KINDS)):
        os.makedirs(os.path.join(root, rel), exist_ok=True)
    return root


def safe_join(root: str, relpath: str):
    """Join and refuse anything that escapes root"""
    if not relpath:
        return None
    root = os.path.abspath(root)
    full = os.path.abspath(os.path.normpath(os.path.join(root, relpath)))
    if os.path.commonpath([root, full]) != root:
        return None
    return full


def resolve(user_id, relpath):
    """Absolute path of a stored image, or None if it does not exist."""
    if not relpath:
        return None
    full = safe_join(user_root(user_id), relpath)
    if full and os.path.isfile(full):
        return full
    return None
