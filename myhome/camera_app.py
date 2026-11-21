from datetime import datetime
from io import BytesIO
from uuid import uuid4

import streamlit as st
from PIL import Image, ImageOps, UnidentifiedImageError

from gallery_app import image_directory


def run(open_gallery):
    st.title("📷 Camera")
    source = st.radio("Photo source", ["Live camera", "Phone camera or photos"], horizontal=True)
    if source == "Live camera":
        st.caption("Allow camera access in your browser. If the preview stays blank, try Phone camera or photos.")
        photo = st.camera_input("Take a picture")
    else:
        photo = st.file_uploader("Choose Camera or a photo in your phone's picker", type=["jpg", "jpeg", "png", "webp"])

    if photo and st.button("Save to Gallery", type="primary"):
        capture = f"Camera-{datetime.now():%Y%m%d-%H%M%S}-{uuid4().hex[:8]}.jpg"
        try:
            with Image.open(photo) as image:
                jpeg = BytesIO()
                ImageOps.exif_transpose(image).convert("RGB").save(jpeg, "JPEG", quality=90)
            (image_directory() / capture).write_bytes(jpeg.getvalue())
        except (UnidentifiedImageError, Image.DecompressionBombError, OSError):
            st.error("This photo could not be saved. Try a JPEG or PNG photo.")
            return
        st.toast("Photo saved")
        open_gallery()
        st.rerun()
