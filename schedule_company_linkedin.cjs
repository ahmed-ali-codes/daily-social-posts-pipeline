/**
 * schedule_{{BRAND_SHORT_NAME_LOWER}}_linkedin.cjs
 * ================================
 * Schedules {{BRAND_NAME}}' 3 company LinkedIn posts.
 * Reads from posts_today.json → {{BRAND_SHORT_NAME_LOWER}}_linkedin array.
 * Times: 9:00 AM, 12:00 PM, 3:00 PM IST
 *
 * CRITICAL: This script switches the author identity in the
 * composer modal to "{{BRAND_NAME}}" before posting.
 *
 * Run: node schedule_{{BRAND_SHORT_NAME_LOWER}}_linkedin.cjs
 */

const puppeteer = require('puppeteer-core');
const fs = require('fs');
const path = require('path');
const os = require('os');

// ============================================================
// PUPPETEER SHADOW DOM HELPERS
// ============================================================
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
      document.querySelectorAll('.msg-overlay-container,[class*="msg-overlay"],#msg-overlay')
        .forEach(el => el.remove());
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
  await page.keyboard.type(value, {delay: 100});
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
  await page.keyboard.type(value, {delay: 100});
  await new Promise(r => setTimeout(r, 1500));
  await page.keyboard.press('ArrowDown');
  await new Promise(r => setTimeout(r, 400));
  await page.keyboard.press('Enter');
  await el.dispose();
  await new Promise(r => setTimeout(r, 800));
}

function findChromePort() {
  const tmpDir = os.tmpdir();
  const dirs = fs.readdirSync(tmpDir).filter(n =>
    n.startsWith('puppeteer_dev_chrome_profile-') || n.startsWith('agent-browser-chrome-')
  );
  if (dirs.length === 0) throw new Error('No Chrome session found in temp. Is agent-browser running?');
  const latest = dirs.map(n => {
    const fullPath = path.join(tmpDir, n);
    return { path: fullPath, mtime: fs.statSync(fullPath).mtimeMs };
  }).sort((a, b) => b.mtime - a.mtime)[0].path;
  const portFile = path.join(latest, 'DevToolsActivePort');
  return fs.readFileSync(portFile, 'utf8').split('\n')[0].trim();
}

// ============================================================
// MAIN — SCHEDULE ECOTRUSTIA'S 3 POSTS
// ============================================================
(async () => {
  const postsFile = path.resolve(__dirname, 'posts_today.json');
  if (!fs.existsSync(postsFile)) {
    console.error('ERROR: posts_today.json not found. Run generate_all_content_gemini.py first.');
    process.exit(1);
  }
  const postsData = JSON.parse(fs.readFileSync(postsFile, 'utf8'));
  const posts = postsData.{{BRAND_SHORT_NAME_LOWER}}_linkedin || [];

  if (posts.length === 0) {
    console.error('ERROR: No {{BRAND_SHORT_NAME}} LinkedIn posts found in posts_today.json');
    process.exit(1);
  }

  for (const post of posts) {
    if (post.type === 'carousel') {
      const dir = post.carousel_pdf;
      if (fs.existsSync(dir)) {
        const pdfs = fs.readdirSync(dir).filter(f => f.endsWith('.pdf'));
        if (pdfs.length > 0) {
          post.assetPath = path.join(dir, pdfs[pdfs.length - 1]);
          post.title = post.carousel_title || '{{BRAND_NAME}} Setup';
        }
      }
      if (!post.assetPath) {
        console.warn(`⚠ Carousel PDF not found at ${dir}. Post 2 will be text-only.`);
        post.type = 'text';
      }
    } else if (post.type === 'infographic') {
      const fn = post.infographic_png;
      if (fs.existsSync(fn)) {
        post.assetPath = path.resolve(fn);
      } else {
        console.warn(`⚠ Infographic PNG not found: ${fn}. Post 1 will be text-only.`);
        post.type = 'text';
      }
    }
  }

  const screenshotDir = path.resolve(__dirname, 'slack_downloads');
  if (!fs.existsSync(screenshotDir)) fs.mkdirSync(screenshotDir, { recursive: true });

  console.log('\n' + '='.repeat(60));
  console.log(`SCHEDULING ECOTRUSTIA LINKEDIN — ${postsData.date}`);
  console.log(`Posts scheduled for: ${postsData.schedule_date}`);
  console.log('='.repeat(60));

  let browser, page;
  try {
    const port = findChromePort();
    browser = await puppeteer.connect({ browserURL: `http://127.0.0.1:${port}` });
    const pages = await browser.pages();
    page = pages.find(p => p.url().includes('linkedin.com'));
    if (!page) throw new Error('LinkedIn page not found. Open LinkedIn in agent-browser first.');
    await page.bringToFront();
    await page.setViewport({ width: 1280, height: 1200 });

    for (const post of posts) {
      const prefix = `${screenshotDir}/eco_li_post_${post.id}_${post.type}`;
      console.log(`\n${'─'.repeat(50)}`);
      console.log(`{{BRAND_SHORT_NAME}} Post ${post.id}/3 | ${post.type} | ${post.slot} IST`);
      console.log(`${'─'.repeat(50)}`);

      console.log('Navigating to LinkedIn feed...');
        await page.goto('https://www.linkedin.com/company/105396729/admin/page-posts/published/', { waitUntil: 'domcontentloaded', timeout: 15000 });
      await new Promise(r => setTimeout(r, 3000));

      // Open post composer
      console.log("Clicking 'Start a post'...");
      const started = await clickNativelyShadow(page, (root) =>
        Array.from(root.querySelectorAll('a[href*="sharebox"], button, div[role="button"]')).find(el =>
          (el.innerText || '').trim().includes('Start a post') || 
          (el.getAttribute('href') || '').includes('sharebox')
        )
      );
      if (!started) throw new Error("Could not find 'Start a post' button");

      const editorSelector = '.ql-editor,[contenteditable="true"]';
      await waitForSelectorShadow(page, editorSelector, 15000);
      await new Promise(r => setTimeout(r, 1500));

      // No need to switch author since we are on the company page

      // Handle file uploads (Infographic or Carousel)
      if ((post.type === 'infographic' || post.type === 'carousel') && post.assetPath) {
        console.log(`Attaching ${post.type}...`);
        
        let clickedAdd = false;
        
        if (post.type === 'infographic') {
          // Click Add Media / Image
          clickedAdd = await clickNativelyShadow(page, (root) => {
            const btns = Array.from(root.querySelectorAll('button'));
            return btns.find(b => (b.ariaLabel || '').includes('Add media')) ||
                   btns.find(b => (b.ariaLabel || '').includes('image'));
          });
        } else if (post.type === 'carousel') {
          // Click Add Document
          clickedAdd = await clickNativelyShadow(page, (root) => {
            const btns = Array.from(root.querySelectorAll('button'));
            return btns.find(b => (b.ariaLabel || '').includes('Add a document')) ||
                   btns.find(b => (b.innerText || '').toLowerCase().includes('document'));
          });
          
          if (!clickedAdd) {
            await clickNativelyShadow(page, (root) =>
              Array.from(root.querySelectorAll('button')).find(b =>
                (b.ariaLabel || '').includes('More') || (b.innerText || '').includes('More')
              )
            );
            await new Promise(r => setTimeout(r, 1200));
            clickedAdd = await clickNativelyShadow(page, (root) => {
              const btns = Array.from(root.querySelectorAll('button'));
              return btns.find(b => (b.ariaLabel || '').includes('Add a document')) ||
                     btns.find(b => (b.innerText || '').toLowerCase().includes('document'));
            });
          }
        }

        if (!clickedAdd) throw new Error(`Could not find upload button for ${post.type}`);
        await new Promise(r => setTimeout(r, 2000));

        const fileInputsHandle = await page.evaluateHandle(() => {
          function findAll(root, arr = []) {
            const walker = document.createTreeWalker(root, NodeFilter.SHOW_ELEMENT, null, false);
            let node;
            while (node = walker.nextNode()) {
              if (node.tagName === 'INPUT' && node.type === 'file') arr.push(node);
              if (node.shadowRoot) findAll(node.shadowRoot, arr);
            }
            return arr;
          }
          return findAll(document.body);
        });
        
        const fileInputsLength = await page.evaluate(inputs => inputs.length, fileInputsHandle);
        if (fileInputsLength === 0) throw new Error('File input not found');
        
        for (let i = 0; i < fileInputsLength; i++) {
          const fileInput = await page.evaluateHandle((inputs, i) => inputs[i], fileInputsHandle, i);
          try {
            await fileInput.asElement().uploadFile(post.assetPath);
          } catch(e) {}
        }
        console.log(`File uploaded: ${path.basename(post.assetPath)}. Waiting...`);
        await new Promise(r => setTimeout(r, 5000));

        // If carousel, set title
        if (post.type === 'carousel') {
          await waitForSelectorShadow(page, 'input[placeholder*="title"]', 10000);
          const titleInput = await getElementShadow(page, 'input[placeholder*="title"]');
          if (titleInput) {
            await titleInput.focus();
            await page.keyboard.type(post.title || '{{BRAND_NAME}} Carousel');
            await titleInput.dispose();
          }
        }

        // Click Done/Next on media modal
        await clickNativelyShadowRetry(page, (root) =>
          Array.from(root.querySelectorAll('button')).find(b => {
            const txt = (b.innerText || '').trim();
            return (txt === 'Done' || txt === 'Next') && !b.disabled && !b.className.includes('vjs-');
          })
        );
        await new Promise(r => setTimeout(r, 3000));
      }

      // Fill caption
      console.log('Typing caption...');
      await waitForSelectorShadow(page, editorSelector, 15000);
      const editorEl = await getElementShadow(page, editorSelector);
      await editorEl.focus();
      await page.evaluate(el => {
        el.focus();
        document.execCommand('selectAll', false, null);
        document.execCommand('delete', false, null);
      }, editorEl);
      await new Promise(r => setTimeout(r, 800));

      const paragraphs = post.caption.split('\n');
      for (let i = 0; i < paragraphs.length; i++) {
        if (i > 0) { await page.keyboard.press('Enter'); await new Promise(r => setTimeout(r, 120)); }
        if (paragraphs[i]) { await page.keyboard.type(paragraphs[i]); await new Promise(r => setTimeout(r, 120)); }
      }
      await new Promise(r => setTimeout(r, 1500));
      await editorEl.dispose();
      await page.screenshot({ path: `${prefix}_draft.png` });

      // Open schedule modal
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
      await new Promise(r => setTimeout(r, 2500));

      // Set date and time
      console.log(`Setting date: ${post.date}, time: ${post.slot}`);
      await fillFieldShadow(page,
        'input[placeholder*="Date"],input[aria-label*="date"],input[id*="date"]', post.date);

      let t = post.slot;
      if (t.startsWith('0')) t = t.substring(1);
      await fillTimeCombobox(page,
        'input[placeholder*="Time"],input[aria-label*="time"],input[id*="time"],input[role="combobox"]', t);

      await page.screenshot({ path: `${prefix}_schedule.png` });

      // Click Next
      const clickedNext = await clickNativelyShadow(page, (root) =>
        Array.from(root.querySelectorAll('button')).find(b => (b.innerText || '').trim() === 'Next')
      );
      if (!clickedNext) throw new Error('Could not click Next');
      await new Promise(r => setTimeout(r, 2500));

      // Click Schedule (final)
      const clickedFinal = await clickNativelyShadow(page, (root) =>
        Array.from(root.querySelectorAll('button')).find(b => (b.innerText || '').trim() === 'Schedule')
      );
      if (!clickedFinal) throw new Error('Could not click final Schedule button');

      console.log('Waiting for confirmation...');
      await new Promise(r => setTimeout(r, 6000));

      const closed = await page.evaluate(() => !document.querySelector('.share-box-v2__modal, .artdeco-modal__content .ql-editor'));
      if (!closed) throw new Error('Composer did not close — scheduling may have failed');

      console.log(`✓ {{BRAND_SHORT_NAME}} Post ${post.id} scheduled for ${post.date} at ${post.slot} IST`);
    }

    console.log('\n' + '='.repeat(60));
    console.log(`✓ ALL 3 ECOTRUSTIA POSTS SCHEDULED for ${postsData.schedule_date}`);
    console.log('='.repeat(60));
    process.exit(0);

  } catch (err) {
    console.error('\n✗ SCHEDULING ERROR:', err.message);
    if (page) {
      try {
        await page.screenshot({ path: path.resolve(__dirname, 'slack_downloads', 'eco_li_error.png') });
        console.log('Error screenshot saved.');
      } catch (_) {}
    }
    process.exit(1);
  }
})();
