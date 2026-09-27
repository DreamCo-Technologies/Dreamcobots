import assert from 'node:assert/strict';
import fs from 'node:fs';
import test from 'node:test';
import vm from 'node:vm';

// Execute both complete shared scripts with only their DOM boundary replaced.
// Relative URLs must remain inside the GitHub Pages repository prefix.
function browserDocument() {
  const appended = [];
  const document = {
    currentScript: null,
    getElementById: () => null,
    addEventListener() {},
    createElement: tagName => ({ tagName, dataset: {} }),
    querySelector(selector) {
      if (selector === 'script[data-repository-actions]') {
        return appended.find(node => node.dataset.repositoryActions);
      }
      if (selector === 'script[data-dreamco-page-actions]') {
        return appended.find(node => node.dataset.dreamcoPageActions);
      }
      return null;
    },
    head: { appendChild: node => appended.push(node) },
  };
  return { document, appended };
}

for (const order of [['nav.js', 'desk-chrome.js'], ['desk-chrome.js', 'nav.js']]) {
  test(`repository controls load exactly once through ${order.join(' then ')}`, () => {
    const { document, appended } = browserDocument();
    const context = vm.createContext({
      document, URL, navigator: {}, window: { addEventListener() {} },
      location: { pathname: '/Dreamcobots/nested/page.html', protocol: 'https:' },
    });
    for (const name of [...order, ...order]) {
      document.currentScript = { src: `https://example.github.io/Dreamcobots/${name}?v=3` };
      vm.runInContext(fs.readFileSync(`website/${name}`, 'utf8'), context, { filename: name });
    }
    const loaders = appended.filter(node => node.dataset.repositoryActions);
    assert.equal(loaders.length, 1, 'loading either navigation twice must not duplicate controls');
    assert.equal(loaders[0].src, 'https://example.github.io/Dreamcobots/repository-actions.js');
    assert.equal(loaders[0].tagName, 'script');
  });
}
