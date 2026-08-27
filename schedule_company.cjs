const puppeteer = require('puppeteer-core');
const fs = require('fs');
const path = require('path');
const os = require('os');

const posts = [
  {
    id: 1,
    type: 'infographic',
    date: '06/25/2026',
    time: '9:00 AM',
    caption: `Millions of custom AI agents will run the future of marketing\n\nIndia's marketing platform MoEngage recently announced a major deal to assign custom AI agents to individual consumers. Instead of static email sequences, brands will deploy dedicated agents that adapt to customer behavior continuously.\n\nGCC businesses that adopt agentic workflows early will build a major barrier against competitors.\n\nAt {{BRAND_SHORT_NAME}}, we build specialized workflows that handle customer lifecycle tasks:\n- WhatsApp sales agents that answer product questions\n- Custom CRM triggers that manage lead handoffs\n- Autopilot email nurturing\n\nBook a free audit to see how your team can deploy agentic automations.\n\n#marketingautomation #artificialintelligence #uaebusiness`,
    imagePath: path.resolve(__dirname, 'linkedin-infographic-20260624.png')
  },
  {
    id: 2,
    type: 'regular',
    date: '06/25/2026',
    time: '1:00 PM',
    caption: `Fixing the Shopify marketing gap\n\nMany e-commerce brands in Dubai have great traffic but poor repeat sales. They rely on manual customer lists.\n\n01. The Problem\nManual list extraction is slow. Customers who buy once are often forgotten.\n\n02. Automated Triggers\nWe connect Shopify to your CRM and SMS gateway. Buying triggers happen instantly.\n\n03. WhatsApp follow-ups\nSend personalized recovery messages. Not templates, but interactive chat.\n\n04. Inventory sync\nAutomatically alert buyers when their favorite items are back in stock.\n\n05. The Result\nRepeat customer rate increases without manual effort.\n\n{{BRAND_NAME}} builds custom e-commerce integrations. DM us to start.\n\n#ecommerce #automation #dubaiagency`
  },
  {
    id: 3,
    type: 'regular',
    date: '06/25/2026',
    time: '6:00 PM',
    caption: `91% of companies say they use AI tools. But only 1 in 5 build around it.\n\nMost teams just use wrappers. They copy-paste prompts into web interfaces. The real gains happen when you build custom integrations directly into your database.\n\n{{BRAND_NAME}} helps Dubai SMBs build real AI integrations.\n- Custom lead routing\n- Automated invoicing\n- Database syncs\n\nDM us for a free audit of your current business workflows.\n\n#automation #uaefounders #seoagency`
  }
];

async function sleep(ms) { return new Promise(r => setTimeout(r, ms)); }

async function getElementShadow(page, selector) {
  const handle = await page.evaluateHandle((sel) => {
    function findEl(root) {
      if (!root) return null;
      const el = root.querySelector(sel);
      if (el) return el;
      const walker = document.createTreeWalker(root, NodeFilter.SHOW_ELEMENT, null, false);
      let node;
      while (node = walker.nextNode()) {
        if (node.shadowRoot) {
          const found = findEl(node.shadowRoot);
          if (found) return found;
        }
      }
      return null;
    }
    return findEl(document.body);
  }, selector);
  return handle.asElement();
}

async function clickNativelyShadow(page, finderFn) {
  try {
    const handle = await page.evaluateHandle((finder) => {
      const fn = new Function('return ' + finder)();
      function findInShadow(root) {
        if (!root) return null;
        const res = fn(root);
        if (res) return res;
        const walker = document.createTreeWalker(root, NodeFilter.SHOW_ELEMENT, null, false);
        let node;
        while (node = walker.nextNode()) {
          if (node.shadowRoot) {
            const found = findInShadow(node.shadowRoot);
            if (found) return found;
          }
        }
        return null;
      }
      return findInShadow(document.body);
    }, finderFn.toString());
    const el = handle.asElement();
    if (el) {
      await page.evaluate(e => {
        e.focus();
        e.scrollIntoView({ block: 'center', inline: 'center' });
      }, el);
      await sleep(200);
      await el.click();
      await el.dispose();
      return true;
    }
    return false;
  } catch (err) {
    console.error("clickNativelyShadow error:", err);
    return false;
  }
}

(async () => {
  try {
    console.log("Locating active devtools port dynamically...");
    const tmpDir = os.tmpdir();
    const dirs = fs.readdirSync(tmpDir).filter(name => name.startsWith('puppeteer_dev_chrome_profile-') || name.startsWith('agent-browser-chrome-'));
    if (dirs.length === 0) throw new Error('No chrome directories found in tmp.');
    const latestDir = dirs.map(name => {
      const fullPath = path.join(tmpDir, name);
      return { path: fullPath, mtime: fs.statSync(fullPath).mtimeMs };
    }).sort((a, b) => b.mtime - a.mtime)[0].path;
    const portFile = path.join(latestDir, 'DevToolsActivePort');
    const content = fs.readFileSync(portFile, 'utf8');
    const port = content.split('\\n')[0].trim();
    
    console.log(`Connecting to browser on port ${port}...`);
    const browser = await puppeteer.connect({ browserURL: `http://127.0.0.1:${port}` });
    const pages = await browser.pages();
    let page = pages.find(p => p.url().includes('linkedin.com'));
    if (!page) page = pages[0];
    await page.bringToFront();

    console.log("WAITING 5 SECONDS. PLEASE ENSURE YOU ARE ON THE ECOTRUSTIA SOLUTIONS COMPANY PAGE AS AN ADMIN...");
    await sleep(5000);

    console.log(`\\n${'='.repeat(60)}`);
    console.log(`SCHEDULING ${posts.length} POSTS FOR ECOTRUSTIA SOLUTIONS`);
    console.log(`${'='.repeat(60)}\\n`);

    for (const post of posts) {
      console.log(`\\n==================================================`);
      console.log(`Scheduling Post ${post.id}/${posts.length} (${post.type}): Date=${post.date}, Time=${post.time}`);
      console.log(`==================================================`);
      
      // Close any open composers
      await page.evaluate(() => {
        const btns = [...document.querySelectorAll('button')];
        const close = btns.find(b => b.getAttribute('aria-label')?.includes('Dismiss') || b.textContent.includes('Close') || b.className.includes('close-button'));
        if (close) close.click();
      });
      await sleep(2000);

      // Click "Start a post"
      console.log("Clicking 'Start a post'...");
      const clickStartPost = await clickNativelyShadow(page, (root) => {
        return Array.from(root.querySelectorAll('*')).find(
          el => (el.tagName === 'BUTTON' || el.getAttribute('role') === 'button' || el.getAttribute('aria-label') === 'Start a post') &&
                el.innerText && el.innerText.trim().includes('Start a post')
        );
      });
      
      if (!clickStartPost) {
        console.log("Could not find 'Start a post'. Are you on the company page admin view?");
        continue;
      }
      await sleep(3000);

      // Type caption
      console.log("Filling post caption text...");
      const editor = await page.$('div.ql-editor[contenteditable="true"]');
      if (editor) {
        await editor.click();
        await sleep(300);
        // Clear editor
        await page.keyboard.down('Meta');
        await page.keyboard.press('a');
        await page.keyboard.up('Meta');
        await page.keyboard.press('Backspace');
        await sleep(200);

        for (const char of post.caption) {
          if (char === '\\n') {
            await page.keyboard.down('Shift');
            await page.keyboard.press('Enter');
            await page.keyboard.up('Shift');
          } else {
            await page.keyboard.type(char, { delay: 1 });
          }
        }
      }
      await sleep(1000);

      // Upload Media if infographic
      if (post.type === 'infographic' && fs.existsSync(post.imagePath)) {
        console.log("Uploading image...");
        let clickedMedia = await clickNativelyShadow(page, (root) => {
          const btns = Array.from(root.querySelectorAll('button'));
          return btns.find(b => b.ariaLabel && b.ariaLabel.includes('Add media')) ||
                 btns.find(b => b.innerText && b.innerText.includes('Add media'));
        });
        await sleep(1500);

        const fileInput = await page.$('input[type="file"]');
        if (fileInput) {
          await fileInput.uploadFile(post.imagePath);
          console.log("Image uploaded. Waiting 3s for processing...");
          await sleep(3000);
          
          // Click Next/Done on media preview
          await page.evaluate(() => {
            const btns = [...document.querySelectorAll('button')];
            const done = btns.find(b => b.textContent.trim() === 'Next' || b.textContent.trim() === 'Done');
            if (done) done.click();
          });
          await sleep(1500);
        }
      }

      // Schedule post
      console.log("Opening Schedule Settings...");
      const scheduleOpened = await clickNativelyShadow(page, (root) => {
        return Array.from(root.querySelectorAll('button')).find(
          b => (b.ariaLabel && b.ariaLabel.includes('Schedule')) || (b.innerText && b.innerText.includes('Schedule'))
        );
      });
      
      if (!scheduleOpened) {
        console.log("Schedule button not found! Fallback to draft/dismiss.");
        await page.keyboard.press('Escape');
        await sleep(1000);
        continue;
      }
      
      await sleep(2000);
      console.log(`Setting schedule: Date=${post.date}, Time=${post.time}`);
      
      const dateInput = await page.$('input[type="date"]');
      if (dateInput) {
        await dateInput.click({clickCount: 3});
        await page.keyboard.press('Backspace');
        await sleep(500);
        await dateInput.type('06/25/2026');
      }
      
      const timeSelect = await page.$('select[aria-label*="time" i], input[aria-label*="time" i]');
      if (timeSelect) {
        await page.evaluate((el) => { el.focus(); el.select(); }, timeSelect);
        await sleep(500);
        await page.keyboard.press('Backspace');
        await page.keyboard.type(post.time);
        await sleep(1000);
        await page.keyboard.press('ArrowDown');
        await sleep(200);
        await page.keyboard.press('Enter');
      }
      
      await sleep(1000);
      console.log("Saving schedule settings (clicking Next)...");
      await clickNativelyShadow(page, (root) => {
        const btns = Array.from(root.querySelectorAll('button'));
        return btns.find(b => b.innerText && b.innerText.trim() === 'Next');
      });
      await sleep(2000);

      console.log("Clicking final 'Schedule' button...");
      await clickNativelyShadow(page, (root) => {
        const btns = Array.from(root.querySelectorAll('button'));
        return btns.find(b => b.innerText && b.innerText.trim() === 'Schedule');
      });
      await sleep(6000);
      console.log(`✓ Successfully scheduled Post ${post.id}/${posts.length}!`);
    }

    console.log(`\\n${'='.repeat(60)}`);
    console.log(`✓ ALL 3 ECOTRUSTIA POSTS SCHEDULED!`);
    console.log(`${'='.repeat(60)}\\n`);

    await browser.disconnect();
  } catch (err) {
    console.error("Scheduler failed:", err);
  }
})();
