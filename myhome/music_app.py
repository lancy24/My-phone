from pathlib import Path

import streamlit as st

from storage import media_directory


AUDIO_TYPES = {
    ".mp3": "audio/mpeg",
    ".wav": "audio/wav",
    ".ogg": "audio/ogg",
    ".m4a": "audio/mp4",
}

def list_songs():
    return sorted(p for p in media_directory("music").iterdir()
                  if p.is_file() and p.suffix.lower() in AUDIO_TYPES)


def run():
    st.title("🎵 Music")
    st.caption("Choose a song and tap Play. If a file does not play on your phone, try an MP3.")

    files = st.file_uploader(
        "Add songs",
        type=["mp3", "wav", "ogg", "m4a"],
        accept_multiple_files=True,
    )

    if st.button("➕ Add to playlist") and files:
        directory = media_directory("music")
        for f in files:
            (directory / Path(f.name).name).write_bytes(f.getbuffer())
        st.success("Songs added ✅")
        st.rerun()

    songs = list_songs()
    if not songs:
        st.info("No songs yet. Upload some above 🎶")
        return

    names = [p.name for p in songs]
    current = st.selectbox("🎧 Now playing", names, key="music_now")
    path = next(song for song in songs if song.name == current)
    try:
        audio = path.read_bytes()
    except FileNotFoundError:
        st.warning("This song was removed. Reopen Music to refresh the playlist.")
        return
    mime = AUDIO_TYPES[path.suffix.lower()]
    st.audio(audio, format=mime, autoplay=False)
    st.download_button("Download song", audio, file_name=path.name, mime=mime)

    st.subheader("📜 Playlist")
    for i, p in enumerate(songs):
        c1, c2 = st.columns([12, 1])
        c1.write(f"🎵 {p.name}")
        if c2.button("🗑️", key=f"music_del_{i}"):
            p.unlink()
            st.rerun()
