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


def settings_bucket():
    if local_mode():
        return None
    try:
        return st.secrets.get("settings_storage")
    except FileNotFoundError:
        return None


@st.cache_resource
def object_store():
    import boto3

    config = settings_bucket()
    return boto3.client(
        "s3",
        region_name=config["region"],
        aws_access_key_id=config["access_key_id"],
        aws_secret_access_key=config["secret_access_key"],
    )


def saved_settings(account, bucket, fallback):
    from botocore.exceptions import BotoCoreError, ClientError

    try:
        response = object_store().get_object(Bucket=bucket, Key=f"settings/{account}.json")
        with response["Body"] as body:
            return json.loads(body.read())
    except ClientError as error:
        if error.response["Error"]["Code"] == "NoSuchKey":
            return fallback
    except (BotoCoreError, ValueError, KeyError):
        pass
    st.error("Saved settings could not be loaded. Please try again later.")
    st.stop()


def read(key, fallback):
    directory = user_directory()
    config = settings_bucket() if key == "settings" else None
    data = load_data(directory / "phone_data.json")
    value = data[key] if key in data else fallback()
    return saved_settings(directory.name, config["bucket"], value) if config else value


def update(key, fallback, transform):
    path = user_directory() / "phone_data.json"
    with WRITE_LOCK:
        config = settings_bucket() if key == "settings" else None
        if config:
            from botocore.exceptions import BotoCoreError, ClientError

            value = transform(read(key, fallback))
            try:
                object_store().put_object(
                    Bucket=config["bucket"],
                    Key=f"settings/{path.parent.name}.json",
                    Body=json.dumps(value, ensure_ascii=False).encode("utf-8"),
                    ContentType="application/json",
                )
            except (BotoCoreError, ClientError, KeyError):
                st.error("Settings could not be saved. Please try again later.")
                st.stop()
            return
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
