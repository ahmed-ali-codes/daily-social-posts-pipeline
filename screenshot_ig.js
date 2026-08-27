const puppeteer = require('puppeteer-core');
const fs = require('fs');
const path = require('path');

(async () => {
  const browser = await puppeteer.launch({
    executablePath: "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    args: ['--no-sandbox', '--disable-setuid-sandbox', '--allow-file-access-from-files', '--disable-web-security'],
    protocolTimeout: 180000
  });

  const filesToScreenshot = [
    'instagram-image-1.html',
    'instagram-image-3.html',
    'instagram-carousel-01.html',
    'instagram-carousel-02.html',
    'instagram-carousel-03.html',
    'instagram-carousel-04.html',
    'instagram-carousel-05.html'
  ];

  for (const file of filesToScreenshot) {
    const slidePath = path.join(__dirname, file);
    const outPath = path.join(__dirname, file.replace('.html', '.png'));

    const page = await browser.newPage();
    await page.setDefaultNavigationTimeout(60000);
    await page.setViewport({ width: 1080, height: 1080 });
    await page.goto(`file://${slidePath}`, { waitUntil: 'domcontentloaded', timeout: 30000 });
    await new Promise(r => setTimeout(r, 1500));
    try {
      await page.screenshot({ path: outPath, clip: {x:0, y:0, width:1080, height:1080}, timeout: 60000 });
      console.log(`✓ ${outPath}`);
    } catch(e) {
      console.error(`✗ ${file}: ${e.message}`);
    }
    await page.close();
  }

  await browser.close();
  console.log('IG_SCREENSHOTS_DONE');
})();
