# Camelot Journey — web service

The notebook (`../camelot_journey.ipynb`) turned into a small web app. You
upload a rekordbox history `.txt` and (eventually) get the harmonic-journey
wheel and the text tracklist sheet back.

The whole UI uses an **organic, abstract-geometric** look whose **colour scheme
is randomised on every page load** (soft morphing blobs + faint geometry).

## Status

- **Step 1 (done):** landing screen — upload box + "how to export your
  rekordbox history" instructions. Uploads are parsed and validated; the
  `/loaded` screen confirms how many tracks were read.
- Next steps (design picker, wheel + tracklist generation/download) build on
  `camelot_core.py`, which already ports the full notebook logic
  (`plot_harmonic_journey`, `plot_tracklist`) — PNG + SVG only, no PDF.

## Run locally

```bash
cd "djset visualizer/web"
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python app.py
# open http://127.0.0.1:5000
```

## Files

| file | purpose |
|---|---|
| `app.py` | Flask app: routes + the per-load random colour theme |
| `camelot_core.py` | headless port of the notebook (parsing + both figures) |
| `templates/` | `base.html` (organic background), `index.html` (upload), `loaded.html` |
| `static/css/style.css` | the organic / glassmorphic styling |
| `static/js/main.js` | drag & drop, filename display, colour reshuffle |
