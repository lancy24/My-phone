from datetime import datetime
from io import BytesIO
from uuid import uuid4

import streamlit as st
from PIL import Image, ImageOps, UnidentifiedImageError

from gallery_app import image_directory


def run(open_gallery):
    st.title("📷 Camera")
    reverse = st.toggle(
        "Mirror selfie",
        value=True,
        help="Shows your right hand on the right of the screen. Applies to the preview and saved photo. Turn off for the back camera or to keep text readable.",
    )
    if reverse:
        st.html("""
            <style>
            [data-testid="stCameraInput"] video,
            [data-testid="stCameraInput"] img[alt="Snapshot"] {
                transform: scaleX(-1);
            }
            </style>
        """)
    photo = st.camera_input("Take a picture")

    if photo and st.button("Save to Gallery", type="primary"):
        capture = f"Camera-{datetime.now():%Y%m%d-%H%M%S}-{uuid4().hex[:8]}.jpg"
        try:
            with Image.open(photo) as image:
                jpeg = BytesIO()
                oriented = ImageOps.exif_transpose(image)
                if reverse:
                    oriented = ImageOps.mirror(oriented)
                oriented.convert("RGB").save(jpeg, "JPEG", quality=90)
            (image_directory() / capture).write_bytes(jpeg.getvalue())
        except (UnidentifiedImageError, Image.DecompressionBombError, OSError):
            st.error("This photo could not be saved. Try a JPEG or PNG photo.")
            return
        st.toast("Photo saved")
        open_gallery()
        st.rerun()
