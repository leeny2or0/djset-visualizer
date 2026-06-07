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

  // Reshuffle colours: reload to get a fresh server-generated palette.
  var reshuffle = document.getElementById("reshuffle");
  if (reshuffle) {
    reshuffle.addEventListener("click", function () {
      window.location.reload();
    });
  }
})();
