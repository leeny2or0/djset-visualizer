"""Camelot Journey — web service.

Upload a rekordbox history .txt; the site (black, minimal — BBH Bartle titles,
Consolas body) removes duplicate tracks and generates the harmonic wheel image
(with a selectable dot colormap), the Instagram tracklist sheet, and the
SoundCloud text list, all downloadable.

Run:
    pip install -r requirements.txt
    python app.py
    # open http://127.0.0.1:5000
"""

import os
import tempfile
import uuid
from pathlib import Path

from flask import (Flask, abort, flash, redirect, render_template, request,
                   send_file, session, url_for)

import camelot_core as core

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-" + uuid.uuid4().hex)

UPLOAD_ROOT = Path(tempfile.gettempdir()) / "camelot_web_uploads"
UPLOAD_ROOT.mkdir(parents=True, exist_ok=True)

ALLOWED_EXT = {".txt", ".tsv", ".csv"}
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024  # 5 MB


# Colormaps offered in the wheel's "점 컬러맵" dropdown (value -> label).
CMAPS = [
    ("bw", "흑백 (기본)"),
    ("viridis", "Viridis"),
    ("plasma", "Plasma"),
    ("magma", "Magma"),
    ("inferno", "Inferno"),
    ("cividis", "Cividis"),
    ("turbo", "Turbo"),
    ("cool", "Cool"),
    ("coolwarm", "Cool–Warm"),
    ("Spectral", "Spectral"),
]
CMAP_VALUES = {v for v, _ in CMAPS}


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
    for old in udir.glob("*"):  # clear previous run's images
        if old.suffix.lower() in (".png", ".svg"):
            old.unlink()
    dest = udir / f"history{ext}"
    f.save(dest)

    try:
        df = core.parse_rekordbox_txt(dest)
    except Exception as exc:  # noqa: BLE001 - surface a friendly message
        flash(f"파일을 읽지 못했어요: {exc}")
        return redirect(url_for("index"))

    df, removed = core.dedupe_tracks(df)

    # generate the default (black & white) wheel + Instagram tracklist sheet
    try:
        core.plot_harmonic_journey(df, udir / "wheel_bw.png", cmap="bw")
        pages = core.plot_tracklist(df, udir / "tracklist.png")
    except Exception as exc:  # noqa: BLE001
        flash(f"이미지를 만들지 못했어요: {exc}")
        return redirect(url_for("index"))

    session["filename"] = f.filename
    session["history_path"] = str(dest)
    session["total"] = int(len(df))
    session["n_keyed"] = int(df["_camelot"].notna().sum())
    session["removed"] = int(removed)
    session["cmap"] = "bw"
    session["pages"] = [{k: Path(v).name for k, v in pg.items()}
                        for pg in pages.values()]
    return redirect(url_for("result"))


@app.route("/result")
def result():
    path = session.get("history_path")
    sid = session.get("sid")
    if not sid or not path or not Path(path).exists() or "pages" not in session:
        return redirect(url_for("index"))

    cmap = request.args.get("cmap", session.get("cmap", "bw"))
    if cmap not in CMAP_VALUES:
        cmap = "bw"
    session["cmap"] = cmap

    df = core.parse_rekordbox_txt(path)
    df, _ = core.dedupe_tracks(df)

    # generate the wheel for this colormap on demand (cached by filename)
    udir = UPLOAD_ROOT / sid
    wheel_png = udir / f"wheel_{cmap}.png"
    if not wheel_png.exists():
        core.plot_harmonic_journey(df, wheel_png, cmap=cmap)
    wheel = {"png": wheel_png.name, "svg": wheel_png.with_suffix(".svg").name}

    return render_template(
        "result.html",
        filename=session.get("filename", "history.txt"),
        total=session.get("total"),
        n_keyed=session.get("n_keyed"),
        removed=session.get("removed", 0),
        wheel=wheel,
        cmaps=CMAPS,
        cmap=cmap,
        pages=session.get("pages", []),
        tracklist=core.tracklist_text(df),
    )


@app.route("/file/<path:name>")
def file(name):
    """Serve a generated image from the current session's folder."""
    sid = session.get("sid")
    if not sid:
        abort(404)
    safe = Path(name).name
    target = UPLOAD_ROOT / sid / safe
    if not target.exists():
        abort(404)
    return send_file(target, as_attachment=request.args.get("dl") == "1",
                     download_name=safe)


if __name__ == "__main__":
    app.run(debug=True, port=int(os.environ.get("PORT", 5000)))
