(function () {
  function card(row) {
    const article = document.createElement("article");
    article.className = "card";
    const title = document.createElement("h2");
    title.textContent = row.name;
    const text = document.createElement("p");
    text.textContent = row.license + ". " + row.note + " The file is not stored here.";
    const link = document.createElement("a");
    link.href = row.href;
    link.textContent = "Open the dataset card";
    link.target = "_blank";
    link.rel = "noopener noreferrer";
    article.append(title, text, link);
    return article;
  }

  fetch("data/free-datasets.json")
    .then(function (response) { return response.json(); })
    .then(function (data) {
      const ready = data.datasets.filter(function (row) { return row.train; });
      const hold = data.datasets.filter(function (row) { return !row.train; });
      document.getElementById("data-lead").textContent = data.datasets.length + " public datasets. " + ready.length + " are marked ready if you follow the license. " + hold.length + " need the card read first. Nothing is downloaded to this site. " + data.rule;
      ready.forEach(function (row) { document.getElementById("ready").append(card(row)); });
      hold.forEach(function (row) { document.getElementById("hold").append(card(row)); });
    })
    .catch(function () {
      document.getElementById("data-lead").textContent = "The dataset list did not load.";
    });
})();
