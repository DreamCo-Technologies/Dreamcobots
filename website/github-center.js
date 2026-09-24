(function () {
  const repo = "DreamCo-Technologies/Dreamcobots";
  const api = "https://api.github.com/repos/" + repo;
  const status = document.getElementById("center-status");
  const connectors = [
    ["Files", "Read and write files in the repository.", "contents"],
    ["Tickets", "Open, close, and comment on issues.", "issues"],
    ["Change requests", "Open and review pull requests.", "pulls"],
    ["Checks", "See the latest Actions runs.", "actions"],
    ["Pages", "Publish the site.", "pages"],
    ["Releases", "Publish a tagged release.", "releases"],
    ["Packages", "Store a built package.", "packages"],
    ["Webhooks", "Hear about a push or a ticket.", "hooks"],
    ["Codespaces", "Open a cloud work room.", "codespaces"],
    ["Secret scan", "Look for leaked keys.", "secret-scanning"],
    ["Dependabot", "See dependency alerts.", "dependabot"],
    ["Projects", "Use a GitHub project board.", "projects"],
    ["Discussions", "Read repository discussions.", "discussions"],
    ["Environments", "See deploy environments.", "deployments"],
    ["Security", "See code-scanning alerts.", "code-scanning"],
  ];

  function say(text) { status.textContent = text; }

  function button(label, href) {
    const link = document.createElement("a");
    link.className = "btn btn-outline";
    link.href = href;
    link.textContent = label;
    return link;
  }

  async function collect(path) {
    const rows = [];
    for (let page = 1; page < 40; page += 1) {
      const response = await fetch(api + path + (path.indexOf("?") === -1 ? "?" : "&") + "per_page=100&page=" + page, { headers: { Accept: "application/vnd.github+json" } });
      if (!response.ok) throw new Error("GitHub returned " + response.status);
      const batch = await response.json();
      if (!batch.length) break;
      rows.push.apply(rows, batch);
      say(rows.length + " loaded.");
      if (batch.length < 100) break;
    }
    return rows;
  }

  document.getElementById("load-commits").addEventListener("click", async function () {
    const box = document.getElementById("commits");
    box.replaceChildren();
    try {
      const commits = await collect("/commits?");
      say(commits.length + " commits. Each one opens on GitHub.");
      commits.forEach(function (commit) {
        const when = (commit.commit.author && commit.commit.author.date) || "";
        const message = (commit.commit.message || "").split("\n")[0];
        box.append(button(commit.sha.slice(0, 7) + " " + when.slice(0, 10) + " " + message, commit.html_url));
      });
    } catch (error) {
      say(error.message + " The commit list needs GitHub to answer.");
    }
  });

  document.getElementById("load-branches").addEventListener("click", async function () {
    const box = document.getElementById("branches");
    box.replaceChildren();
    try {
      const branches = await collect("/branches?");
      say(branches.length + " branches. Each one opens on GitHub.");
      branches.forEach(function (branch) {
        box.append(button(branch.name, "https://github.com/" + repo + "/tree/" + encodeURIComponent(branch.name)));
      });
    } catch (error) {
      say(error.message);
    }
  });

  const connectorBox = document.getElementById("connectors");
  connectors.forEach(function (item) {
    const article = document.createElement("article");
    article.className = "card";
    const title = document.createElement("h2");
    title.textContent = item[0];
    const text = document.createElement("p");
    text.textContent = item[1] + " This page can open GitHub's screen. It cannot change the repository until a GitHub App is installed by you.";
    const docs = document.createElement("a");
    docs.href = "https://docs.github.com/en/rest/" + item[2];
    docs.textContent = "GitHub's own instructions";
    docs.target = "_blank";
    docs.rel = "noopener noreferrer";
    article.append(title, text, docs);
    connectorBox.append(article);
  });

  document.getElementById("bot-form").addEventListener("submit", function (event) {
    event.preventDefault();
    const name = document.getElementById("bot-name").value.trim();
    const job = document.getElementById("bot-job").value.trim();
    const slug = name.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "").slice(0, 60) || "new-bot";
    const draft = "# " + name + "\n\n" + job + "\n\nThis note is a bot plan. It does not run by itself.\n";
    document.getElementById("bot-draft").textContent = draft;
    const link = document.getElementById("bot-create");
    link.hidden = false;
    link.href = "https://github.com/" + repo + "/new/main/bots?filename=" + encodeURIComponent(slug + ".md");
    link.textContent = "Create this file on GitHub";
    say("The draft is ready. GitHub will ask you to sign in before the file is saved.");
  });
})();
