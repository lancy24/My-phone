from datetime import datetime
from io import BytesIO
from uuid import uuid4

import streamlit as st
from PIL import Image, ImageOps, UnidentifiedImageError

from gallery_app import image_directory


def run(open_gallery):
    st.title("📷 Camera")
    photo = st.camera_input("Take a picture")

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
