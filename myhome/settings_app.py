import streamlit as st

from gallery_app import list_images
from look import load_settings, save_settings, WALLPAPERS


def run():
    st.title("⚙️ Settings")
    s = load_settings()
    tab1, tab2, tab3 = st.tabs(["🎨 Look", "🔒 Lock", "📱 Phone"])

    with tab1:
        dark = st.toggle("🌙 Dark mode", value=s["dark"], key="set_dark")
        if dark != s["dark"]:
            save_settings({"dark": dark})
            st.rerun()

        st.subheader("🖼️ Wallpaper")
        photos = [p.name for p in list_images()]
        names = list(WALLPAPERS)
        options = names + (["📷 Photo from Gallery"] if photos else [])

        current = s["wallpaper"]
        if current.startswith("img:") and photos:
            index = len(names)
        elif current in names:
            index = names.index(current)
        else:
            index = 0

        choice = st.radio("Choose wallpaper", options, index=index, key="set_wall")

        if choice == "📷 Photo from Gallery":
            photo = st.selectbox("Pick a picture", photos, key="set_photo")
            st.image(f"images/{photo}", width=200)
            new_wall = f"img:{photo}"
        else:
            st.markdown(
                f'<div style="height:120px; width:200px; border-radius:20px; '
                f'background:{WALLPAPERS[choice]}"></div>',
                unsafe_allow_html=True,
            )
            new_wall = choice

        if st.button("✅ Apply wallpaper"):
            save_settings({"wallpaper": new_wall})
            st.success("Wallpaper changed! Go Home to see it 🏠")

    with tab2:
        lock_on = st.toggle("🔒 Lock screen", value=s["lock_on"], key="set_lock")
        if lock_on != s["lock_on"]:
            save_settings({"lock_on": lock_on})
            st.rerun()

        st.subheader("Change PIN")
        with st.form("pin_form", clear_on_submit=True):
            old = st.text_input("Current PIN", type="password", max_chars=4)
            new = st.text_input("New PIN (4 digits)", type="password", max_chars=4)
            again = st.text_input("Confirm new PIN", type="password", max_chars=4)

            if st.form_submit_button("Change PIN"):
                if old != s["pin"]:
                    st.error("Current PIN is wrong ❌")
                elif not (new.isdigit() and len(new) == 4):
                    st.error("New PIN must be exactly 4 digits")
                elif new != again:
                    st.error("PINs don't match")
                else:
                    save_settings({"pin": new})
                    st.success("PIN changed ✅")

    with tab3:
        name = st.text_input("Phone name", value=s["phone_name"], key="set_name")
        if st.button("Save name"):
            save_settings({"phone_name": name.strip() or "My Phone"})
            st.success("Saved ✅")