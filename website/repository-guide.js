(() => {
  const input = document.getElementById('page-filter');
  const rows = [...document.querySelectorAll('#page-list > li')];
  const count = document.getElementById('page-count');
  function filter() {
    const query = input.value.trim().toLowerCase();
    let visible = 0;
    rows.forEach(row => {
      row.hidden = !row.textContent.toLowerCase().includes(query);
      if (!row.hidden) visible += 1;
    });
    count.textContent = `${visible} of ${rows.length} pages`;
    document.getElementById('page-empty').hidden = visible !== 0;
  }
  input.addEventListener('input', filter);
  filter();
})();
