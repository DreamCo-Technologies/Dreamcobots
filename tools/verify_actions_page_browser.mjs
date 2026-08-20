#!/usr/bin/env node
import { chromium } from '@playwright/test';

const target = process.argv[2] || 'http://127.0.0.1:8765/actions.html';
const executablePath = process.env.PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH;
const browser = await chromium.launch({ headless: true, executablePath });
const errors = [];

try {
  const page = await browser.newPage({ viewport: { width: 1440, height: 1000 } });
  page.on('console', (message) => { if (message.type() === 'error') errors.push(message.text()); });
  page.on('pageerror', (error) => errors.push(error.message));

  await page.goto(target, { waitUntil: 'networkidle' });
  await page.waitForSelector('.workflow-item');
  await page.waitForSelector('#actions-control-cards');
  await page.waitForSelector('#actions-search');

  const desktop = {
    title: await page.locator('h1').textContent(),
    rows: await page.locator('.workflow-item').count(),
    workflows: await page.locator('#metric-workflows').textContent(),
    upgrades: await page.locator('#metric-upgrades').textContent(),
    benchmarks: await page.locator('#metric-benchmarks').textContent(),
    controls: await page.locator('.actions-control-card').count(),
    status: await page.locator('#actions-refresh-status').textContent(),
    overflow: await page.evaluate(() => document.documentElement.scrollWidth > document.documentElement.clientWidth),
  };

  await page.locator('.workflow-row button').first().click();
  desktop.dialog = await page.locator('#workflow-detail').evaluate((element) => element.open);
  desktop.dialogUpgrades = await page.locator('#workflow-detail-body ol li').count();
  await page.locator('#close-workflow-detail').click();
  await page.screenshot({ path: '/tmp/dreamco-actions-desktop.png', fullPage: true });

  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto(target, { waitUntil: 'networkidle' });
  await page.waitForSelector('.workflow-item');
  await page.waitForSelector('#actions-search');
  const mobile = {
    rows: await page.locator('.workflow-item').count(),
    controls: await page.locator('.actions-control-card').count(),
    overflow: await page.evaluate(() => document.documentElement.scrollWidth > document.documentElement.clientWidth),
    firstWorkflowLinks: await page.locator('.workflow-commands').first().getByRole('link').count(),
  };
  await page.screenshot({ path: '/tmp/dreamco-actions-mobile.png', fullPage: true });

  const failures = [];
  const expectedWorkflows = Number(desktop.workflows);
  if (desktop.title !== 'AGI Mission Control') failures.push('desktop title');
  if (desktop.rows !== expectedWorkflows || mobile.rows !== expectedWorkflows) failures.push('workflow count');
  if (!desktop.controls || desktop.controls < 1 || mobile.controls !== desktop.controls) failures.push('prospectus controls');
  if (!desktop.dialog || desktop.dialogUpgrades < 1) failures.push('detail dialog');
  if (desktop.overflow || mobile.overflow) failures.push('horizontal overflow');
  if (mobile.firstWorkflowLinks !== 2) failures.push('mobile workflow commands');
  if (errors.length) failures.push('browser console');

  console.log(JSON.stringify({ ok: failures.length === 0, target, desktop, mobile, errors, failures }, null, 2));
  if (failures.length) process.exitCode = 1;
} finally {
  await browser.close();
}