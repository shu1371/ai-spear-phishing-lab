// 把 lab/outputs/run_log.txt 按「三段」渲染成真实终端风格的 PNG 截图
const fs = require('fs');
const path = require('path');
const pwPath = 'C:/Users/LX/AppData/Roaming/npm/node_modules/@playwright/mcp/node_modules/playwright';
const { chromium } = require(pwPath);

const labDir = __dirname;
const logPath = path.join(labDir, 'outputs', 'run_log.txt');
const outDir = path.join(labDir, '..', 'images');
fs.mkdirSync(outDir, { recursive: true });

const log = fs.readFileSync(logPath, 'utf8');

// 切分三段：基线 / 攻击 / 汇总
function slice(startMarker, endMarker) {
  const s = log.indexOf(startMarker);
  const e = endMarker ? log.indexOf(endMarker) : -1;
  const chunk = e > s ? log.slice(s, e) : log.slice(s);
  return chunk.trimEnd();
}
const base = slice('===== 基线', '===== 攻击');
const attack = slice('===== 攻击', '===== 汇总');
const summary = slice('===== 汇总');

// 终端上色：根据关键字给行着不同颜色
function colorize(txt) {
  const esc = {
    reset: '#d4d4d4', green: '#4ec9b0', red: '#f48771', amber: '#dcdcaa',
    blue: '#569cd6', gray: '#6a9955', cyan: '#9cdcfe', yellow: '#d7ba7d',
  };
  return txt.split('\n').map(line => {
    let c = esc.reset;
    if (/gw=BLOCK|score=100|拦截 8\/8/.test(line)) c = esc.red;
    else if (/gw=PASS/.test(line)) c = esc.green;
    else if (/click=True/.test(line)) c = esc.yellow;
    else if (/=====/.test(line)) c = esc.blue;
    else if (/==>/.test(line)) c = esc.cyan;
    const safe = line.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
    return `<div style="color:${c}">${safe || '&nbsp;'}</div>`;
  }).join('');
}

async function shot(name, title, bodyText) {
  const html = `<!doctype html><html><head><meta charset="utf-8"><style>
    body{margin:0;background:#1e1e1e;display:flex;justify-content:center;padding:24px;font-family:'Cascadia Code','Consolas','Microsoft YaHei',monospace;}
    .term{background:#1e1e1e;border:1px solid #333;border-radius:10px;box-shadow:0 8px 30px rgba(0,0,0,.5);width:920px;overflow:hidden;}
    .bar{background:#2d2d2d;padding:10px 14px;display:flex;align-items:center;gap:8px;}
    .dot{width:12px;height:12px;border-radius:50%;}
    .t{color:#cfcfcf;font-size:13px;margin-left:10px;}
    .body{padding:16px 18px;font-size:14px;line-height:1.55;white-space:pre-wrap;color:#d4d4d4;}
  </style></head><body>
  <div class="term"><div class="bar">
    <span class="dot" style="background:#ff5f56"></span>
    <span class="dot" style="background:#ffbd2e"></span>
    <span class="dot" style="background:#27c93f"></span>
    <span class="t">${title}</span></div>
  <div class="body">${colorize(bodyText)}</div></div></body></html>`;
  const browser = await chromium.launch();
  const page = await browser.newPage({ deviceScaleFactor: 2 });
  await page.setContent(html);
  const out = path.join(outDir, name);
  await page.locator('.term').screenshot({ path: out });
  await browser.close();
  console.log('rendered', out, fs.statSync(out).size, 'bytes');
}

(async () => {
  await shot('run_terminal_1_baseline.png', 'experiment.py — 基线: 模板钓鱼', base);
  await shot('run_terminal_2_attack.png', 'experiment.py — 攻击: 个性化钓鱼', attack);
  await shot('run_terminal_3_summary.png', 'experiment.py — 汇总', summary);
})().catch(e => { console.error(e); process.exit(1); });
