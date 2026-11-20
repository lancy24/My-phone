import io
import mimetypes
import zipfile
from datetime import date
from pathlib import Path
from uuid import uuid4

import streamlit as st

from look import save_settings
from storage import media_directory, update


def image_directory():
    return media_directory("images")


def list_images():
    exts = {".png", ".jpg", ".jpeg", ".webp", ".gif"}
    return sorted(p for p in image_directory().iterdir() if p.is_file() and p.suffix.lower() in exts)


def run():
    st.title("🖼️ Gallery")

    files = st.file_uploader(
        "Upload pictures",
        type=["png", "jpg", "jpeg", "webp"],
        accept_multiple_files=True,
    )

    if st.button("Save pictures") and files:
        directory = image_directory()
        for f in files:
            name = Path(f.name).name
            target = directory / name
            if target.exists():
                target = directory / f"{target.stem}-{uuid4().hex[:8]}{target.suffix}"
            target.write_bytes(f.getbuffer())
        st.toast("Pictures saved")
        st.rerun()

    imgs = list_images()
    if not imgs:
        st.info("Take a photo in Camera or upload one here.")
        return

    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as z:
        for p in imgs:
            z.write(p, arcname=p.name)

    st.download_button(
        "📦 Download all (ZIP)",
        buf.getvalue(),
        file_name="my_pictures.zip",
        mime="application/zip",
    )

    photo = st.selectbox("Photo", imgs, format_func=lambda path: path.name)
    st.image(str(photo), use_container_width=True)

    left, right = st.columns(2)
    if left.button("Set as wallpaper", use_container_width=True):
        save_settings({"wallpaper": f"img:{photo.name}"})
        st.toast("Wallpaper updated")

    right.download_button(
        "Download photo",
        photo.read_bytes(),
        file_name=photo.name,
        mime=mimetypes.guess_type(photo.name)[0] or "image/png",
        use_container_width=True,
    )

    with st.expander("Add to photo diary"):
        with st.form("photo_diary", clear_on_submit=True):
            day = st.date_input("Date", date.today())
            caption = st.text_input("Caption", max_chars=200)

            if st.form_submit_button("Save diary entry"):
                entry = {
                    "date": day.isoformat(),
                    "photo": photo.name,
                    "caption": caption.strip(),
                }
                update("diary", list, lambda entries: entries + [entry])
                st.success("Saved to Calendar")
