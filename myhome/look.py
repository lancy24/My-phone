import base64
import io
from pathlib import Path

import streamlit as st
from PIL import Image

from storage import legacy_settings, read, update


DEFAULTS = {
    "phone_name": "My Phone",
    "wallpaper": "Rose Linen",
    "dark": False,
    "lock_on": True,
    "pin": "1234",
}

WALLPAPERS = {
    "Rose Linen": "radial-gradient(ellipse at 10% 10%, #fff7ed 0%, transparent 55%), linear-gradient(155deg, #f8e8dc 10%, #edc7c5 100%)",
    "Aurora": "radial-gradient(ellipse at 95% 12%, #127d78 0%, transparent 45%), radial-gradient(ellipse at 0% 68%, #30467a 0%, transparent 50%), linear-gradient(155deg, #0a152e 0%, #12213b 100%)",
    "Pink Sunset": "linear-gradient(160deg, #ffe4ec 0%, #ffb3c9 55%, #ff80ab 100%)",
    "Lavender Sky": "linear-gradient(160deg, #f1ebff 0%, #cdbbff 100%)",
    "Ocean": "linear-gradient(160deg, #e3f7ff 0%, #8fd0f2 100%)",
    "Mint": "linear-gradient(160deg, #e6fff2 0%, #96e8bf 100%)",
    "Midnight": "linear-gradient(160deg, #1b1035 0%, #5b4b9a 100%)",
}


def load_settings():
    return {**DEFAULTS, **read("settings", legacy_settings)}


def save_settings(settings):
    update("settings", legacy_settings, lambda current: {**current, **settings})


@st.cache_data
def photo_background(path, mtime):
    """Make a smaller gallery photo for use as a CSS background."""
    img = Image.open(path).convert("RGB")
    img.thumbnail((700, 1000))

    buf = io.BytesIO()
    img.save(buf, "JPEG", quality=80)

    b64 = base64.b64encode(buf.getvalue()).decode()
    return f"url(data:image/jpeg;base64,{b64})"


def wallpaper_background(settings):
    wp = settings["wallpaper"]

    if wp.startswith("img:") and Path(wp[4:]).name == wp[4:]:
        path = Path("images") / wp[4:]

        try:
            return photo_background(str(path), path.stat().st_mtime)
        except OSError:
            pass

    return WALLPAPERS.get(wp, WALLPAPERS[DEFAULTS["wallpaper"]])


def base_css(dark):
    palette = (
        ("#241e20", "#342a2d", "#faeeea", "#d1b9ba", "#965265", "#564045")
        if dark else
        ("#faf5f1", "#fffdfa", "#39292d", "#70555b", "#965265", "#e6d4cf")
    )
    bg, surface, ink, muted, accent, line = palette

    return f"""
    <style>
    .stApp {{
        --phone-bg: {bg};
        --phone-surface: {surface};
        --phone-text: {ink};
        --phone-muted: {muted};
        --phone-accent: {accent};
        --phone-line: {line};
        background: var(--phone-bg);
        color: var(--phone-text);
    }}
    [data-testid="stHeader"] {{ background: transparent; }}
    .block-container {{ max-width: 900px; padding-top: 3.25rem; }}
    .stApp :is(h1, h2, h3, label, [data-testid="stMarkdownContainer"]) {{
        color: var(--phone-text);
    }}
    .stApp [data-testid="stCaptionContainer"] p {{
        color: var(--phone-muted);
    }}
    .stApp :is(.stButton, .stDownloadButton, .stFormSubmitButton, [data-testid="stPopover"]) > button {{
        border-radius: 13px;
        border-color: var(--phone-line);
        background: var(--phone-surface);
        color: var(--phone-text);
    }}
    .stApp :is(.stButton, .stFormSubmitButton) > button:hover {{
        border-color: var(--phone-accent);
        background: var(--phone-accent);
        color: #fff;
    }}
    .stApp button:focus-visible {{
        outline: 2px solid #b87386;
        outline-offset: 2px;
    }}
    .stApp :is([data-baseweb="input"], [data-baseweb="textarea"], [data-baseweb="select"] > div,
               [data-testid="stFileUploaderDropzone"], [data-testid="stExpander"] details) {{
        background: var(--phone-surface);
        color: var(--phone-text);
    }}
    .stApp :is(input, textarea) {{ color: var(--phone-text); }}
    .stApp .phone-calendar {{
        width: 100%;
        table-layout: fixed;
        border-collapse: separate;
        border-spacing: 0.2rem;
    }}
    .stApp .phone-calendar :is(th, td) {{
        padding: 0.4rem 0.1rem;
        text-align: center;
        border: 0;
        color: var(--phone-text);
    }}
    .stApp .phone-calendar .calendar-other-month {{ color: var(--phone-muted); }}
    .stApp .phone-calendar .calendar-today {{
        background: var(--phone-accent);
        color: #fff;
        border-radius: 0.55rem;
        font-weight: 700;
    }}
    .stApp .st-key-calculator_pad {{ max-width: 360px; margin-inline: auto; }}
    .stApp .st-key-calculator_pad [data-testid="stHorizontalBlock"] {{
        display: grid;
        grid-template-columns: repeat(4, minmax(0, 1fr));
        gap: 0.5rem;
    }}
    .stApp .st-key-calculator_pad [data-testid="stColumn"] {{ width: 100%; min-width: 0; }}
    .stApp .st-key-calculator_pad button {{ min-width: 0; min-height: 44px; padding-inline: 0.25rem; }}
    @media (max-width: 600px) {{
        .stApp .block-container {{ padding-inline: clamp(0.65rem, 4vw, 1rem); }}
        .stApp .st-key-calendar_page [data-testid="stHorizontalBlock"] {{
            display: grid;
            grid-template-columns: auto minmax(0, 1fr) auto;
            gap: 0.25rem;
        }}
        .stApp .st-key-calendar_page [data-testid="stColumn"] {{ width: 100%; min-width: 0; }}
        .stApp .phone-calendar {{ font-size: 0.78rem; }}
    }}
    </style>
    """


def frame_css(settings):
    """Use the selected wallpaper behind the home and PIN screens."""
    bg = wallpaper_background(settings)
    wallpaper = settings["wallpaper"]
    dark_wallpaper = wallpaper in {"Aurora", "Midnight"} or wallpaper.startswith("img:")
    overlay = "linear-gradient(#20121780, #20121780), " if dark_wallpaper else ""
    ink = "#fff9f5" if dark_wallpaper else "#39292d"

    return f"""
    <style>
    .stApp .block-container {{
        max-width: 320px;
        width: calc(100% - 1rem);
        min-height: min(608px, calc((100vw - 1rem) * 1.9));
        height: auto;
        box-sizing: border-box;
        margin: 3rem auto 1rem;
        border: 5px solid #674c51;
        border-radius: 30px;
        padding: 1.75rem clamp(0.55rem, 3vw, 0.9rem) 1.75rem;
        position: relative;
        --frame-ink: {ink};
        background: {overlay}{bg};
        background-size: cover;
        background-position: center;
        box-shadow: 0 12px 32px #674c5126;
    }}
    .stApp .block-container::before {{
        content: "";
        position: absolute;
        top: 9px;
        left: 50%;
        transform: translateX(-50%);
        width: 44px;
        height: 5px;
        border-radius: 10px;
        background: #674c51;
    }}
    .stApp .block-container > [data-testid="stVerticalBlock"] {{
        gap: 0.65rem;
    }}
    .stApp :is(.widget, .status-bar, .applabel) {{
        color: var(--frame-ink);
        background: transparent;
    }}
    .widget {{
        text-align: center;
        font-variant-numeric: tabular-nums;
    }}
    .clock-time {{
        font-size: clamp(2rem, 12vw, 3.7rem);
        font-weight: 700;
        line-height: 1.1;
    }}
    .applabel {{ display: inline-block; padding: 0.2rem 0; }}
    .status-bar {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        flex-wrap: wrap;
        gap: 0.35rem;
        padding: 0.2rem 0.15rem;
        font-size: 0.875rem;
        overflow-wrap: anywhere;
    }}
    .stApp .st-key-home_task [data-testid="stCaptionContainer"] p {{
        color: var(--frame-ink);
        overflow-wrap: anywhere;
    }}
    .stApp :is(.st-key-app_grid, .st-key-pin_pad) [data-testid="stHorizontalBlock"] {{
        display: grid;
        grid-template-columns: repeat(3, minmax(0, 1fr));
        gap: 0.45rem;
    }}
    .stApp :is(.st-key-app_grid, .st-key-pin_pad) [data-testid="stColumn"] {{
        width: 100%;
        min-width: 0;
    }}
    .stApp :is(.st-key-app_grid, .st-key-pin_pad) button {{
        width: 100%;
        min-width: 0;
        min-height: 52px;
        padding: 0.3rem;
    }}
    .stApp .st-key-app_grid [data-testid="stHorizontalBlock"] {{
        gap: 0.5rem;
    }}
    .stApp .st-key-app_grid {{
        padding-bottom: 0.75rem;
    }}
    .stApp .st-key-app_grid [data-testid="stColumn"] {{
        padding-bottom: 0.4rem;
    }}
    .stApp .st-key-app_grid button {{
        min-height: 48px;
        padding: 0.35rem 0.25rem;
    }}
    .stApp .st-key-app_grid [data-testid="stColumn"] [data-testid="stVerticalBlock"] {{
        gap: 0.2rem;
    }}
    .stApp .st-key-app_grid button p {{
        margin: 0;
        font-size: 1.2rem;
    }}
    .stApp .st-key-app_grid [data-testid="stCaptionContainer"] p {{
        margin: 0;
        text-align: center;
        color: var(--frame-ink);
        line-height: 1.2;
        white-space: normal;
        overflow-wrap: anywhere;
        font-size: 0.75rem;
    }}
    .stApp .st-key-quick_controls [data-testid="stExpander"] summary {{
        min-height: 0;
        padding: 0.3rem 0.55rem;
    }}
    .stApp .st-key-quick_controls [data-testid="stExpanderDetails"] {{
        padding: 0.35rem 0.55rem 0.5rem;
    }}
    .stApp .st-key-quick_controls [data-testid="stVerticalBlock"] {{
        gap: 0.3rem;
    }}
    .stApp .st-key-quick_controls button {{
        min-height: 32px;
        padding: 0.15rem 0.5rem;
    }}
    .stApp .st-key-quick_controls p {{
        font-size: 0.8rem;
    }}
    .stApp .block-container::after {{
        content: "";
        position: absolute;
        bottom: 9px;
        left: 50%;
        transform: translateX(-50%);
        width: 82px;
        height: 4px;
        background: var(--frame-ink);
        border-radius: 50px;
        pointer-events: none;
    }}
    @media (max-width: 360px) {{
        .stApp .block-container {{
            margin-top: 2.75rem;
            border-width: 3px;
            padding-inline: 0.65rem;
        }}
        .stApp .st-key-app_grid [data-testid="stHorizontalBlock"] {{ gap: 0.35rem; }}
    }}
    </style>
    """
