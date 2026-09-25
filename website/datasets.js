(function () {
  function card(row) {
    const article = document.createElement("article");
    article.className = "card";
    const title = document.createElement("h3");
    title.textContent = row.name;
    const text = document.createElement("p");
    text.textContent = row.license + ". " + row.note;
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
      const ready = data.datasets.filter(function (row) { return row.train; }).length;
      document.getElementById("data-lead").textContent = data.datasets.length + " public datasets in categories. " + ready + " can be trained on if you follow the license. Buddy studied the listings, not the files. " + data.rule;
      const box = document.getElementById("groups");
      const names = [];
      data.datasets.forEach(function (row) {
        if (names.indexOf(row.category) === -1) names.push(row.category);
      });
      names.forEach(function (name) {
        const heading = document.createElement("h2");
        heading.textContent = name;
        box.append(heading);
        data.datasets.filter(function (row) { return row.category === name; }).forEach(function (row) {
          box.append(card(row));
        });
      });
    })
    .catch(function () {
      document.getElementById("data-lead").textContent = "The dataset list did not load.";
    });
})();
