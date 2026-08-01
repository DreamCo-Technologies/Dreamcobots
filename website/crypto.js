(() => {
  const catalog = window.BUDDY_SPECIALIZED_HUBS?.crypto;
  const families = catalog?.families || [];
  const byId = id => document.getElementById(id);
  const node = (tag, className = '', text = '') => { const item = document.createElement(tag); item.className = className; item.textContent = text; return item; };

  function list(items) {
    const ul = node('ul', 'crypto-result-list');
    items.forEach(item => ul.append(node('li', '', item)));
    return ul;
  }

  function showResult(targetId, title, items, notice) {
    const target = byId(targetId);
    target.replaceChildren(node('h2', '', title), list(items), node('p', 'crypto-notice', notice));
  }

  families.forEach(family => {
    const option = node('option', '', family.label);
    option.value = family.id;
    byId('wallet-network').append(option);
    const card = node('article', 'crypto-network');
    card.append(node('h3', '', family.label), node('p', '', family.integration), node('code', '', family.standards.join(' · ')));
    byId('crypto-network-grid').append(card);
  });
  byId('chain-family-count').textContent = String(families.length);
  [byId('wallet-approval'), byId('mining-approval'), byId('dreamcoin-approval')].forEach(control => {
    control.addEventListener('change', event => {
      event.currentTarget.closest('form')?.classList.toggle('is-approved', event.currentTarget.checked);
    });
  });

  document.querySelectorAll('[data-crypto-panel]').forEach(button => button.addEventListener('click', () => {
    document.querySelectorAll('[data-crypto-panel]').forEach(item => item.classList.toggle('active', item === button));
    document.querySelectorAll('.crypto-panel').forEach(panel => { panel.hidden = panel.id !== button.dataset.cryptoPanel; });
  }));

  byId('wallet-plan-form').addEventListener('submit', event => {
    event.preventDefault();
    if (!event.currentTarget.reportValidity()) return;
    const family = families.find(item => item.id === byId('wallet-network').value);
    showResult('wallet-result', `${family?.label || 'Wallet'} plan`, [
      'Verify the exact network, asset contract, decimals, and trusted explorer.',
      `Connect through ${family?.integration || 'a user-controlled wallet'}.`,
      'Start watch-only and expose no account by default.',
      'Simulate address, amount, fee, slippage, allowance, and balance changes.',
      'Require the user-controlled wallet to display and approve every signature.',
      'Save transaction evidence, never private keys or recovery phrases.',
    ], 'This public page creates a plan only. It cannot sign or submit a transaction.');
  });

  byId('mining-plan-form').addEventListener('submit', event => {
    event.preventDefault();
    if (!event.currentTarget.reportValidity()) return;
    const devices = Number(byId('mining-devices').value);
    const watts = Number(byId('mining-watts').value);
    const rate = Number(byId('mining-electricity').value);
    const revenue = Number(byId('mining-revenue').value);
    const kwh = devices * watts * 24 / 1000;
    const cost = kwh * rate;
    const metrics = node('div', 'crypto-result-metric');
    [[`${kwh.toFixed(2)} kWh`, 'Daily energy'], [`$${cost.toFixed(2)}`, 'Daily electricity'], [`$${(revenue - cost).toFixed(2)}`, 'Before hardware, pool, tax']].forEach(([value, label]) => {
      const cell = node('div'); cell.append(node('strong', '', value), node('span', '', label)); metrics.append(cell);
    });
    const target = byId('mining-result');
    target.replaceChildren(node('h2', '', 'Mining cost scenario'), metrics, list(['Add hardware depreciation and downtime.', 'Verify pool terms and network rules.', 'Review circuit, heat, ventilation, noise, and fire safety.', 'Set automatic temperature and power shutdown limits.']), node('p', 'crypto-notice', 'Revenue and difficulty can change quickly. This is not a profit promise and starts no mining process.'));
  });

  byId('dreamcoin-plan-form').addEventListener('submit', event => {
    event.preventDefault();
    if (!event.currentTarget.reportValidity()) return;
    showResult('dreamcoin-result', 'DreamCoin testnet gates', catalog?.dreamcoin?.required_before_launch || [], 'No coin is created, minted, offered, sold, or assigned a value by this plan.');
  });
})();
