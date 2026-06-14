# Camelot Journey — web service

The notebook (`../camelot_journey.ipynb`) turned into a small web app. You
upload a rekordbox history `.txt` and (eventually) get the harmonic-journey
wheel and the text tracklist sheet back.

The UI is **black and minimal** — titles in **BBH Bartle** (Google Fonts),
body in **Consolas** (with a Korean fallback). On the result page the harmonic
wheel's dot **colormap is selectable** from a dropdown.

## 여는 방법

`web/index.html` 하나만 있으면 됩니다. **서버 없이** (그냥 더블클릭하거나, FTP/정적
호스팅에 올려서) 모든 기능이 동작합니다:

- 히스토리 `.txt` 파싱 + **중복 제거**
- **SoundCloud "아티스트 - 트랙명" 텍스트 리스트** (번호/정렬 6가지)
- **휠 이미지** + **인스타용 트랙리스트 이미지** 생성·다운로드(PNG·SVG) —
  파이썬(matplotlib)을 **브라우저 안에서**(Pyodide·WebAssembly) 돌립니다.
  최초 1회는 런타임을 받느라 시간이 조금 걸리고, 그다음부터는 캐시되어 빨라집니다.

> 파일은 어디에도 업로드되지 않고 브라우저 안에서만 처리됩니다.
> `templates/` 안의 `.html` 은 Flask 서버 전용 템플릿이라 더블클릭하면 CSS가
> 안 먹습니다 — **`web/index.html` 을 여세요.**

### (선택) Flask 서버로 실행
이미지를 **서버에서** 미리 만들어 두고 싶으면(브라우저 런타임 다운로드 없이) 아래
"Run locally"로 Flask 앱을 띄울 수도 있습니다. 정적 페이지와 결과는 동일합니다.

## Status

- 정적 페이지(`web/index.html`)가 **단독으로** 전 기능 제공 — 텍스트 리스트 +
  휠/트랙리스트 이미지(Pyodide). FTP/정적 호스팅 OK.
- Flask 앱(`app.py`)은 같은 기능을 **서버 사이드**로 제공(선택). 핵심 로직은
  `camelot_core.py` 한 곳에 있고, 정적 페이지는 이를 그대로 브라우저에서 import 합니다.

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
