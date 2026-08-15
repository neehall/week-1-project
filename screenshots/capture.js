// Reusable screenshot driver for the Sales Dashboard.
// Requires `playwright` + Chromium installed (see README note below).
// Usage: node capture.js [output-path]
const { chromium } = require('playwright');

(async () => {
  const outPath = process.argv[2] || `screenshots/dashboard_${new Date().toISOString().replace(/[:.]/g, '-')}.png`;
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1600, height: 1000 } });
  await page.goto('http://localhost:8501', { waitUntil: 'networkidle', timeout: 30000 });
  await page.waitForSelector('text=Sales Dashboard', { timeout: 20000 });
  await page.waitForTimeout(2500); // let charts finish drawing
  await page.screenshot({ path: outPath, fullPage: true });
  await browser.close();
  console.log('Saved to', outPath);
})().catch((err) => {
  console.error(err);
  process.exit(1);
});
