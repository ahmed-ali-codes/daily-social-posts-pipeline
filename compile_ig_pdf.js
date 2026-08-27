const puppeteer = require('puppeteer-core');
const fs = require('fs');
const path = require('path');

(async () => {
  const browser = await puppeteer.launch({
    executablePath: "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    args: ['--no-sandbox', '--disable-setuid-sandbox']
  });

  const page = await browser.newPage();
  
  let html = '<html><body style="margin:0;padding:0;">';
  for (let i = 1; i <= 5; i++) {
    const file = path.join(__dirname, `instagram-carousel-0${i}.png`);
    if (fs.existsSync(file)) {
      const base64 = fs.readFileSync(file).toString('base64');
      html += `<img src="data:image/png;base64,${base64}" style="width:1080px;height:1080px;display:block;page-break-after:always;" />`;
    }
  }
  html += '</body></html>';
  
  await page.setContent(html, { waitUntil: 'networkidle0' });
  
  const dateStr = new Date().toISOString().slice(0, 10);
  const outDir = path.join(__dirname, 'carousel-routine', 'output', dateStr, 'carousel-eco');
  fs.mkdirSync(outDir, { recursive: true });
  
  const outPath = path.join(outDir, '{{BRAND_SHORT_NAME_LOWER}}-carousel.pdf');
  
  await page.pdf({
    path: outPath,
    width: 1080,
    height: 1080,
    printBackground: true,
    pageRanges: ''
  });
  
  console.log(`Generated {{BRAND_SHORT_NAME}} Carousel PDF at ${outPath}`);
  await browser.close();
})();
