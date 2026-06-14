"""In-browser (Pyodide) driver for image generation.

Runs inside Pyodide and reuses camelot_core.py. JS calls these functions and
gets JSON back (PNG as base64, SVG as text). Also runs fine under normal
CPython, which is how the logic is unit-tested.
"""

import base64
import json
import os

import camelot_core as core

_state = {"df": None}
_OUT = "/tmp/camelot"


def _ensure_dir():
    os.makedirs(_OUT, exist_ok=True)


def _b64(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("ascii")


def setup_fonts(ttf_path):
    """Register a CJK/Korean font so non-Latin track titles aren't tofu.

    Pyodide's matplotlib only ships DejaVu (no Hangul); we add a Korean font
    and use it as a per-glyph fallback after a monospace Latin face.
    """
    import matplotlib as mpl
    from matplotlib import font_manager as fm
    fm.fontManager.addfont(ttf_path)
    name = fm.FontProperties(fname=ttf_path).get_name()
    mpl.rcParams["font.family"] = ["DejaVu Sans Mono", name]
    return name


def load_history(data):
    """data: bytes-like of the uploaded .txt. Parses + dedupes; caches df."""
    _ensure_dir()
    with open(_OUT + "/history.txt", "wb") as f:
        f.write(bytes(data))
    df = core.parse_rekordbox_txt(_OUT + "/history.txt")
    df, removed = core.dedupe_tracks(df)
    _state["df"] = df
    return json.dumps({
        "total": int(len(df)),
        "n_keyed": int(df["_camelot"].notna().sum()),
        "removed": int(removed),
    })


def gen_wheel(cmap):
    """Generate the wheel with the given colormap; return base64 PNG + SVG."""
    df = _state["df"]
    core.plot_harmonic_journey(df, _OUT + "/wheel.png", cmap=cmap)
    return json.dumps({
        "png": _b64(_OUT + "/wheel.png"),
        "svg": open(_OUT + "/wheel.svg", encoding="utf-8").read(),
    })


def gen_tracklist():
    """Generate the tracklist sheet page(s); return a list of {png, svg}."""
    df = _state["df"]
    pages = core.plot_tracklist(df, _OUT + "/tracklist.png")
    out = []
    for _, files in pages.items():
        out.append({
            "png": _b64(str(files["png"])),
            "svg": open(str(files["svg"]), encoding="utf-8").read(),
        })
    return json.dumps(out)


def tracklist_text(mode):
    """Return the SoundCloud text list for the cached df (server-equivalent)."""
    return core.tracklist_text(_state["df"], mode=mode)
