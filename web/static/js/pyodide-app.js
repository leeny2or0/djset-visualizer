// In-browser image generation via Pyodide (Python + matplotlib in WebAssembly).
// Lets the wheel / Instagram tracklist images work on static / FTP hosting,
// with no Python server. Heavy on first use (downloads the runtime once).
(function () {
  "use strict";

  var PYODIDE_VER = "v0.27.5";
  var PYODIDE_JS = "https://cdn.jsdelivr.net/pyodide/" + PYODIDE_VER + "/full/pyodide.js";
  // Korean font so Hangul track titles render in the figures (Pyodide mpl = DejaVu only)
  var KFONT = "https://cdn.jsdelivr.net/gh/google/fonts@main/ofl/nanumgothic/NanumGothic-Regular.ttf";

  var py = null;
  var readyPromise = null;

  function loadScript(src) {
    return new Promise(function (resolve, reject) {
      var s = document.createElement("script");
      s.src = src; s.onload = resolve; s.onerror = function () { reject(new Error("load " + src)); };
      document.head.appendChild(s);
    });
  }

  function yieldUI() { return new Promise(function (r) { setTimeout(r, 40); }); }

  async function init(onPhase) {
    if (readyPromise) return readyPromise;
    readyPromise = (async function () {
      onPhase && onPhase("runtime");
      await loadScript(PYODIDE_JS);
      py = await loadPyodide();

      onPhase && onPhase("packages");
      await py.loadPackage(["numpy", "pandas", "matplotlib", "scipy", "micropip"]);
      try {
        await py.runPythonAsync(
          "import micropip\nawait micropip.install('adjustText', deps=False)");
      } catch (e) {
        console.warn("adjustText unavailable; wheel labels won't auto-arrange.", e);
      }

      onPhase && onPhase("code");
      var coreSrc = await (await fetch("camelot_core.py")).text();
      py.FS.writeFile("camelot_core.py", coreSrc);
      var drvSrc = await (await fetch("static/py/driver.py")).text();
      py.FS.writeFile("driver.py", drvSrc);
      py.runPython("import driver");

      try {  // Korean/CJK font (best effort)
        var fbuf = new Uint8Array(await (await fetch(KFONT)).arrayBuffer());
        py.FS.mkdirTree("/tmp/camelot");
        py.FS.writeFile("/tmp/camelot/korean.ttf", fbuf);
        py.runPython("import driver; driver.setup_fonts('/tmp/camelot/korean.ttf')");
      } catch (e) {
        console.warn("Korean font load failed; non-Latin titles may not render.", e);
      }
      return py;
    })();
    return readyPromise;
  }

  async function loadHistory(file, onPhase) {
    await init(onPhase);
    var buf = new Uint8Array(await file.arrayBuffer());
    py.globals.set("_data", buf);
    var meta = py.runPython("driver.load_history(_data)");
    py.globals.set("_data", undefined);
    return JSON.parse(meta);
  }

  async function wheel(cmap) {
    await yieldUI();           // let the "generating" status paint first
    py.globals.set("_cmap", cmap || "bw");
    return JSON.parse(py.runPython("driver.gen_wheel(_cmap)"));
  }

  async function tracklist() {
    await yieldUI();
    return JSON.parse(py.runPython("driver.gen_tracklist()"));
  }

  window.PyImages = { init: init, loadHistory: loadHistory, wheel: wheel, tracklist: tracklist };
})();
