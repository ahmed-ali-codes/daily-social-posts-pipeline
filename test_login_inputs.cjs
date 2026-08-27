const puppeteer = require('puppeteer-core');
const fs = require('fs');

(async () => {
  const browser = await puppeteer.launch({
    executablePath: '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
    headless: false,
    args: ['--window-size=1280,1200']
  });
  
  const page = (await browser.pages())[0];
  await page.goto('https://www.linkedin.com/login', { waitUntil: 'networkidle2' });
  
  // Dump input elements
  const inputs = await page.evaluate(() => {
    return Array.from(document.querySelectorAll('input')).map(i => ({
      id: i.id,
      name: i.name,
      type: i.type,
      class: i.className,
      placeholder: i.placeholder || ''
    }));
  });
  console.log('Inputs found:', JSON.stringify(inputs, null, 2));
  
  await browser.close();
})();
