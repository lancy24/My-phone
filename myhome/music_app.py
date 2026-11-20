import mimetypes
from pathlib import Path

import streamlit as st


MUSIC_DIR = Path("music")
MUSIC_DIR.mkdir(exist_ok=True)


def list_songs():
    exts = {".mp3", ".wav", ".ogg", ".m4a"}
    return sorted(p for p in MUSIC_DIR.iterdir() if p.suffix.lower() in exts)


def run():
    st.title("🎵 Music")

    files = st.file_uploader(
        "Add songs",
        type=["mp3", "wav", "ogg", "m4a"],
        accept_multiple_files=True,
    )

    if st.button("➕ Add to playlist") and files:
        for f in files:
            (MUSIC_DIR / f.name).write_bytes(f.getbuffer())
        st.success("Songs added ✅")
        st.rerun()

    songs = list_songs()
    if not songs:
        st.info("No songs yet. Upload some above 🎶")
        return

    names = [p.name for p in songs]
    current = st.selectbox("🎧 Now playing", names, key="music_now")
    path = MUSIC_DIR / current
    mime = mimetypes.guess_type(path.name)[0] or "audio/mpeg"
    st.audio(path.read_bytes(), format=mime)

    st.subheader("📜 Playlist")
    for i, p in enumerate(songs):
        c1, c2 = st.columns([12, 1])
        c1.write(f"🎵 {p.name}")
        if c2.button("🗑️", key=f"music_del_{i}"):
            p.unlink()
            st.rerun()