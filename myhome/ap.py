import calendar as pycalendar
import html
from datetime import date, datetime

import psutil
import streamlit as st

import Notes
import gallery_app
import calculator_app
import timer_app
import music_app
import settings_app
import camera_app
from look import load_settings, save_settings, base_css, frame_css
from storage import read


st.set_page_config(page_title="My Phone", page_icon="📱", layout="wide")

settings = load_settings()
st.markdown(base_css(settings["dark"]), unsafe_allow_html=True)

s = st.session_state

if "page" not in s:
    s.page = "home"
if "locked" not in s:
    s.locked = settings["lock_on"]
if "pin_input" not in s:
    s.pin_input = ""
if "pin_msg" not in s:
    s.pin_msg = ""

today = date.today()
if "calendar_month" not in s:
    s.calendar_month = date(today.year, today.month, 1)

if s.locked and not settings["lock_on"]:
    s.locked = False


def go(page):
    s.page = page


def lock_phone():
    s.locked = True
    s.page = "home"
    s.pin_input = ""
    s.pin_msg = ""


def press_pin(key):
    pin = load_settings()["pin"]
    s.pin_msg = ""

    if key == "C":
        s.pin_input = ""
    elif key == "⌫":
        s.pin_input = s.pin_input[:-1]
    else:
        s.pin_input += key

        if len(s.pin_input) >= len(pin):
            if s.pin_input == pin:
                s.locked = False
                s.page = "home"
            else:
                s.pin_msg = "❌ Wrong PIN"

            s.pin_input = ""


def esc(text):
    return html.escape(str(text))


@st.fragment(run_every=60)
def status_bar():
    battery = psutil.sensors_battery()

    if battery is None:
        battery_text = "Battery unavailable"
    else:
        battery_icon = "⚡" if battery.power_plugged else "🔋"
        battery_text = f"{battery_icon} {battery.percent}%"

    st.markdown(
        f'<div class="status-bar"><strong>{esc(settings["phone_name"])}</strong>'
        f'<span>{battery_text}</span></div>',
        unsafe_allow_html=True,
    )


@st.fragment(run_every=10)
def clock_widget():
    now = datetime.now()

    st.markdown(
        f'<div class="widget">'
        f'<div class="clock-time">{now:%H:%M}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )


def change_calendar_month(amount):
    current = s.calendar_month
    month_index = current.month - 1 + amount
    year = current.year + month_index // 12
    month = month_index % 12 + 1
    s.calendar_month = date(year, month, 1)


def show_current_month():
    today = date.today()
    s.calendar_month = date(today.year, today.month, 1)


def calendar_widget():
    today = date.today()
    st.button(
        f"📅  {today.strftime('%A, %d %B')}",
        key="calendar_widget_button",
        on_click=go,
        args=("calendar",),
        use_container_width=True,
    )


def calendar_page():
    today = date.today()
    shown_month = s.calendar_month

    left, center, right = st.columns([1, 5, 1])

    with left:
        st.button(
            "◀",
            key="previous_month",
            on_click=change_calendar_month,
            args=(-1,),
            use_container_width=True,
        )

    with center:
        st.markdown(
            f"<div style='text-align:center; font-size:24px; "
            f"font-weight:bold; padding:5px 0;'>"
            f"📅 {shown_month.strftime('%B %Y')}</div>",
            unsafe_allow_html=True,
        )

    with right:
        st.button(
            "▶",
            key="next_month",
            on_click=change_calendar_month,
            args=(1,),
            use_container_width=True,
        )

    st.button("Today", key="go_to_today", on_click=show_current_month)

    weeks = pycalendar.Calendar(firstweekday=0).monthdatescalendar(
        shown_month.year,
        shown_month.month,
    )

    weekdays = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    headers = "".join(f'<th scope="col">{day}</th>' for day in weekdays)
    rows = []
    for week in weeks:
        cells = []
        for day in week:
            cell_class = ""
            if day == today:
                cell_class = ' class="calendar-today" aria-current="date"'
            elif day.month != shown_month.month:
                cell_class = ' class="calendar-other-month"'
            cells.append(f"<td{cell_class}>{day.day}</td>")
        rows.append("<tr>" + "".join(cells) + "</tr>")

    st.markdown(
        '<table class="phone-calendar" aria-label="Month calendar">'
        f"<thead><tr>{headers}</tr></thead><tbody>{''.join(rows)}</tbody></table>",
        unsafe_allow_html=True,
    )

    entries = read("diary", list)
    if entries:
        st.subheader("Photo diary")
        entry_date = st.date_input("Diary date", today)
        matches = [
            entry for entry in entries
            if entry["date"] == entry_date.isoformat()
        ]
        if not matches:
            st.caption("No photos for this date.")
        for entry in matches:
            photo = gallery_app.IMG_DIR / entry["photo"]
            if photo.is_file():
                st.image(str(photo), caption=entry["caption"])


def lock_screen():
    st.markdown(frame_css(settings), unsafe_allow_html=True)

    st.markdown(
        '<div style="text-align:center">'
        '<span class="applabel">🔒 Locked</span></div>',
        unsafe_allow_html=True,
    )

    clock_widget()

    pin_len = len(settings["pin"])
    dots = " ".join(
        "●" if i < len(s.pin_input) else "○"
        for i in range(pin_len)
    )
    st.markdown(
        f'<div style="text-align:center">'
        f'<span class="applabel" style="font-size:26px; letter-spacing:6px">'
        f'{dots}</span></div>',
        unsafe_allow_html=True,
    )

    if s.pin_msg:
        st.markdown(
            f'<div style="text-align:center">'
            f'<span class="applabel">{esc(s.pin_msg)}</span></div>',
            unsafe_allow_html=True,
        )
    elif settings["pin"] == "1234":
        st.markdown(
            '<div style="text-align:center">'
            '<span class="applabel">'
            'Hint: PIN is 1234 (change it in Settings)'
            '</span></div>',
            unsafe_allow_html=True,
        )

    rows = [
        ["1", "2", "3"],
        ["4", "5", "6"],
        ["7", "8", "9"],
        ["C", "0", "⌫"],
    ]

    with st.container(key="pin_pad"):
        for r, row in enumerate(rows):
            for c, (col, key) in enumerate(zip(st.columns(3, gap="small"), row)):
                col.button(
                    key,
                    key=f"pin_{r}{c}",
                    on_click=press_pin,
                    args=(key,),
                    use_container_width=True,
                )


APPS = [
    ("📝", "Notes", "notes"),
    ("🖼️", "Gallery", "gallery"),
    ("🧮", "Calculator", "calculator"),
    ("📊", "Data Explorer", "explorer"),
    ("📅", "Calendar", "calendar"),
    ("⏱️", "Timer", "timer"),
    ("🎵", "Music", "music"),
    ("⚙️", "Settings", "settings"),
    ("📷", "Camera", "camera"),
]


def home_timer():
    left = timer_app.remaining_time()
    if left == 0:
        st.rerun()
    if left is None and not s.get("tm_done", False):
        return

    label = (
        "⏰ Time’s up · Open Timer"
        if not left
        else f"⏳ {timer_app.fmt(left)} · Open Timer"
    )
    if st.button(label, key="home_timer", use_container_width=True):
        go("timer")
        st.rerun()


live_home_timer = st.fragment(run_every=1)(home_timer)


def quick_controls():
    with st.expander("Quick controls"):
        dark = st.toggle("Dark mode", value=settings["dark"], key="quick_dark")
        if dark != settings["dark"]:
            save_settings({"dark": dark})
            st.rerun()

        st.button("Wallpaper settings", on_click=go, args=("settings",))
        if settings["lock_on"]:
            st.button("Lock phone", on_click=lock_phone)


def home():
    st.markdown(frame_css(settings), unsafe_allow_html=True)

    status_bar()
    clock_widget()
    calendar_widget()
    if s.get("tm_running", False):
        live_home_timer()
    elif s.get("tm_done", False):
        home_timer()

    pending = [
        item for item in Notes.load(Notes.TODO_FILE)
        if item[0] == "TODO" and item[2] != "done"
    ]
    if pending:
        with st.container(key="home_task"):
            st.caption("Next task · " + esc(pending[0][3]))

    with st.container(key="app_grid"):
        for start in range(0, len(APPS), 3):
            row = APPS[start:start + 3]
            for col, (icon, name, page) in zip(st.columns(3, gap="small"), row):
                col.button(
                    icon,
                    key=f"app_{page}",
                    on_click=go,
                    args=(page,),
                    use_container_width=True,
                )
                col.caption(name)

    with st.container(key="quick_controls"):
        quick_controls()


apps = {
    "notes": Notes,
    "gallery": gallery_app,
    "calculator": calculator_app,
    "timer": timer_app,
    "music": music_app,
    "settings": settings_app,
}


if s.locked:
    lock_screen()
elif s.page == "home":
    home()
elif s.page == "calendar":
    with st.container(key="calendar_page"):
        st.button("← Home", on_click=go, args=("home",))
        calendar_page()
else:
    st.button("← Home", on_click=go, args=("home",))
    if s.page == "camera":
        camera_app.run(lambda: go("gallery"))
    elif s.page == "explorer":
        import dataexplorer

        dataexplorer.run()
    else:
        apps[s.page].run()
