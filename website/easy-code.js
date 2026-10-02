(function () {
  const box = document.getElementById("easy");
  fetch("data/easy-code.json").then(function (response) { return response.json(); }).then(function (data) {
    ["repository", "pages"].forEach(function (key) {
      const heading = document.createElement("h2");
      heading.textContent = key === "repository" ? "20 ways on GitHub" : "20 ways on this site";
      box.append(heading);
      data[key].forEach(function (item) {
        const link = document.createElement("a");
        link.className = "btn btn-outline";
        link.href = item.href;
        link.textContent = item.plain;
        box.append(link);
      });
    });
  });
})();
