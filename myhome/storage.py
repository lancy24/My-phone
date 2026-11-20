import json
import os
from hashlib import sha256
from pathlib import Path
from tempfile import NamedTemporaryFile
from threading import Lock

import streamlit as st

WRITE_LOCK = Lock()


def local_mode():
    return os.getenv("MY_PHONE_LOCAL_MODE") == "1"


def user_directory():
    if local_mode():
        return Path(".")

    identity = st.user.to_dict()
    subject = identity.get("sub")
    if not getattr(st.user, "is_logged_in", False) or not isinstance(subject, str) or not subject:
        raise PermissionError("Sign in before accessing phone data.")

    account = sha256(subject.encode("utf-8")).hexdigest()
    root = Path(os.getenv("MY_PHONE_DATA_ROOT", Path.home() / ".my-phone"))
    return root / account


def media_directory(kind):
    directory = user_directory() / kind
    directory.mkdir(parents=True, exist_ok=True)
    return directory


def load_data(path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return {}


def read(key, fallback):
    data = load_data(user_directory() / "phone_data.json")
    return data[key] if key in data else fallback()


def update(key, fallback, transform):
    path = user_directory() / "phone_data.json"
    with WRITE_LOCK:
        path.parent.mkdir(parents=True, exist_ok=True)
        data = load_data(path)
        data[key] = transform(data[key] if key in data else fallback())
        temp_path = None

        try:
            with NamedTemporaryFile(
                mode="w", encoding="utf-8", dir=path.parent, delete=False
            ) as output:
                temp_path = Path(output.name)
                json.dump(data, output, ensure_ascii=False, indent=2)
            temp_path.replace(path)
        finally:
            if temp_path is not None:
                temp_path.unlink(missing_ok=True)


def legacy_settings():
    if not local_mode():
        return {}
    try:
        return json.loads(Path("phone_settings.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}
