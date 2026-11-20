from datetime import datetime
from uuid import uuid4

import streamlit as st

from gallery_app import IMG_DIR


def run(open_gallery):
    st.title("📷 Camera")
    photo = st.camera_input("Take a picture")

    if photo and st.button("Save to Gallery", type="primary"):
        capture = f"Camera-{datetime.now():%Y%m%d-%H%M%S}-{uuid4().hex[:8]}.jpg"
        (IMG_DIR / capture).write_bytes(photo.getvalue())
        st.toast("Photo saved")
        open_gallery()
        st.rerun()