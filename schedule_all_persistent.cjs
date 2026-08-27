/**
 * schedule_all_persistent.cjs
 * ===========================
 * Launches Chrome with a PERSISTENT profile, so logins are remembered.
 * Checks for login, and if logged in, schedules all 7 posts.
 */

const puppeteer = require('puppeteer-core');
const fs = require('fs');
const path = require('path');
const os = require('os');

const ECOTRUSTIA_PAGE = 'https://www.linkedin.com/company/105396729/admin/page-posts/published/';

// Puppeteer shadow DOM helpers (same as before)
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
async function waitForSelectorShadow(page, selector, timeout = 15000) {
  const start = Date.now();
  while (Date.now() - start < timeout) {
    const el = await getElementShadow(page, selector);
    if (el) { await el.dispose(); return true; }
    await new Promise(r => setTimeout(r, 500));
  }
  throw new Error(`Timeout waiting for: ${selector}`);
}
async function clickNativelyShadow(page, finderFn) {
  try {
    await page.evaluate(() => {
      document.querySelectorAll('.msg-overlay-container,[class*="msg-overlay"],#msg-overlay').forEach(el => el.remove());
    });
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
      try {
        await page.evaluate(e => { e.focus(); e.scrollIntoView({ block: 'center' }); }, el);
        await new Promise(r => setTimeout(r, 200));
        await el.click();
      } catch {
        await page.evaluate(e => {
          const rect = e.getBoundingClientRect();
          const x = rect.left + rect.width / 2, y = rect.top + rect.height / 2;
          const opts = { bubbles: true, cancelable: true, view: window, clientX: x, clientY: y };
          e.dispatchEvent(new MouseEvent('mousedown', opts));
          e.focus();
          e.dispatchEvent(new MouseEvent('mouseup', opts));
          e.dispatchEvent(new MouseEvent('click', opts));
        }, el);
      }
      await el.dispose();
      return true;
    }
    return false;
  } catch (err) {
    console.error('clickNativelyShadow error:', err.message);
    return false;
  }
}
async function clickNativelyShadowRetry(page, finderFn, timeout = 15000) {
  const start = Date.now();
  while (Date.now() - start < timeout) {
    if (await clickNativelyShadow(page, finderFn)) return true;
    await new Promise(r => setTimeout(r, 1000));
  }
  return false;
}
async function fillFieldShadow(page, selector, value) {
  const el = await getElementShadow(page, selector);
  if (!el) throw new Error(`Cannot find field: ${selector}`);
  await page.evaluate(input => { input.focus(); input.select(); }, el);
  await new Promise(r => setTimeout(r, 400));
  await page.keyboard.press('Backspace');
  await new Promise(r => setTimeout(r, 400));
  await page.keyboard.type(value, {delay: 50});
  await page.keyboard.press('Enter');
  await new Promise(r => setTimeout(r, 200));
  await page.keyboard.press('Escape');
  await new Promise(r => setTimeout(r, 200));
  await page.keyboard.press('Tab');
  await el.dispose();
  await new Promise(r => setTimeout(r, 800));
}
async function fillTimeCombobox(page, selector, value) {
  const el = await getElementShadow(page, selector);
  if (!el) throw new Error(`Cannot find time combobox: ${selector}`);
  await page.evaluate(input => { input.focus(); input.select(); }, el);
  await new Promise(r => setTimeout(r, 400));
  await page.keyboard.press('Backspace');
  await new Promise(r => setTimeout(r, 400));
  await page.keyboard.type(value, {delay: 50});
  await new Promise(r => setTimeout(r, 1500));
  await page.keyboard.press('ArrowDown');
  await new Promise(r => setTimeout(r, 400));
  await page.keyboard.press('Enter');
  await el.dispose();
  await new Promise(r => setTimeout(r, 800));
}
const sleep = ms => new Promise(r => setTimeout(r, ms));

// ============================================================
// MAIN
// ============================================================
(async () => {
  const postsFile = path.resolve(__dirname, 'posts_today.json');
  if (!fs.existsSync(postsFile)) {
    console.error('ERROR: posts_today.json not found.');
    process.exit(1);
  }
  const postsData = JSON.parse(fs.readFileSync(postsFile, 'utf8'));
  const ahmedPosts = postsData.ahmed_linkedin || [];
  const ecoPosts = postsData.{{BRAND_SHORT_NAME_LOWER}}_linkedin || [];

  for (const post of ahmedPosts) {
    if (post.type === 'carousel' && post.carousel_pdf && fs.existsSync(post.carousel_pdf)) {
      const pdfs = fs.readdirSync(post.carousel_pdf).filter(f => f.endsWith('.pdf'));
      if (pdfs.length > 0) post.assetPath = path.resolve(post.carousel_pdf, pdfs[pdfs.length - 1]);
    }
  }
  for (const post of ecoPosts) {
    if (post.type === 'carousel' && post.carousel_pdf && fs.existsSync(post.carousel_pdf)) {
      const pdfs = fs.readdirSync(post.carousel_pdf).filter(f => f.endsWith('.pdf'));
      if (pdfs.length > 0) post.assetPath = path.resolve(post.carousel_pdf, pdfs[pdfs.length - 1]);
    } else if (post.type === 'infographic' && post.infographic_png && fs.existsSync(post.infographic_png)) {
      post.assetPath = path.resolve(post.infographic_png);
    }
  }

  const screenshotDir = path.resolve(__dirname, 'slack_downloads');
  if (!fs.existsSync(screenshotDir)) fs.mkdirSync(screenshotDir, { recursive: true });

  const userDataDir = path.resolve(os.homedir(), '.agent-browser-data');
  console.log(`\nLaunching Chrome with persistent profile at: ${userDataDir}`);
  
  const browser = await puppeteer.launch({
    executablePath: '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
    headless: false,
    userDataDir: userDataDir,
    args: [
      '--no-sandbox',
      '--disable-setuid-sandbox',
      '--disable-gpu',
      '--disable-dev-shm-usage',
      '--window-size=1280,1200',
      '--lang=en-US'
    ],
    defaultViewport: { width: 1280, height: 1200 }
  });

  const page = (await browser.pages())[0];
  await page.setExtraHTTPHeaders({ 'Accept-Language': 'en-US,en;q=0.9' });

  console.log('Navigating to LinkedIn...');
  await page.goto('https://www.linkedin.com/feed/', { waitUntil: 'domcontentloaded', timeout: 30000 });
  await sleep(4000);

  let currentUrl = page.url();
  if (currentUrl.includes('login') || currentUrl.includes('signup')) {
    console.log('\n⚠️  YOU ARE NOT LOGGED IN.');
    console.log('Please log into LinkedIn manually in the Chrome window that just opened.');
    console.log('Waiting 90 seconds for you to log in...\n');
    await sleep(90000);
    
    currentUrl = page.url();
    if (currentUrl.includes('login') || currentUrl.includes('signup')) {
      console.error('ERROR: Still not logged in. Cannot proceed.');
      process.exit(1);
    }
  }

  console.log('✓ Logged in! Proceeding to schedule posts...');

  async function schedulePost(post, label, navigateUrl) {
    const prefix = `${screenshotDir}/${label}_post_${post.id}_${post.type}`;
    console.log(`\n──────────────────────────────────────────────────`);
    console.log(`${label} Post ${post.id} | ${post.type} | ${post.slot}`);
    console.log(`──────────────────────────────────────────────────`);
    
    await page.goto(navigateUrl, { waitUntil: 'domcontentloaded', timeout: 15000 });
    await sleep(4000);

    await page.evaluate(() => document.querySelectorAll('.msg-overlay-container,[class*="msg-overlay"],#msg-overlay').forEach(el => el.remove()));
    await page.evaluate(() => {
      const btn = Array.from(document.querySelectorAll('button')).find(b => (b.getAttribute('aria-label') || '').includes('Dismiss') || (b.innerText || '').includes('Dismiss'));
      if (btn) btn.click();
    });
    await sleep(1500);

    let started = await clickNativelyShadow(page, (root) =>
      Array.from(root.querySelectorAll('a[href*="sharebox"], button, div[role="button"]')).find(el =>
        (el.innerText || '').trim().includes('Start a post') || (el.innerText || '').trim().includes('ابدأ منشورًا') || (el.getAttribute('href') || '').includes('sharebox')
      )
    );
    if (!started) {
      started = await page.evaluate(() => {
        const trigger = document.querySelector('button.share-box-feed-entry__trigger');
        if (trigger) { trigger.click(); return true; }
        return false;
      });
    }
    if (!started) throw new Error("Could not find 'Start a post' button");

    const editorSelector = '.ql-editor,[contenteditable="true"]';
    await waitForSelectorShadow(page, editorSelector, 15000);
    await sleep(1000);

    if ((post.type === 'carousel' || post.type === 'infographic') && post.assetPath) {
      console.log(`Attaching ${post.type}...`);
      let clickedAdd = await clickNativelyShadow(page, (root) => {
        const btns = Array.from(root.querySelectorAll('button'));
        if (post.type === 'infographic') return btns.find(b => (b.ariaLabel || '').includes('Add media') || (b.ariaLabel || '').includes('image'));
        return btns.find(b => (b.ariaLabel || '').includes('Add a document') || (b.innerText || '').toLowerCase().includes('document'));
      });
      
      if (!clickedAdd && post.type === 'carousel') {
        await clickNativelyShadow(page, (root) => Array.from(root.querySelectorAll('button')).find(b => (b.ariaLabel || '').includes('More') || (b.innerText || '').includes('More')));
        await sleep(1000);
        clickedAdd = await clickNativelyShadow(page, (root) => Array.from(root.querySelectorAll('button')).find(b => (b.ariaLabel || '').includes('Add a document') || (b.innerText || '').toLowerCase().includes('document')));
      }

      await sleep(2000);
      const fileInputHandle = await page.evaluateHandle(() => {
        function find(root) {
          const walker = document.createTreeWalker(root, NodeFilter.SHOW_ELEMENT, null, false);
          let node;
          while (node = walker.nextNode()) {
            if (node.tagName === 'INPUT' && node.type === 'file') return node;
            if (node.shadowRoot) { const f = find(node.shadowRoot); if (f) return f; }
          }
          return null;
        }
        return find(document.body);
      });
      const fileInput = fileInputHandle.asElement();
      if (!fileInput) throw new Error('File input not found');
      await fileInput.uploadFile(post.assetPath);
      console.log('File uploaded. Waiting 5s...');
      await sleep(5000);

      if (post.type === 'carousel') {
        try {
          await waitForSelectorShadow(page, 'input[placeholder*="title"]', 5000);
          const titleInput = await getElementShadow(page, 'input[placeholder*="title"]');
          if (titleInput) {
            await titleInput.focus();
            await page.keyboard.type(post.title || 'Builder Breakdown');
            await titleInput.dispose();
          }
        } catch(e) {}
      }

      await clickNativelyShadowRetry(page, (root) => Array.from(root.querySelectorAll('button')).find(b => {
        const txt = (b.innerText || '').trim();
        return (txt === 'Done' || txt === 'Next') && !b.disabled && !b.className.includes('vjs-');
      }));
      await sleep(2000);
    }

    console.log('Typing caption...');
    const editorEl = await getElementShadow(page, editorSelector);
    await editorEl.focus();
    await page.evaluate(el => { el.focus(); document.execCommand('selectAll', false, null); document.execCommand('delete', false, null); }, editorEl);
    await sleep(500);

    const paragraphs = post.caption.split('\n');
    for (let i = 0; i < paragraphs.length; i++) {
      if (i > 0) { await page.keyboard.press('Enter'); await sleep(50); }
      if (paragraphs[i]) { await page.keyboard.type(paragraphs[i], {delay: 5}); await sleep(50); }
    }
    await sleep(1000);
    await editorEl.dispose();
    await page.screenshot({ path: `${prefix}_draft.png` });

    console.log('Opening schedule modal...');
    const clickedSched = await clickNativelyShadow(page, (root) => {
      const modal = root.querySelector('.share-box,.artdeco-modal,[role="dialog"]');
      const container = modal || root;
      const buttons = Array.from(container.querySelectorAll('button'));
      const postBtn = buttons.find(b => (b.innerText || '').trim() === 'Post');
      if (postBtn && postBtn.previousElementSibling) return postBtn.previousElementSibling;
      return buttons.find(b => (b.ariaLabel || '').includes('Schedule'));
    });
    if (!clickedSched) throw new Error('Could not find Schedule icon button');
    await sleep(2000);

    await fillFieldShadow(page, 'input[placeholder*="Date"],input[aria-label*="date"],input[id*="date"]', post.date);
    let t = post.slot; if (t.startsWith('0')) t = t.substring(1);
    await fillTimeCombobox(page, 'input[placeholder*="Time"],input[aria-label*="time"],input[id*="time"],input[role="combobox"]', t);
    
    await clickNativelyShadow(page, (root) => Array.from(root.querySelectorAll('button')).find(b => (b.innerText || '').trim() === 'Next'));
    await sleep(2000);
    
    await clickNativelyShadow(page, (root) => Array.from(root.querySelectorAll('button')).find(b => (b.innerText || '').trim() === 'Schedule'));
    await sleep(4000);
    
    console.log(`✓ Post ${post.id} scheduled for ${post.date} at ${post.slot}`);
  }

  console.log(`\n=== SCHEDULING AHMED POSTS ===`);
  for (const post of ahmedPosts) {
    try { await schedulePost(post, 'ahmed', 'https://www.linkedin.com/feed/'); }
    catch (err) {
      console.error(`✗ ERROR on {{AUTHOR_NAME}} Post ${post.id}: ${err.message}`);
      await page.keyboard.press('Escape'); await sleep(1000);
    }
  }

  console.log(`\n=== SCHEDULING ECOTRUSTIA POSTS ===`);
  for (const post of ecoPosts) {
    try { await schedulePost(post, '{{BRAND_SHORT_NAME_LOWER}}', ECOTRUSTIA_PAGE); }
    catch (err) {
      console.error(`✗ ERROR on {{BRAND_SHORT_NAME}} Post ${post.id}: ${err.message}`);
      await page.keyboard.press('Escape'); await sleep(1000);
    }
  }

  console.log('\n✅ ALL LINKEDIN POSTS SCHEDULING COMPLETE');
})();
