// Camelot Journey — client-side i18n. Default English; top-right KO/EN toggle.
// Translatable elements carry data-i18n="key"; values may contain HTML.
(function () {
  "use strict";

  var DICT = {
    en: {
      "idx.title": "Map the flow<br>of your DJ&nbsp;set.",
      "idx.sub": "Upload your rekordbox history file and get a tracklist for your SoundCloud description.",
      "idx.dropTitle": "Drag your history file here, or click to choose",
      "idx.dropHint": "A <code>.txt</code> exported from rekordbox (tab-separated)",
      "idx.start": "Start →",
      "idx.formNote": "Duplicate tracks are removed automatically. Generating the wheel &amp; tracklist images takes a few seconds.",
      "idx.howTitle": "How to export your history file from rekordbox",
      "idx.s1b": "Open Histories",
      "idx.s1p": "In the rekordbox left sidebar, open <code>Histories</code> and select the session for the date you want.",
      "idx.s2b": "Show the needed columns",
      "idx.s2p": "Right-click the track list header and enable the <code>Track Title</code> · <code>Artist</code> · <code>BPM</code> · <code>Key</code> columns.",
      "idx.s3b": "Export to a file",
      "idx.s3p": "Right-click the list → <code>Export a playlist to a file</code>, and save it as <code>txt</code>.",
      "idx.s4b": "Upload",
      "idx.s4p": "Drop the saved <code>.txt</code> into the upload box above. Encodings (UTF-16, etc.) are handled automatically.",
      "idx.noteFlask": "Your file is only used for analysis and briefly stored in a temp folder.",
      "idx.noteStatic": "Your file is processed entirely in your browser and is never uploaded anywhere. Duplicate tracks are removed automatically.<br><b>Generating / downloading</b> the wheel &amp; Instagram list images needs the server — in a terminal run <code>cd web &amp;&amp; pip install -r requirements.txt &amp;&amp; python app.py</code>, then open <code>http://127.0.0.1:5000</code>.",
      "res.done": "Done",
      "res.tracksUnit": " tracks.",
      "res.from": "From",
      "res.tracks": "Tracks",
      "res.dupesRemoved": "Duplicates removed",
      "res.withKey": "With key",
      "res.wheelTitle": "Harmonic wheel image",
      "res.cmapLabel": "Dot colormap",
      "res.tracklistTitle": "Instagram tracklist image",
      "res.pagesUnit": " pages",
      "res.pasteTitle": "Tracklist for SoundCloud",
      "res.copy": "Copy",
      "res.pasteSub": "<code>Artist - Track</code> format. Copy and paste it into your SoundCloud upload description.",
      "res.another": "← Upload another file",
      "cmap.bw": "B&amp;W (default)",
      "js.copied": "Copied ✓",
      "js.generating": "Generating…",
      "js.selected": "Selected · ",
      "static.resultTitle": "{n} tracks · Tracklist for SoundCloud",
      "static.dupSuffix": " (removed {r} duplicates)",
      "static.parseErrTitle": "Couldn't read the file",
      "static.parseErrBody": "Make sure it's a rekordbox history .txt (no Track Title column was found)."
    },
    ko: {
      "idx.title": "DJ 셋의 흐름을<br>한 장의 지도로.",
      "idx.sub": "rekordbox 히스토리 파일을 올리면, 사운드클라우드 소개글용 트랙리스트를 만들어 드려요.",
      "idx.dropTitle": "히스토리 파일을 여기에 끌어다 놓거나 클릭해서 선택",
      "idx.dropHint": "rekordbox에서 내보낸 <code>.txt</code> 파일 (탭 구분)",
      "idx.start": "분석 시작 →",
      "idx.formNote": "중복 트랙은 자동으로 제거돼요. 휠·트랙리스트 이미지를 만드는 데 몇 초 걸립니다.",
      "idx.howTitle": "rekordbox에서 히스토리 파일 내보내는 방법",
      "idx.s1b": "히스토리 열기",
      "idx.s1p": "rekordbox 좌측 사이드바의 <code>Histories</code>(히스토리)를 펼쳐 원하는 날짜의 세션을 선택합니다.",
      "idx.s2b": "필요한 컬럼 켜기",
      "idx.s2p": "트랙 목록 헤더를 우클릭해 <code>Track Title</code> · <code>Artist</code> · <code>BPM</code> · <code>Key</code> 컬럼이 보이도록 체크합니다.",
      "idx.s3b": "파일로 내보내기",
      "idx.s3p": "목록 위에서 우클릭 → <code>Export a playlist to a file</code>(파일로 내보내기)를 선택하고, 형식을 <code>txt</code>(텍스트)로 저장합니다.",
      "idx.s4b": "업로드",
      "idx.s4p": "저장한 <code>.txt</code> 파일을 위 업로드 창에 올리면 끝입니다. 인코딩(UTF-16 등)은 자동으로 처리돼요.",
      "idx.noteFlask": "파일은 분석에만 사용되며 임시 폴더에 잠깐 저장됩니다.",
      "idx.noteStatic": "파일은 이 페이지(브라우저) 안에서만 처리되며 어디에도 업로드되지 않습니다. 중복 트랙은 자동으로 제거돼요.<br>휠·인스타용 리스트 <b>이미지 생성/다운로드</b>는 서버 실행이 필요합니다 — 터미널에서 <code>cd web &amp;&amp; pip install -r requirements.txt &amp;&amp; python app.py</code> 후 <code>http://127.0.0.1:5000</code> 접속.",
      "res.done": "완성됐어요",
      "res.tracksUnit": "곡.",
      "res.from": "출처",
      "res.tracks": "트랙",
      "res.dupesRemoved": "중복 제거",
      "res.withKey": "키 있음",
      "res.wheelTitle": "하모닉 휠 이미지",
      "res.cmapLabel": "점 컬러맵",
      "res.tracklistTitle": "인스타용 트랙리스트 이미지",
      "res.pagesUnit": "장",
      "res.pasteTitle": "SoundCloud 소개글용 트랙리스트",
      "res.copy": "복사",
      "res.pasteSub": "<code>아티스트 - 트랙명</code> 형식이에요. 복사해서 사운드클라우드 업로드 소개글에 붙여넣으세요.",
      "res.another": "← 다른 파일 올리기",
      "cmap.bw": "흑백 (기본)",
      "js.copied": "복사됨 ✓",
      "js.generating": "이미지 생성 중…",
      "js.selected": "선택됨 · ",
      "static.resultTitle": "{n}곡 · SoundCloud 소개글용 트랙리스트",
      "static.dupSuffix": " (중복 {r}곡 제거)",
      "static.parseErrTitle": "파일을 읽지 못했어요",
      "static.parseErrBody": "rekordbox에서 내보낸 히스토리 .txt가 맞는지 확인해 주세요. (Track Title 컬럼을 찾을 수 없습니다.)"
    }
  };

  function getLang() {
    var l = localStorage.getItem("lang");
    return (l === "ko" || l === "en") ? l : "en";
  }
  function t(key) {
    var d = DICT[getLang()] || DICT.en;
    return d[key] != null ? d[key] : (DICT.en[key] != null ? DICT.en[key] : "");
  }
  function apply(lang) {
    var d = DICT[lang] || DICT.en;
    document.querySelectorAll("[data-i18n]").forEach(function (el) {
      var k = el.getAttribute("data-i18n");
      if (d[k] != null) el.innerHTML = d[k];
    });
    document.documentElement.lang = lang;
    document.querySelectorAll(".lang-btn").forEach(function (b) {
      b.classList.toggle("active", b.dataset.lang === lang);
    });
    document.dispatchEvent(new CustomEvent("langchange", { detail: { lang: lang } }));
  }
  function setLang(lang) {
    localStorage.setItem("lang", lang);
    apply(lang);
  }
  function init() {
    apply(getLang());
    document.querySelectorAll(".lang-btn").forEach(function (b) {
      b.addEventListener("click", function () { setLang(b.dataset.lang); });
    });
  }

  window.I18N = { t: t, getLang: getLang, setLang: setLang, apply: apply };
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
