const { chromium } = require('X:/My-Projects/TradingBot/apps/chart/node_modules/playwright-core');

(async () => {
  const browser = await chromium.launch({ channel: 'msedge', headless: true });
  const page = await browser.newPage({ viewport: { width: 1440, height: 1000 } });
  const errors = [];
  page.on('pageerror', error => errors.push(error.message));
  page.on('console', message => { if (message.type() === 'error') errors.push(message.text()); });
  await page.route('**/api/info/**', route => route.fulfill({ json: {
    payload: { timeframe: 5, directions: { bearish: {
      eZones: [{ sourceTime: 1789430400, number: 3, family: 'red', price: '100' }],
      stopAlls: [{ sourceTime: 1789430430, number: 2, price: '95' }],
    } } },
    snapshot: { calculation: { symbol: 'TEST', timeframe: 5, direction: 'bearish' } },
  } }));
  await page.goto('http://localhost:5173/info/qa/5s/bearish/1-2--aabbccddeeff0011.json');
  await page.locator('.event').first().waitFor({ state: 'attached' });
  await page.locator('.day-head').click();
  console.log(JSON.stringify({ title: await page.title(), url: page.url(),
    radios: await page.locator('input[type=radio]').count(),
    bulk: await page.locator('[data-time-group-status]').count(),
    export: await page.locator('#report-text').inputValue(), errors }));
  await page.locator('.bridge-output > summary').first().click();
  await page.locator('.bridge-yaml').first().waitFor();
  await page.screenshot({ path: `${__dirname}/manual-report-desktop.png`, fullPage: true });
  await page.locator('#clear-filters').click();
  const empty = await page.locator('#empty').isVisible();
  const cleared = await page.locator('#report-text').inputValue();
  await page.locator('#all-filters').check();
  const restored = await page.locator('.event:visible').count();
  await page.setViewportSize({ width: 390, height: 844 });
  await page.screenshot({ path: `${__dirname}/manual-report-mobile.png`, fullPage: true });
  console.log(JSON.stringify({ emptyAfterClear: empty, exportAfterClear: cleared,
    restored, overflow: await page.evaluate(() => document.documentElement.scrollWidth > innerWidth), errors }));
  await browser.close();
})().catch(error => { console.error(error); process.exit(1); });
