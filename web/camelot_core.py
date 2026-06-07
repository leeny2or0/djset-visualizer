"""Core logic for the Camelot harmonic-journey web service.

Headless (Agg) port of the notebook `camelot_journey.ipynb`:
  - rekordbox history parsing
  - key <-> Camelot mapping
  - the wheel "harmonic journey" figure (3 designs)
  - the text tracklist sheet (25 tracks/page)

Figures are saved as PNG + SVG only (no PDF).
"""

import re
from pathlib import Path
from collections import defaultdict

import numpy as np
import pandas as pd
import matplotlib as mpl
mpl.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import patheffects
from matplotlib.colors import Normalize, LinearSegmentedColormap
from matplotlib.patches import Rectangle

try:
    from adjustText import adjust_text
except Exception:  # pragma: no cover - adjustText is optional but recommended
    def adjust_text(*a, **k):
        return 0

# --- coding-style monospace font with Korean + CJK fallbacks ----------------
mpl.rcParams.update({
    "font.family": ["Menlo", "Monaco", "DejaVu Sans Mono",
                    "Apple SD Gothic Neo", "Hiragino Sans GB",
                    "Consolas", "Courier New"],
    "mathtext.fontset": "stix",
    "svg.fonttype": "none",
})

R_INNER = 0.62   # A (minor)
R_OUTER = 1.00   # B (major)

KEY_TO_CAMELOT = {
    "Abm": "1A", "G#m": "1A", "Ebm": "2A", "D#m": "2A",
    "Bbm": "3A", "A#m": "3A", "Fm": "4A", "Cm": "5A", "Gm": "6A",
    "Dm": "7A", "Am": "8A", "Em": "9A", "Bm": "10A",
    "F#m": "11A", "Gbm": "11A", "C#m": "12A", "Dbm": "12A",
    "B": "1B", "F#": "2B", "Gb": "2B", "Db": "3B", "C#": "3B",
    "Ab": "4B", "G#": "4B", "Eb": "5B", "D#": "5B", "Bb": "6B", "A#": "6B",
    "F": "7B", "C": "8B", "G": "9B", "D": "10B", "A": "11B", "E": "12B",
}

CAMELOT_TO_KEY = {
    "1A": "Abm", "2A": "Ebm", "3A": "Bbm", "4A": "Fm",
    "5A": "Cm", "6A": "Gm", "7A": "Dm", "8A": "Am",
    "9A": "Em", "10A": "Bm", "11A": "F#m", "12A": "C#m",
    "1B": "B", "2B": "F#", "3B": "Db", "4B": "Ab",
    "5B": "Eb", "6B": "Bb", "7B": "F", "8B": "C",
    "9B": "G", "10B": "D", "11B": "A", "12B": "E",
}


def normalize_key(key_str):
    if key_str is None or (isinstance(key_str, float) and np.isnan(key_str)):
        return None
    s = str(key_str).strip()
    if not s:
        return None
    m = re.fullmatch(r"\s*(\d{1,2})\s*([AaBb])\s*", s)
    if m:
        n = int(m.group(1))
        if 1 <= n <= 12:
            return f"{n}{m.group(2).upper()}"
    s2 = s.replace("minor", "m").replace("Minor", "m")
    s2 = s2.replace("major", "").replace("Major", "").replace(" ", "")
    return KEY_TO_CAMELOT.get(s2)


def parse_rekordbox_txt(filepath):
    """Parse a rekordbox-exported history/playlist .txt (tab-separated)."""
    last_err = None
    df = None
    for enc in ("utf-16", "utf-16-le", "utf-8-sig", "utf-8", "cp949"):
        try:
            df = pd.read_csv(filepath, sep="\t", encoding=enc)
            break
        except (UnicodeDecodeError, UnicodeError) as e:
            last_err = e
            continue
    if df is None:
        raise last_err

    df.columns = [c.strip().lstrip("#").strip() for c in df.columns]
    key_col = next((c for c in df.columns if c.lower() in ("key", "tonality")), None)
    title_col = next((c for c in df.columns
                      if c.lower() in ("track title", "title", "name")), None)
    artist_col = next((c for c in df.columns if c.lower() == "artist"), None)
    if title_col is None or key_col is None:
        raise ValueError("Track Title / Key 컬럼을 찾지 못했습니다. "
                         "rekordbox에서 내보낸 히스토리 txt가 맞는지 확인해 주세요.")
    rename = {key_col: "Key", title_col: "Track Title"}
    if artist_col:
        rename[artist_col] = "Artist"
    df = df.rename(columns=rename)
    if "Artist" not in df.columns:
        df["Artist"] = ""
    df["_camelot"] = df["Key"].apply(normalize_key)
    return df


def camelot_xy(camelot):
    if camelot is None:
        return None
    n = int(camelot[:-1])
    ring = camelot[-1]
    r = R_INNER if ring == "A" else R_OUTER
    theta = np.deg2rad(90 - (n % 12) * 30)
    return r * np.cos(theta), r * np.sin(theta)


def jitter_overlaps(points, jitter_r=0.085):
    counts, indices = defaultdict(int), []
    for x, y in points:
        k = (round(x, 4), round(y, 4))
        indices.append(counts[k])
        counts[k] += 1
    out = []
    for i, (x, y) in enumerate(points):
        k = (round(x, 4), round(y, 4))
        total = counts[k]
        if total > 1:
            rr = jitter_r * (1.0 + 0.14 * max(0, total - 3))
            sub = 2 * np.pi * indices[i] / total
            out.append((x + rr * np.cos(sub), y + rr * np.sin(sub)))
        else:
            out.append((x, y))
    return out


# Single black & white (monochrome) design. Play order is encoded by greyscale
# value (light grey at the start -> black at the end) plus the number in each dot.
STYLES = {
    "bw": dict(
        fig_bg="white", ax_bg="white",
        cmap=LinearSegmentedColormap.from_list(
            "bw_order", ["#c7c7c7", "#7a7a7a", "#111111"]),
        ring="#d2d2d2", spoke="#e3e3e3", pos_label="#9a9a9a",
        point_size=170, num_fontsize=6.0, point_edge="#111111", point_edge_w=0.7,
        text="#111111", text_stroke="white", text_stroke_w=2.0,
        leader="#b0b0b0", glow=False,
    ),
}


def _save(fig, out_path, fig_bg, dpi=300):
    """Save a figure as PNG + SVG (no PDF). Returns {"png":path, "svg":path}."""
    out_path = Path(out_path)
    saved = {}
    png = out_path.with_suffix(".png")
    fig.savefig(png, dpi=dpi, facecolor=fig_bg)
    saved["png"] = png
    svg = out_path.with_suffix(".svg")
    fig.savefig(svg, facecolor=fig_bg)
    saved["svg"] = svg
    return saved


def tracklist_text(df, numbered=True, sep=" - "):
    """'Artist - Track Title' lines for pasting into a SoundCloud description."""
    lines = []
    for i, (_, row) in enumerate(df.reset_index(drop=True).iterrows()):
        artist = str(row.get("Artist") or "").strip()
        title = str(row.get("Track Title") or "").strip()
        body = f"{artist}{sep}{title}" if (artist and title) else (
            title or artist or f"Track {i + 1}")
        lines.append(f"{i + 1}. {body}" if numbered else body)
    return "\n".join(lines)


def plot_harmonic_journey(df, output_path, style="bw"):
    """Square 1:1 Camelot wheel journey plot. Saves PNG + SVG."""
    if style not in STYLES:
        raise ValueError(f"unknown style {style!r}")
    S = STYLES[style]

    df = df.reset_index(drop=True)
    valid = df.dropna(subset=["_camelot"]).reset_index(drop=True)
    raw_xy = [camelot_xy(c) for c in valid["_camelot"]]
    xy = jitter_overlaps(raw_xy)
    xs = np.array([p[0] for p in xy])
    ys = np.array([p[1] for p in xy])
    n_pts = len(xy)

    cmap = S["cmap"] if not isinstance(S["cmap"], str) else plt.get_cmap(S["cmap"])
    norm = Normalize(vmin=0, vmax=max(n_pts - 1, 1))

    fig = plt.figure(figsize=(9, 9), facecolor=S["fig_bg"])
    ax = fig.add_axes([0.04, 0.04, 0.92, 0.92])
    ax.set_facecolor(S["ax_bg"])
    ax.set_aspect("equal")
    LIM = 2.15
    ax.set_xlim(-LIM, LIM); ax.set_ylim(-LIM, LIM)
    ax.axis("off")

    th = np.linspace(0, 2 * np.pi, 400)
    for r in [R_INNER - 0.07, R_INNER + 0.07, R_OUTER - 0.07, R_OUTER + 0.07]:
        ax.plot(r * np.cos(th), r * np.sin(th), color=S["ring"], lw=0.6, zorder=0)
    for n in range(12):
        a = np.deg2rad(90 - n * 30 - 15)
        ax.plot([(R_INNER - 0.07) * np.cos(a), (R_OUTER + 0.07) * np.cos(a)],
                [(R_INNER - 0.07) * np.sin(a), (R_OUTER + 0.07) * np.sin(a)],
                color=S["spoke"], lw=0.45, zorder=0)

    R_LBL_A = R_INNER - 0.135
    R_LBL_B = R_OUTER + 0.135
    for n in range(1, 13):
        a = np.deg2rad(90 - (n % 12) * 30)
        ax.text(R_LBL_A * np.cos(a), R_LBL_A * np.sin(a), CAMELOT_TO_KEY[f"{n}A"],
                ha="center", va="center", color=S["pos_label"], fontsize=8.5)
        ax.text(R_LBL_B * np.cos(a), R_LBL_B * np.sin(a), CAMELOT_TO_KEY[f"{n}B"],
                ha="center", va="center", color=S["pos_label"], fontsize=8.5)

    dot_r_pt = (S["point_size"] / np.pi) ** 0.5
    shrink = dot_r_pt + 2.5
    for i in range(n_pts - 1):
        c = cmap(norm(i))
        if S["glow"]:
            ax.plot([xs[i], xs[i + 1]], [ys[i], ys[i + 1]], color=c, lw=5.5,
                    alpha=0.18, solid_capstyle="round", zorder=1)
        ax.annotate("", zorder=2, xy=(xs[i + 1], ys[i + 1]), xytext=(xs[i], ys[i]),
                    arrowprops=dict(arrowstyle="-|>", color=c, lw=1.1, alpha=0.95,
                                    mutation_scale=10, shrinkA=shrink, shrinkB=shrink))

    sc_colors = [cmap(norm(i)) for i in range(n_pts)]
    if S["glow"]:
        ax.scatter(xs, ys, s=S["point_size"] * 3.2, c=sc_colors, alpha=0.16,
                   linewidths=0, zorder=2)
    ax.scatter(xs, ys, s=S["point_size"], c=sc_colors, edgecolors=S["point_edge"],
               linewidths=S["point_edge_w"], zorder=3)
    for i in range(n_pts):
        r_, g_, b_ = cmap(norm(i))[:3]
        lum = 0.299 * r_ + 0.587 * g_ + 0.114 * b_
        num_c = "#15191f" if lum > 0.6 else "#ffffff"
        stroke_c = "#ffffff" if lum > 0.6 else "#0a0d12"
        ax.text(xs[i], ys[i], str(i + 1), ha="center", va="center", zorder=4,
                fontsize=S["num_fontsize"], color=num_c, fontweight="bold",
                path_effects=[patheffects.withStroke(linewidth=0.8, foreground=stroke_c)])

    obstacle_x = list(xs); obstacle_y = list(ys)
    for n in range(1, 13):
        a = np.deg2rad(90 - (n % 12) * 30)
        obstacle_x.append(R_LBL_A * np.cos(a)); obstacle_y.append(R_LBL_A * np.sin(a))
        obstacle_x.append(R_LBL_B * np.cos(a)); obstacle_y.append(R_LBL_B * np.sin(a))
    for theta in np.linspace(0, 2 * np.pi, 60, endpoint=False):
        obstacle_x.append(R_OUTER * np.cos(theta))
        obstacle_y.append(R_OUTER * np.sin(theta))

    R_LABEL_INIT = R_OUTER + 0.32
    base_angles = np.arctan2(ys, xs)
    order = np.argsort(base_angles)
    sorted_a = base_angles[order].astype(float).copy()
    MIN_GAP = np.deg2rad(7.0)
    for k in range(1, len(order)):
        if sorted_a[k] - sorted_a[k - 1] < MIN_GAP:
            sorted_a[k] = sorted_a[k - 1] + MIN_GAP
    label_angles = np.zeros_like(base_angles, dtype=float)
    for k, i in enumerate(order):
        label_angles[i] = sorted_a[k]

    texts = []
    for i in range(n_pts):
        artist = str(valid.iloc[i].get("Artist") or "").strip()
        title_ = str(valid.iloc[i].get("Track Title") or "").strip()
        label = f"{artist} — {title_}".strip(" —-·").strip() or f"Track {i + 1}"
        full = f"{i + 1}. {label}"
        lx = R_LABEL_INIT * np.cos(label_angles[i])
        ly = R_LABEL_INIT * np.sin(label_angles[i])
        t = ax.text(lx, ly, full, fontsize=7.4, color=S["text"], ha="center",
                    va="center", zorder=5, clip_on=False,
                    path_effects=[patheffects.withStroke(
                        linewidth=S["text_stroke_w"], foreground=S["text_stroke"])])
        texts.append(t)

    adjust_text(texts, ax=ax, x=obstacle_x, y=obstacle_y, expand=(1.3, 1.5),
                arrowprops=dict(arrowstyle="-", color=S["leader"], lw=0.5,
                                alpha=0.85, shrinkA=2, shrinkB=4),
                target_x=list(xs), target_y=list(ys), force_text=(0.6, 0.8),
                force_static=(0.3, 0.4), force_pull=(0.0, 0.0),
                max_move=60, iter_lim=600)

    MIN_R = R_OUTER + 0.18
    for t in texts:
        px, py = t.get_position()
        r = np.hypot(px, py)
        if r < MIN_R:
            t.set_position((px / r * MIN_R, py / r * MIN_R) if r > 1e-6 else (0, MIN_R))

    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    inv = ax.transData.inverted()
    reach = LIM
    for t in ax.texts:
        if not t.get_text():
            continue
        bb = t.get_window_extent(renderer=renderer)
        for corner in ((bb.x0, bb.y0), (bb.x1, bb.y1), (bb.x0, bb.y1), (bb.x1, bb.y0)):
            dx, dy = inv.transform(corner)
            reach = max(reach, abs(dx), abs(dy))
    reach *= 1.03
    ax.set_xlim(-reach, reach); ax.set_ylim(-reach, reach)

    saved = _save(fig, output_path, S["fig_bg"])
    plt.close(fig)
    return saved


def plot_tracklist(df, output_path, style="bw", per_page=25):
    """Text tracklist sheet(s): Track Title | Artist | BPM | Key. PNG + SVG.

    Returns {"page1": {"png":..,"svg":..}, "page2": {...}, ...}.
    """
    if style not in STYLES:
        raise ValueError(f"unknown style {style!r}")
    S = STYLES[style]

    df = df.reset_index(drop=True)
    n = len(df)
    n_pages = max(1, (n + per_page - 1) // per_page)

    bg = mpl.colors.to_rgb(S["fig_bg"])
    bg_lum = 0.299 * bg[0] + 0.587 * bg[1] + 0.114 * bg[2]
    stripe = "#ffffff" if bg_lum < 0.5 else "#000000"

    X_TITLE, X_ARTIST, X_BPM, X_KEY = 0.045, 0.520, 0.880, 0.965
    MAXW_TITLE = X_ARTIST - X_TITLE - 0.020
    MAXW_ARTIST = X_BPM - 0.040 - X_ARTIST

    def fit_text(ax, renderer, fig, x, y, s, ha, base_fs, max_w):
        t = ax.text(x, y, s, ha=ha, va="center", transform=ax.transAxes,
                    fontsize=base_fs, color=S["text"], zorder=3)
        if s:
            w = t.get_window_extent(renderer=renderer).width / fig.bbox.width
            if w > max_w and w > 0:
                t.set_fontsize(base_fs * max_w / w)
        return t

    output_path = Path(output_path)
    saved = {}
    for pg in range(n_pages):
        chunk = df.iloc[pg * per_page:(pg + 1) * per_page]
        fig = plt.figure(figsize=(9, 9), facecolor=S["fig_bg"])
        ax = fig.add_axes([0, 0, 1, 1])
        ax.set_facecolor(S["ax_bg"])
        ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis("off")
        fig.canvas.draw()
        renderer = fig.canvas.get_renderer()

        for x, s, ha in ((X_TITLE, "TRACK TITLE", "left"), (X_ARTIST, "ARTIST", "left"),
                         (X_BPM, "BPM", "right"), (X_KEY, "KEY", "right")):
            ax.text(x, 0.955, s, ha=ha, va="center", transform=ax.transAxes,
                    fontsize=8.5, color=S["pos_label"], fontweight="bold", zorder=3)
        if n_pages > 1:
            ax.text(X_KEY, 0.985, f"{pg + 1} / {n_pages}", ha="right", va="center",
                    transform=ax.transAxes, fontsize=7.5, color=S["pos_label"])
        ax.plot([X_TITLE, X_KEY], [0.935, 0.935], color=S["ring"], lw=0.8,
                transform=ax.transAxes, zorder=1)

        y_first, y_bottom = 0.905, 0.035
        step = (y_first - y_bottom) / per_page
        for r, (_, row) in enumerate(chunk.iterrows()):
            y = y_first - r * step
            if r % 2 == 1:
                ax.add_patch(Rectangle((0.030, y - step / 2), 0.945, step,
                                       transform=ax.transAxes, facecolor=stripe,
                                       alpha=0.045, edgecolor="none", zorder=0))
            title = str(row.get("Track Title") or "").strip()
            artist = str(row.get("Artist") or "").strip()
            bpm = row.get("BPM")
            try:
                bpm_s = f"{float(bpm):.0f}" if pd.notna(bpm) else ""
            except (TypeError, ValueError):
                bpm_s = str(bpm or "").strip()
            key_s = CAMELOT_TO_KEY.get(normalize_key(row.get("Key")),
                                       str(row.get("Key") or "").strip())
            fit_text(ax, renderer, fig, X_TITLE, y, title, "left", 9.2, MAXW_TITLE)
            fit_text(ax, renderer, fig, X_ARTIST, y, artist, "left", 8.6, MAXW_ARTIST)
            ax.text(X_BPM, y, bpm_s, ha="right", va="center", transform=ax.transAxes,
                    fontsize=8.6, color=S["text"], zorder=3)
            ax.text(X_KEY, y, key_s, ha="right", va="center", transform=ax.transAxes,
                    fontsize=8.6, color=S["text"], zorder=3)

        suffix = f"_p{pg + 1}" if n_pages > 1 else ""
        base = output_path.with_name(output_path.stem + suffix)
        saved[f"page{pg + 1}"] = _save(fig, base, S["fig_bg"])
        plt.close(fig)
    return saved
