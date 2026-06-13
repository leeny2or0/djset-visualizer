// Camelot Journey — interactions: drag & drop, copy, submit state, colormap.
(function () {
  "use strict";

  var drop = document.getElementById("drop");
  var input = document.getElementById("history");
  var fileName = document.getElementById("fileName");

  function tr(key, fallback) {
    return (window.I18N && window.I18N.t(key)) || fallback;
  }

  function showName(name) {
    if (!fileName) return;
    fileName.textContent = tr("js.selected", "Selected · ") + name;
    fileName.hidden = false;
  }

  if (drop && input) {
    input.addEventListener("change", function () {
      if (input.files && input.files.length) showName(input.files[0].name);
    });

    ["dragenter", "dragover"].forEach(function (ev) {
      drop.addEventListener(ev, function (e) {
        e.preventDefault();
        drop.classList.add("drag");
      });
    });
    ["dragleave", "drop"].forEach(function (ev) {
      drop.addEventListener(ev, function (e) {
        e.preventDefault();
        drop.classList.remove("drag");
      });
    });
    drop.addEventListener("drop", function (e) {
      if (e.dataTransfer && e.dataTransfer.files.length) {
        input.files = e.dataTransfer.files;
        showName(e.dataTransfer.files[0].name);
      }
    });
  }

  // Copy the tracklist to the clipboard (for the SoundCloud description).
  var copyBtn = document.getElementById("copyBtn");
  if (copyBtn) {
    copyBtn.addEventListener("click", function () {
      var area = document.getElementById(copyBtn.dataset.target);
      if (!area) return;
      var done = function () {
        var old = copyBtn.textContent;
        copyBtn.textContent = tr("js.copied", "Copied ✓");
        copyBtn.classList.add("ok");
        setTimeout(function () {
          copyBtn.textContent = old;
          copyBtn.classList.remove("ok");
        }, 1600);
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

  // Image generation takes a few seconds — show a working state on submit.
  var goBtn = document.getElementById("goBtn");
  if (goBtn && goBtn.form) {
    goBtn.form.addEventListener("submit", function () {
      goBtn.textContent = tr("js.generating", "Generating…");
      goBtn.disabled = true;
      goBtn.style.opacity = "0.7";
    });
  }

  // Server dropdowns (colormap, numbering): reload /result with the chosen value.
  document.querySelectorAll("select[data-base]").forEach(function (sel) {
    sel.addEventListener("change", function () {
      var param = sel.dataset.param || "cmap";
      window.location = sel.dataset.base + "?" + param + "=" + encodeURIComponent(sel.value);
    });
  });
})();
