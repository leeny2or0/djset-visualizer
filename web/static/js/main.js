// Camelot Journey — landing interactions: drag & drop, filename, reshuffle.
(function () {
  "use strict";

  var drop = document.getElementById("drop");
  var input = document.getElementById("history");
  var fileName = document.getElementById("fileName");

  function showName(name) {
    if (!fileName) return;
    fileName.textContent = "선택됨 · " + name;
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
        copyBtn.textContent = "복사됨 ✓";
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

  // Reshuffle colours: reload to get a fresh server-generated palette.
  var reshuffle = document.getElementById("reshuffle");
  if (reshuffle) {
    reshuffle.addEventListener("click", function () {
      window.location.reload();
    });
  }
})();
