// 用已缓存的 Playwright Chromium 把 SVG 渲染成 2x PNG
const path = require('path');
const fs = require('fs');
const pwPath = 'C:/Users/LX/AppData/Roaming/npm/node_modules/@playwright/mcp/node_modules/playwright';
const { chromium } = require(pwPath);

const labDir = __dirname;
const svgDir = path.join(labDir, 'svg');
const outDir = path.join(labDir, '..', 'images');
fs.mkdirSync(outDir, { recursive: true });

const files = ['fig1_architecture', 'fig2_attack_chain', 'fig3_defense', 'fig4_results'];

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage({ deviceScaleFactor: 2 });
  for (const name of files) {
    const svg = fs.readFileSync(path.join(svgDir, name + '.svg'), 'utf8');
    await page.setContent(svg);
    const out = path.join(outDir, name + '.png');
    await page.locator('svg').screenshot({ path: out });
    console.log('rendered', out, fs.statSync(out).size, 'bytes');
  }
  await browser.close();
})().catch(e => { console.error(e); process.exit(1); });
