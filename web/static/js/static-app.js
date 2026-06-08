// Static (no-server) app: read a rekordbox history .txt in the browser and
// build an "Artist - Track" tracklist for pasting into a SoundCloud description.
(function () {
  "use strict";

  var input = document.getElementById("history");
  var drop = document.getElementById("drop");
  var fileName = document.getElementById("fileName");
  var result = document.getElementById("result");
  var resultTitle = document.getElementById("resultTitle");
  var area = document.getElementById("tracklist");
  var copyBtn = document.getElementById("copyBtn");

  // --- decode bytes (rekordbox history is usually UTF-16LE w/ BOM) ----------
  function decode(buf) {
    var b = new Uint8Array(buf);
    if (b[0] === 0xff && b[1] === 0xfe) return new TextDecoder("utf-16le").decode(buf);
    if (b[0] === 0xfe && b[1] === 0xff) return new TextDecoder("utf-16be").decode(buf);
    if (b[0] === 0xef && b[1] === 0xbb && b[2] === 0xbf) return new TextDecoder("utf-8").decode(buf);
    var nul = 0, lim = Math.min(b.length, 4000);
    for (var i = 0; i < lim; i++) if (b[i] === 0) nul++;
    if (nul > lim * 0.1) return new TextDecoder("utf-16le").decode(buf);
    return new TextDecoder("utf-8").decode(buf);
  }

  function findCol(header, names) {
    for (var n = 0; n < names.length; n++) {
      var idx = header.indexOf(names[n]);
      if (idx >= 0) return idx;
    }
    return -1;
  }

  function parse(text) {
    var lines = text.split(/\r?\n/).filter(function (l) { return l.length > 0; });
    if (!lines.length) return { rows: [], ok: false };
    var header = lines[0].split("\t").map(function (h) {
      return h.replace(/^#/, "").trim().toLowerCase();
    });
    var ti = findCol(header, ["track title", "title", "name"]);
    var ai = findCol(header, ["artist"]);
    if (ti < 0) return { rows: [], ok: false };
    var rows = [];
    for (var r = 1; r < lines.length; r++) {
      var c = lines[r].split("\t");
      var title = (c[ti] || "").trim();
      var artist = ai >= 0 ? (c[ai] || "").trim() : "";
      if (!title && !artist) continue;
      rows.push({ title: title, artist: artist });
    }
    return { rows: rows, ok: true };
  }

  function tracklistText(rows) {
    return rows.map(function (t, i) {
      var body = (t.artist && t.title) ? (t.artist + " - " + t.title)
        : (t.title || t.artist || ("Track " + (i + 1)));
      return (i + 1) + ". " + body;
    }).join("\n");
  }

  function showName(name) {
    if (!fileName) return;
    fileName.textContent = "선택됨 · " + name;
    fileName.hidden = false;
  }

  function handleFile(file) {
    if (!file) return;
    showName(file.name);
    var reader = new FileReader();
    reader.onload = function () {
      var parsed = parse(decode(reader.result));
      if (!parsed.ok) {
        resultTitle.textContent = "파일을 읽지 못했어요";
        area.value = "rekordbox에서 내보낸 히스토리 .txt가 맞는지 확인해 주세요.\n" +
                     "(Track Title 컬럼을 찾을 수 없습니다.)";
        result.hidden = false;
        return;
      }
      resultTitle.textContent = parsed.rows.length + "곡 · SoundCloud 소개글용 트랙리스트";
      area.value = tracklistText(parsed.rows);
      result.hidden = false;
      result.scrollIntoView({ behavior: "smooth", block: "nearest" });
    };
    reader.readAsArrayBuffer(file);
  }

  if (input) {
    input.addEventListener("change", function () {
      if (input.files && input.files.length) handleFile(input.files[0]);
    });
  }
  if (drop) {
    ["dragenter", "dragover"].forEach(function (ev) {
      drop.addEventListener(ev, function (e) { e.preventDefault(); drop.classList.add("drag"); });
    });
    ["dragleave", "drop"].forEach(function (ev) {
      drop.addEventListener(ev, function (e) { e.preventDefault(); drop.classList.remove("drag"); });
    });
    drop.addEventListener("drop", function (e) {
      if (e.dataTransfer && e.dataTransfer.files.length) handleFile(e.dataTransfer.files[0]);
    });
  }

  if (copyBtn) {
    copyBtn.addEventListener("click", function () {
      if (!area.value) return;
      var done = function () {
        var old = copyBtn.textContent;
        copyBtn.textContent = "복사됨 ✓";
        copyBtn.classList.add("ok");
        setTimeout(function () { copyBtn.textContent = old; copyBtn.classList.remove("ok"); }, 1600);
      };
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(area.value).then(done, function () {
          area.select(); document.execCommand("copy"); done();
        });
      } else {
        area.select(); document.execCommand("copy"); done();
      }
    });
  }

  var reshuffle = document.getElementById("reshuffle");
  if (reshuffle) reshuffle.addEventListener("click", function () { window.location.reload(); });
})();
