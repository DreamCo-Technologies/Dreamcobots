import { calculateBotTemplate, formatCalculatorValue } from './calculator-engine.js';

const state = { registry: null, selected: null, filtered: [] };
const numberFormat = new Intl.NumberFormat('en-US');
const search = document.getElementById('calculator-search');
const division = document.getElementById('calculator-division');
const list = document.getElementById('calculator-list');
const stage = document.getElementById('calculator-stage');
const matchCount = document.getElementById('calculator-match-count');

function escapeHtml(value) {
  return String(value ?? '')
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')
    .replaceAll("'", '&#39;');
}

function unitLabel(unit) {
  return ({ currency: 'USD', percent: '%', months: 'months', hours: 'hours', minutes: 'minutes', number: 'number' })[unit] || unit;
}

function renderDirectory() {
  const query = search.value.trim().toLowerCase();
  const selectedDivision = division.value;
  state.filtered = state.registry.calculators.filter((calculator) => {
    const bot = calculator.bot;
    const haystack = `${bot.display_name} ${bot.slug} ${bot.division} ${bot.category} ${calculator.name}`.toLowerCase();
    return (!query || haystack.includes(query)) && (selectedDivision === 'all' || bot.division === selectedDivision);
  });
  const visible = state.filtered.slice(0, 100);
  matchCount.textContent = state.filtered.length > visible.length
    ? `${numberFormat.format(state.filtered.length)} matches, showing first ${visible.length}`
    : `${numberFormat.format(state.filtered.length)} matching calculators`;
  list.innerHTML = visible.map((calculator) => `<button class="calculator-list-button ${state.selected?.calculator_id === calculator.calculator_id ? 'active' : ''}" type="button" role="option" aria-selected="${state.selected?.calculator_id === calculator.calculator_id}" data-calculator="${escapeHtml(calculator.calculator_id)}">
      <span class="calculator-list-emoji" aria-hidden="true">${escapeHtml(calculator.bot.emoji)}</span>
      <span><strong>${escapeHtml(calculator.bot.display_name)}</strong><small>${escapeHtml(calculator.bot.division)} · ${escapeHtml(calculator.template_id.replaceAll('_', ' '))}</small></span>
    </button>`).join('');
}

function boundedValue(spec, raw) {
  const numeric = Number(raw);
  if (!Number.isFinite(numeric)) return spec.default;
  return Math.min(spec.max, Math.max(spec.min, numeric));
}

function currentInputs(calculator) {
  return Object.fromEntries(calculator.inputs.map((spec) => {
    const input = document.getElementById(`calculator-input-${spec.key}`);
    return [spec.key, boundedValue(spec, input?.value ?? spec.default)];
  }));
}

function renderResults() {
  const calculator = state.selected;
  if (!calculator) return;
  const values = calculateBotTemplate(calculator.template_id, currentInputs(calculator));
  const results = document.getElementById('calculator-results');
  if (!results) return;
  results.innerHTML = calculator.outputs.map((output) => `<div class="calculator-result">
      <span>${escapeHtml(output.label)}</span>
      <strong>${escapeHtml(formatCalculatorValue(values[output.key], output.unit))}</strong>
    </div>`).join('');
}

function renderCalculator(calculator) {
  const reference = calculator.assigned_division_formula;
  stage.innerHTML = `<div class="calculator-titlebar">
      <div class="calculator-title">
        <span class="calculator-title-emoji" aria-hidden="true">${escapeHtml(calculator.bot.emoji)}</span>
        <div><h2>${escapeHtml(calculator.name)}</h2><p>${escapeHtml(calculator.bot.division)} · ${escapeHtml(calculator.bot.category)} · ${escapeHtml(calculator.objective)}</p></div>
      </div>
      <span class="calculator-status">Local engine ready</span>
    </div>
    <div class="calculator-body">
      <section class="calculator-input-panel" aria-label="Calculator assumptions">
        <div class="calculator-panel-head"><h3>Assumptions</h3><button id="calculator-reset" class="calculator-reset" type="button">Reset values</button></div>
        <div class="calculator-fields">
          ${calculator.inputs.map((input) => `<div class="calculator-field">
            <label for="calculator-input-${escapeHtml(input.key)}">${escapeHtml(input.label)}</label>
            <div class="calculator-input-wrap">
              <input id="calculator-input-${escapeHtml(input.key)}" data-calculator-input type="number" inputmode="decimal" value="${input.default}" min="${input.min}" max="${input.max}" step="${input.step}" />
              <span>${escapeHtml(unitLabel(input.unit))}</span>
            </div>
          </div>`).join('')}
        </div>
      </section>
      <section class="calculator-output-panel" aria-label="Calculated results">
        <div class="calculator-panel-head"><h3>Planning estimate</h3></div>
        <div id="calculator-results" class="calculator-results"></div>
        <div class="calculator-reference">
          <h3>Assigned division formula reference</h3>
          <p class="calculator-reference-name">${escapeHtml(reference.name)}</p>
          <pre class="calculator-formula"></pre>
          <p class="calculator-reference-note">Reference only. This text is displayed for research traceability and is never executed as code. ${escapeHtml(reference.description)}</p>
        </div>
      </section>
    </div>
    <div class="calculator-footer">
      <div class="calculator-meta"><span>Calculator ID</span><strong>${escapeHtml(calculator.calculator_id)}</strong></div>
      <div class="calculator-actions">
        <a class="btn btn-outline btn-sm" href="${escapeHtml(calculator.links.prospectus)}">Prospectus</a>
        <a class="btn btn-primary btn-sm" href="${escapeHtml(calculator.links.buddy)}">Plan with Buddy</a>
      </div>
    </div>`;
  stage.querySelector('.calculator-formula').textContent = reference.formula;
  stage.querySelectorAll('[data-calculator-input]').forEach((input) => input.addEventListener('input', renderResults));
  document.getElementById('calculator-reset').addEventListener('click', () => {
    calculator.inputs.forEach((spec) => {
      document.getElementById(`calculator-input-${spec.key}`).value = spec.default;
    });
    renderResults();
  });
  renderResults();
}

function selectCalculator(calculator, updateUrl = true) {
  state.selected = calculator;
  renderDirectory();
  renderCalculator(calculator);
  if (updateUrl) {
    const url = new URL(location.href);
    url.searchParams.set('bot', calculator.bot.slug);
    history.replaceState({}, '', url);
  }
}

async function initialize() {
  try {
    const response = await fetch('data/bot-calculators.json', { cache: 'no-store' });
    if (!response.ok) throw new Error(`Calculator registry returned ${response.status}`);
    state.registry = await response.json();
    const summary = state.registry.summary;
    document.getElementById('calculator-count').textContent = numberFormat.format(summary.calculators);
    document.getElementById('calculator-divisions').textContent = numberFormat.format(summary.divisions_covered);
    document.getElementById('calculator-templates').textContent = numberFormat.format(summary.calculator_templates);
    const divisions = [...new Set(state.registry.calculators.map((item) => item.bot.division))].sort();
    division.insertAdjacentHTML('beforeend', divisions.map((name) => `<option value="${escapeHtml(name)}">${escapeHtml(name)}</option>`).join(''));
    const requested = new URLSearchParams(location.search).get('bot');
    const selected = state.registry.calculators.find((item) => item.bot.slug === requested)
      || state.registry.calculators.find((item) => item.template_id === 'real_estate_flip')
      || state.registry.calculators[0];
    selectCalculator(selected, false);
  } catch (error) {
    stage.innerHTML = `<p class="calculator-error">Calculator registry unavailable: ${escapeHtml(error.message)}</p>`;
    matchCount.textContent = 'Registry unavailable';
  }
}

search.addEventListener('input', renderDirectory);
division.addEventListener('change', renderDirectory);
list.addEventListener('click', (event) => {
  const button = event.target.closest('[data-calculator]');
  if (!button) return;
  const calculator = state.registry.calculators.find((item) => item.calculator_id === button.dataset.calculator);
  if (calculator) selectCalculator(calculator);
});

initialize();
