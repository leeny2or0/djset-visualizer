// Monochrome (black & white) organic theme, generated fresh on every load.
// Mirrors app.py make_theme() but client-side so the static page works offline.
(function () {
  "use strict";

  function rnd(a, b) { return a + Math.random() * (b - a); }
  function clamp(v, lo, hi) { return Math.min(hi, Math.max(lo, v)); }
  function gray(v) {
    var n = Math.round(clamp(v, 0, 1) * 255);
    var h = n.toString(16).padStart(2, "0");
    return "#" + h + h + h;
  }
  function blobRadius() {
    var p = [];
    for (var i = 0; i < 8; i++) p.push(Math.round(rnd(28, 72)));
    return p[0] + "% " + p[1] + "% " + p[2] + "% " + p[3] + "% / " +
           p[4] + "% " + p[5] + "% " + p[6] + "% " + p[7] + "%";
  }

  var dark = Math.random() < 0.30;
  var base = dark ? rnd(0.55, 0.82) : rnd(0.16, 0.46);
  var accents = [];
  for (var i = 0; i < 4; i++) accents.push(gray(clamp(base + rnd(-0.14, 0.18), 0.05, 0.92)));

  var t = dark ? {
    bg: "#0f0f0f", bg2: "#1b1b1b", surface: "rgba(255,255,255,0.06)",
    text: "#f2f2f2", muted: "#a9a9a9", border: "rgba(255,255,255,0.16)",
    shadow: "0 24px 60px rgba(0,0,0,0.5)"
  } : {
    bg: "#f3f3f3", bg2: "#e8e8e8", surface: "rgba(255,255,255,0.72)",
    text: "#141414", muted: "#6a6a6a", border: "rgba(0,0,0,0.10)",
    shadow: "0 24px 60px rgba(0,0,0,0.12)"
  };

  var root = document.documentElement.style;
  root.setProperty("--bg", t.bg);
  root.setProperty("--bg2", t.bg2);
  root.setProperty("--surface", t.surface);
  root.setProperty("--text", t.text);
  root.setProperty("--muted", t.muted);
  root.setProperty("--border", t.border);
  root.setProperty("--accent", accents[0]);
  root.setProperty("--accent2", accents[1]);
  root.setProperty("--accent3", accents[2]);
  root.setProperty("--card-shadow", t.shadow);
  document.body.className = dark ? "dark" : "light";

  // organic blobs (monochrome): random shape / position / tone each load
  function buildBlobs() {
    var field = document.querySelector(".bg-field");
    if (!field) return;
    field.style.color = accents[1]; // for the geometric <svg currentColor>
    for (var k = 0; k < 6; k++) {
      var b = document.createElement("span");
      b.className = "blob";
      var op = dark ? rnd(0.28, 0.55) : rnd(0.4, 0.72);
      b.style.cssText =
        "--bx:" + rnd(-12, 88).toFixed(1) + "vw;" +
        "--by:" + rnd(-12, 88).toFixed(1) + "vh;" +
        "--bs:" + rnd(26, 54).toFixed(1) + "vw;" +
        "--bc:" + accents[k % accents.length] + ";" +
        "--bo:" + op.toFixed(2) + ";" +
        "--bf:" + rnd(28, 70).toFixed(1) + "px;" +
        "--br:" + blobRadius() + ";" +
        "--bd:" + rnd(20, 38).toFixed(1) + "s;" +
        "--bdl:" + rnd(-24, 0).toFixed(1) + "s;" +
        "--bdr:" + rnd(2, 7).toFixed(1) + "vh;";
      field.appendChild(b);
    }
  }
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", buildBlobs);
  } else {
    buildBlobs();
  }
})();
