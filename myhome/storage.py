import json
from pathlib import Path
from tempfile import NamedTemporaryFile
from threading import Lock


DATA_FILE = Path("phone_data.json")
WRITE_LOCK = Lock()


def load_data():
    try:
        return json.loads(DATA_FILE.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return {}


def read(key, fallback):
    data = load_data()
    return data[key] if key in data else fallback()


def update(key, fallback, transform):
    with WRITE_LOCK:
        data = load_data()
        data[key] = transform(data[key] if key in data else fallback())
        temp_path = None

        try:
            with NamedTemporaryFile(
                mode="w", encoding="utf-8", dir=DATA_FILE.parent, delete=False
            ) as output:
                temp_path = Path(output.name)
                json.dump(data, output, ensure_ascii=False, indent=2)
            temp_path.replace(DATA_FILE)
        finally:
            if temp_path is not None:
                temp_path.unlink(missing_ok=True)


def legacy_settings():
    try:
        return json.loads(Path("phone_settings.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}
