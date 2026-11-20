import time

import streamlit as st


def init():
    s = st.session_state
    defaults = {
        "tm_running": False,
        "tm_end": 0.0,
        "tm_left": 0.0,
        "tm_done": False,
    }
    for key, value in defaults.items():
        s.setdefault(key, value)


def fmt(seconds):
    seconds = int(max(0, round(seconds)))
    h, rest = divmod(seconds, 3600)
    m, sec = divmod(rest, 60)
    return f"{h:02d}:{m:02d}:{sec:02d}"


def remaining_time():
    s = st.session_state
    if not s.get("tm_running", False):
        return None

    left = s.tm_end - time.time()
    if left <= 0:
        s.tm_running = False
        s.tm_left = 0.0
        s.tm_done = True
        return 0.0

    return left


def timer_start():
    s = st.session_state
    left = s.tm_left if s.tm_left > 0 else s.tm_min * 60 + s.tm_sec
    if left > 0:
        s.tm_end = time.time() + left
        s.tm_running = True
        s.tm_done = False


def timer_pause():
    s = st.session_state
    s.tm_left = max(0.0, s.tm_end - time.time())
    s.tm_running = False


def timer_reset():
    s = st.session_state
    s.tm_running = False
    s.tm_left = 0.0
    s.tm_done = False


def timer_display():
    s = st.session_state

    if s.tm_running:
        left = remaining_time()
        if left == 0:
            st.rerun()
    elif s.tm_left > 0:
        left = s.tm_left
    else:
        left = s.get("tm_min", 1) * 60 + s.get("tm_sec", 0)

    st.markdown(
        f"<h1 style='text-align:center; font-size:64px'>{fmt(left)}</h1>",
        unsafe_allow_html=True,
    )


live_timer_display = st.fragment(run_every=1)(timer_display)


def run():
    init()
    s = st.session_state
    st.title("⏱️ Timer")

    if s.tm_done:
        st.success("⏰ Time's up!")
        st.balloons()
        s.tm_done = False

    c1, c2 = st.columns(2)
    c1.number_input("Minutes", 0, 600, 1, key="tm_min", disabled=s.tm_running)
    c2.number_input("Seconds", 0, 59, 0, key="tm_sec", disabled=s.tm_running)
    if s.tm_running:
        live_timer_display()
    else:
        timer_display()

    b1, b2, b3 = st.columns(3)
    b1.button("▶️ Start", on_click=timer_start, disabled=s.tm_running, use_container_width=True)
    b2.button("⏸️ Pause", on_click=timer_pause, disabled=not s.tm_running, use_container_width=True)
    b3.button("🔄 Reset", on_click=timer_reset, use_container_width=True)
