"""Camelot Journey — web service.

Step 1 (this build): a landing screen where you upload a rekordbox history
.txt, with instructions on how to export it. The whole site uses an organic,
abstract-geometric look whose colour scheme is randomised on every page load.

Run:
    pip install -r requirements.txt
    python app.py
    # open http://127.0.0.1:5000
"""

import colorsys
import os
import random
import tempfile
import uuid
from pathlib import Path

from flask import (Flask, flash, redirect, render_template, request, session,
                   url_for)

import camelot_core as core

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-" + uuid.uuid4().hex)

UPLOAD_ROOT = Path(tempfile.gettempdir()) / "camelot_web_uploads"
UPLOAD_ROOT.mkdir(parents=True, exist_ok=True)

ALLOWED_EXT = {".txt", ".tsv", ".csv"}
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024  # 5 MB


# --------------------------------------------------------------------------- #
# Organic, randomised colour theme — new on every page load.
# --------------------------------------------------------------------------- #
def _hex(rgb):
    return "#%02x%02x%02x" % tuple(int(round(c * 255)) for c in rgb)


def _blob_radius():
    v = [random.randint(28, 72) for _ in range(8)]
    return "%d%% %d%% %d%% %d%% / %d%% %d%% %d%% %d%%" % tuple(v)


def make_theme():
    """Build a fresh, harmonious palette + organic blob field."""
    h0 = random.random()
    spread = random.uniform(0.06, 0.30)
    direction = random.choice((-1, 1))
    scheme = random.choice(("analogous", "analogous", "triadic", "split"))
    if scheme == "triadic":
        hues = [(h0 + k / 3.0) % 1.0 for k in range(4)]
    elif scheme == "split":
        hues = [h0, (h0 + 0.5 - 0.08) % 1.0, (h0 + 0.5 + 0.08) % 1.0,
                (h0 + spread) % 1.0]
    else:
        hues = [(h0 + direction * i * spread) % 1.0 for i in range(4)]

    dark = random.random() < 0.42

    accents = []
    for h in hues:
        s = random.uniform(0.52, 0.85)
        light = random.uniform(0.5, 0.64) if dark else random.uniform(0.54, 0.7)
        accents.append(_hex(colorsys.hls_to_rgb(h, light, s)))

    if dark:
        bg = _hex(colorsys.hls_to_rgb(h0, 0.10, 0.32))
        bg2 = _hex(colorsys.hls_to_rgb(hues[-1], 0.13, 0.30))
        surface = "rgba(28, 27, 32, 0.55)"
        text = "#f4f1ec"
        muted = "#b8b2aa"
        border = "rgba(255, 255, 255, 0.14)"
        card_shadow = "0 24px 60px rgba(0,0,0,0.45)"
    else:
        bg = _hex(colorsys.hls_to_rgb(h0, 0.955, 0.55))
        bg2 = _hex(colorsys.hls_to_rgb(hues[-1], 0.93, 0.5))
        surface = "rgba(255, 255, 255, 0.62)"
        text = "#1c1b1a"
        muted = "#6c665f"
        border = "rgba(0, 0, 0, 0.08)"
        card_shadow = "0 24px 60px rgba(40,30,20,0.16)"

    blobs = []
    for _ in range(6):
        blobs.append(dict(
            color=random.choice(accents),
            x=round(random.uniform(-12, 88), 1),
            y=round(random.uniform(-12, 88), 1),
            size=round(random.uniform(26, 54), 1),
            blur=round(random.uniform(28, 70), 1),
            opacity=round(random.uniform(0.28, 0.55) if dark
                          else random.uniform(0.4, 0.72), 2),
            radius=_blob_radius(),
            dur=round(random.uniform(20, 38), 1),
            delay=round(random.uniform(-24, 0), 1),
            drift=round(random.uniform(2, 7), 1),
        ))

    return dict(
        accents=accents, accent=accents[0], accent2=accents[1 % len(accents)],
        accent3=accents[2 % len(accents)],
        bg=bg, bg2=bg2, surface=surface, text=text, muted=muted, border=border,
        card_shadow=card_shadow, dark=dark, blobs=blobs,
        seed=uuid.uuid4().hex[:8],
    )


@app.context_processor
def inject_theme():
    # A new theme for every render -> colours change every time you open a page.
    return {"theme": make_theme()}


# --------------------------------------------------------------------------- #
# Routes
# --------------------------------------------------------------------------- #
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/upload", methods=["POST"])
def upload():
    f = request.files.get("history")
    if not f or not f.filename:
        flash("파일을 선택해 주세요.")
        return redirect(url_for("index"))

    ext = Path(f.filename).suffix.lower()
    if ext not in ALLOWED_EXT:
        flash("rekordbox에서 내보낸 .txt 파일을 올려 주세요.")
        return redirect(url_for("index"))

    sid = session.get("sid") or uuid.uuid4().hex
    session["sid"] = sid
    udir = UPLOAD_ROOT / sid
    udir.mkdir(parents=True, exist_ok=True)
    dest = udir / f"history{ext}"
    f.save(dest)

    try:
        df = core.parse_rekordbox_txt(dest)
    except Exception as exc:  # noqa: BLE001 - surface a friendly message
        flash(f"파일을 읽지 못했어요: {exc}")
        return redirect(url_for("index"))

    session["filename"] = f.filename
    session["history_path"] = str(dest)
    session["total"] = int(len(df))
    session["n_keyed"] = int(df["_camelot"].notna().sum())
    return redirect(url_for("loaded"))


@app.route("/loaded")
def loaded():
    path = session.get("history_path")
    if not path or not Path(path).exists():
        return redirect(url_for("index"))
    df = core.parse_rekordbox_txt(path)
    return render_template(
        "loaded.html",
        filename=session.get("filename", "history.txt"),
        total=int(len(df)),
        n_keyed=int(df["_camelot"].notna().sum()),
        tracklist=core.tracklist_text(df),
    )


if __name__ == "__main__":
    app.run(debug=True, port=int(os.environ.get("PORT", 5000)))
