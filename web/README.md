# Camelot Journey — web service

The notebook (`../camelot_journey.ipynb`) turned into a small web app. You
upload a rekordbox history `.txt` and (eventually) get the harmonic-journey
wheel and the text tracklist sheet back.

The whole UI uses an **organic, abstract-geometric** look whose **colour scheme
is randomised on every page load** (soft morphing blobs + faint geometry).

## 여는 방법 (둘 중 하나)

1. **그냥 더블클릭** — `web/index.html` 를 브라우저로 열면 됩니다. 서버 없이
   동작하는 정적 페이지로, 업로드한 히스토리 `.txt` 를 **브라우저 안에서** 파싱해
   "아티스트 - 트랙명" 트랙리스트를 만들어 줍니다 (SoundCloud 소개글 복붙용).
   > ⚠️ `templates/` 안의 `.html` 은 Flask 서버용 템플릿이라 더블클릭하면
   > CSS가 안 먹습니다. **반드시 `web/index.html` 을 여세요.**

2. **서버로 실행** — 휠/트랙리스트 이미지 생성까지 쓰려면 아래 "Run locally".

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
