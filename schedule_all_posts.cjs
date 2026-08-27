const puppeteer = require('puppeteer-core');
const fs = require('fs');
const path = require('path');
const os = require('os');

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
  const startTime = Date.now();
  while (Date.now() - startTime < timeout) {
    const el = await getElementShadow(page, selector);
    if (el) {
      await el.dispose();
      return true;
    }
    await new Promise(r => setTimeout(r, 500));
  }
  throw new Error(`Timeout waiting for shadow selector: ${selector}`);
}

async function clickNativelyShadow(page, finderFn) {
  try {
    await page.evaluate(() => {
      document.querySelectorAll('.msg-overlay-container, [class*="msg-overlay"], #msg-overlay').forEach(el => el.remove());
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
      const tagAndClass = await page.evaluate(e => {
        return `${e.tagName} class="${e.className}" text="${e.innerText ? e.innerText.trim().substring(0,30) : ''}"`;
      }, el);
      console.log(`clickNativelyShadow: Found element: <${tagAndClass}>`);
      try {
        await page.evaluate(e => {
          e.focus();
          e.scrollIntoView({ block: 'center', inline: 'center' });
        }, el);
        await new Promise(r => setTimeout(r, 200));
        await el.click();
      } catch (clickErr) {
        console.log("Puppeteer native click failed, falling back to programmatic event sequence:", clickErr.message);
        await page.evaluate(e => {
          const rect = e.getBoundingClientRect();
          const x = rect.left + rect.width / 2;
          const y = rect.top + rect.height / 2;
          const opts = { bubbles: true, cancelable: true, view: window, screenX: x, screenY: y, clientX: x, clientY: y };
          e.dispatchEvent(new PointerEvent('pointerdown', opts));
          e.dispatchEvent(new MouseEvent('mousedown', opts));
          e.focus();
          e.dispatchEvent(new PointerEvent('pointerup', opts));
          e.dispatchEvent(new MouseEvent('mouseup', opts));
          e.dispatchEvent(new MouseEvent('click', opts));
        }, el);
      }
      await el.dispose();
      return true;
    }
    return false;
  } catch (err) {
    console.error("clickNativelyShadow error:", err);
    return false;
  }
}

async function clickNativelyShadowRetry(page, finderFn, timeout = 15000) {
  const startTime = Date.now();
  while (Date.now() - startTime < timeout) {
    const clicked = await clickNativelyShadow(page, finderFn);
    if (clicked) return true;
    await new Promise(r => setTimeout(r, 1000));
  }
  return false;
}

async function fillFieldShadow(page, selector, value) {
  const el = await getElementShadow(page, selector);
  if (!el) throw new Error(`Could not find element to fill: ${selector}`);
  
  await page.evaluate((input) => {
    input.focus();
    input.select();
  }, el);
  
  await new Promise(r => setTimeout(r, 500));
  await page.keyboard.press('Backspace');
  
  await new Promise(r => setTimeout(r, 500));
  await page.keyboard.type(value);
  await page.keyboard.press('Enter');
  await new Promise(r => setTimeout(r, 200));
  await page.keyboard.press('Escape');
  await new Promise(r => setTimeout(r, 200));
  await page.keyboard.press('Tab');
  await el.dispose();
  await new Promise(r => setTimeout(r, 1000));
}

async function fillTimeComboboxShadow(page, selector, value) {
  const el = await getElementShadow(page, selector);
  if (!el) throw new Error(`Could not find combobox element to fill: ${selector}`);
  
  await page.evaluate((input) => {
    input.focus();
    input.select();
  }, el);
  
  await new Promise(r => setTimeout(r, 500));
  await page.keyboard.press('Backspace');
  
  await new Promise(r => setTimeout(r, 500));
  await page.keyboard.type(value);
  console.log(`Typed ${value} into time combobox, waiting for suggestions...`);
  await new Promise(r => setTimeout(r, 1500));
  
  await page.keyboard.press('ArrowDown');
  await new Promise(r => setTimeout(r, 500));
  await page.keyboard.press('Enter');
  await el.dispose();
  await new Promise(r => setTimeout(r, 1000));
}

// ==========================================
// ALL 11 POSTS — 4 per day across 3 days
// Schedule: 9:00 AM, 12:00 PM, 3:00 PM, 6:00 PM IST
// ==========================================

(async () => {
  const posts = [
    {
      id: 1,
      type: 'regular',
      date: '06/25/2026',
      time: '8:00 AM',
      caption: `Here is what I learned building custom lead gen engines after scraping city planning commission minutes\n\nA month ago, a civil engineer PM got laid off and started building. Instead of jumping to standard automation tools, they coded custom scrapers in Python.\n\nThey realized city planning documents are a goldmine. The minutes list rezoning requests. Rezoning requests mean land development. Land development means new builders, attorneys, and contractors are about to get hired.\n\nBy writing a script that reads these minutes, extracts the affected businesses, and enriches the contact info, they built a highly targeted pipeline.\n\nThree lessons from this:\n- Mine review data. Look at local trades businesses to spot cities with genuine labor shortages.\n- Avoid building spam engines. Keep email lists short and clean. apollo exports are often dirty and increase bounce rates.\n- Code your gateway. Using a Telegram gateway to manually review comment bot outputs keeps interactions authentic.\n\nDM me if you are trying to automate lead sourcing. I am building similar flows this week.\n\n#builderjourney #leadgeneration #automation`
    },
    {
      id: 2,
      type: 'regular',
      date: '06/25/2026',
      time: '12:00 PM',
      caption: `Vibe-coded automations are quietly breaking UAE business operations\n\nI keep talking to local founders who hired an "expert" to build n8n or Make scenarios. Three months later, the whole system stops working.\n\nHere are the 4 main reasons these setups fail in production:\n- Happy path thinking. Most builders plan for things to go right. The minute there is a timeout or a missing field, the entire pipeline crashes.\n- Zero error handling. There are no alerts when a run fails. The client only finds out when a customer complains.\n- Lack of modularity. Huge scenarios that are impossible to edit. If you change one node, the whole system misfires.\n- No documentation. No comments, no readme, no explanation of keys.\n\nWe need to stop treating business automation like a quick weekend hobby. If you are trusting your core operations to automated workflows, you need real software engineering principles.\n\n#automation #softwareengineering #dubaimarket`
    },
    {
      id: 3,
      type: 'carousel',
      date: '06/25/2026',
      time: '5:00 PM',
      caption: `Building automation tools that find hidden data. Here is the 5-step framework to extract leads from public city minutes.\n\n#buildinpublic #automation #softwareengineering`,
      assetPath: '/Users/apple/Documents/{{BRAND_SHORT_NAME}}-data/daily-linkedin-posts-pipeline/carousel-routine/output/2026-06-24/carousel-branded/linkedin-carousel-2026-06-24.pdf',
      title: 'AI City Minute Parser'
    },
    {
      id: 4,
      type: 'regular',
      date: '06/25/2026',
      time: '8:00 PM',
      caption: `The work that makes you money is rarely the work that makes you feel productive\n\nIt is easy to spend five hours optimizing your dashboard. Or tweaking CSS. Or reviewing new productivity software. At the end of the day, you feel like you did a lot.\n\nBut none of those hours brought in a single customer.\n\nThe most valuable work usually feels uncomfortable:\n- Following up on warm leads\n- Asking past clients for referrals\n- Pitching regional businesses\n- Doing direct outreach\n\nStop hiding behind easy setup tasks. Focus on the hard activities that grow the business.\n\n#productivity #entrepreneurship #solopreneur`
    }
  ];

  const screenshotDir = path.resolve(__dirname, 'slack_downloads');
  if (!fs.existsSync(screenshotDir)) {
    fs.mkdirSync(screenshotDir, { recursive: true });
  }

  try {
    console.log("Locating active devtools port dynamically...");
    const tmpDir = os.tmpdir();
    const dirs = fs.readdirSync(tmpDir).filter(name => name.startsWith('puppeteer_dev_chrome_profile-') || name.startsWith('agent-browser-chrome-'));
    if (dirs.length === 0) {
      throw new Error('No chrome directories found in tmp.');
    }
    const latestDir = dirs.map(name => {
      const fullPath = path.join(tmpDir, name);
      return { path: fullPath, mtime: fs.statSync(fullPath).mtimeMs };
    }).sort((a, b) => b.mtime - a.mtime)[0].path;
    const portFile = path.join(latestDir, 'DevToolsActivePort');
    const content = fs.readFileSync(portFile, 'utf8');
    const port = content.split('\n')[0].trim();
    console.log(`Connecting to browser on port ${port}...`);
    const browser = await puppeteer.connect({ browserURL: `http://127.0.0.1:${port}` });
    const pages = await browser.pages();
    const page = pages.find(p => p.url().includes('linkedin.com'));
    if (!page) {
      console.error("LinkedIn page not found! Make sure LinkedIn is open in the agent-browser.");
      process.exit(1);
    }
    await page.bringToFront();
    await page.setViewport({ width: 1280, height: 1200 });

    console.log(`\n${'='.repeat(60)}`);
    console.log(`SCHEDULING ALL ${posts.length} POSTS (4 per day, 3 days)`);
    console.log(`${'='.repeat(60)}\n`);

    for (const post of posts) {
      console.log(`\n${'='.repeat(50)}`);
      console.log(`Scheduling Post ${post.id}/${posts.length} (${post.type}): Date=${post.date}, Time=${post.time}`);
      console.log(`${'='.repeat(50)}`);
      const prefix = `${screenshotDir}/post_${post.id}_${post.type}`;

      // Navigate to feed for clean state
      console.log("Navigating to feed home page...");
      try {
        await page.goto('https://www.linkedin.com/feed/', { waitUntil: 'domcontentloaded', timeout: 15000 });
      } catch (err) {
        console.log("Navigation timeout/error, continuing:", err.message);
      }
      await new Promise(r => setTimeout(r, 4000));

      // Hide messaging overlays
      console.log("Hiding messaging overlays...");
      await page.evaluate(() => {
        const style = document.createElement('style');
        style.id = 'hide-msg-overlay-style-' + Date.now();
        style.innerHTML = `
          .msg-overlay-container, 
          [class*="msg-overlay"], 
          #msg-overlay { 
            display: none !important; 
          }
        `;
        document.head.appendChild(style);
      });

      // Close any open composers
      console.log("Checking and closing any open composers first...");
      await page.evaluate(() => {
        function findDismissBtn(root) {
          if (!root) return null;
          const btn = Array.from(root.querySelectorAll('button')).find(
            b => {
              const label = b.getAttribute('aria-label') || '';
              const txt = b.innerText || '';
              const cls = b.className || '';
              return label.includes('Dismiss') || 
                     txt.includes('Dismiss') ||
                     label.toLowerCase() === 'close' ||
                     cls.includes('close-button');
            }
          );
          if (btn) return btn;
          const walker = document.createTreeWalker(root, NodeFilter.SHOW_ELEMENT, null, false);
          let node;
          while (node = walker.nextNode()) {
            if (node.shadowRoot) {
              const found = findDismissBtn(node.shadowRoot);
              if (found) return found;
            }
          }
          return null;
        }
        const dismissBtn = findDismissBtn(document.body);
        if (dismissBtn) dismissBtn.click();
      });
      await new Promise(r => setTimeout(r, 2000));

      console.log("Clicking 'Start a post'...");
      const clickStartPost = await clickNativelyShadow(page, (root) => {
        return Array.from(root.querySelectorAll('*')).find(
          el => (el.tagName === 'BUTTON' || el.getAttribute('role') === 'button' || el.getAttribute('aria-label') === 'Start a post') &&
                el.innerText && el.innerText.trim().includes('Start a post')
        );
      });
      if (!clickStartPost) throw new Error("Could not find 'Start a post' button");

      const editorSelector = '.ql-editor, [contenteditable="true"]';
      await waitForSelectorShadow(page, editorSelector, 15000);
      await new Promise(r => setTimeout(r, 1000));

      // ========== HANDLE ATTACHMENTS ==========
      if (post.type === 'poll') {
        console.log("Handling Poll attachment...");
        await clickNativelyShadow(page, (root) => {
          return Array.from(root.querySelectorAll('button')).find(
            b => (b.ariaLabel && b.ariaLabel.includes('More')) || (b.innerText && b.innerText.includes('More'))
          );
        });
        await new Promise(r => setTimeout(r, 1500));

        const clickedPoll = await clickNativelyShadow(page, (root) => {
          return Array.from(root.querySelectorAll('button')).find(
            b => (b.ariaLabel && b.ariaLabel.includes('Create a poll')) || (b.innerText && b.innerText.includes('Create a poll'))
          );
        });
        if (!clickedPoll) throw new Error("Could not find 'Create a poll' button");
        await new Promise(r => setTimeout(r, 2000));

        // Fill question
        await waitForSelectorShadow(page, 'textarea.polls-detour__question-field, textarea[placeholder*="commute"], textarea[id*="question"]');
        const questionEl = await getElementShadow(page, 'textarea.polls-detour__question-field, textarea[placeholder*="commute"], textarea[id*="question"]');
        await questionEl.focus();
        await page.keyboard.type(post.title);
        await questionEl.dispose();
        console.log("Filled poll question.");

        const options = post.pollOptionsStr.split('|').map(o => o.trim());
        
        const getInputs = async () => {
          const inputsHandle = await page.evaluateHandle(() => {
            function findInputs(root) {
              let found = [];
              const els = root.querySelectorAll('input[id*="poll-option"]');
              for (const el of els) found.push(el);
              const walker = document.createTreeWalker(root, NodeFilter.SHOW_ELEMENT, null, false);
              let node;
              while (node = walker.nextNode()) {
                if (node.shadowRoot) found = found.concat(findInputs(node.shadowRoot));
              }
              return found;
            }
            return findInputs(document.body);
          });
          const properties = await inputsHandle.getProperties();
          const currentInputs = [];
          for (const property of properties.values()) {
            const el = property.asElement();
            if (el) currentInputs.push(el);
          }
          return currentInputs;
        };

        let optionInputs = await getInputs();
        if (optionInputs.length < 2) throw new Error("Option inputs not found");
        
        await optionInputs[0].focus();
        await page.keyboard.type(options[0]);
        await new Promise(r => setTimeout(r, 300));
        
        await optionInputs[1].focus();
        await page.keyboard.type(options[1]);
        await new Promise(r => setTimeout(r, 300));

        if (options[2]) {
          console.log("Adding third option...");
          await clickNativelyShadow(page, (root) => {
            return Array.from(root.querySelectorAll('button')).find(b => b.innerText && b.innerText.includes('Add option'));
          });
          await new Promise(r => setTimeout(r, 1000));
          
          optionInputs = await getInputs();
          if (optionInputs.length < 3) throw new Error("Option 3 input not found");
          await optionInputs[2].focus();
          await page.keyboard.type(options[2]);
          await new Promise(r => setTimeout(r, 300));
        }

        if (options[3]) {
          console.log("Adding fourth option...");
          await clickNativelyShadow(page, (root) => {
            return Array.from(root.querySelectorAll('button')).find(b => b.innerText && b.innerText.includes('Add option'));
          });
          await new Promise(r => setTimeout(r, 1000));
          
          optionInputs = await getInputs();
          if (optionInputs.length < 4) throw new Error("Option 4 input not found");
          await optionInputs[3].focus();
          await page.keyboard.type(options[3]);
          await new Promise(r => setTimeout(r, 300));
        }

        // Verify poll options
        console.log("Performing validation check on typed poll options...");
        const verifyVals = await page.evaluate(() => {
          function findInputs(root) {
            let found = [];
            const els = root.querySelectorAll('input[id*="poll-option"]');
            for (const el of els) found.push(el.value.trim());
            const walker = document.createTreeWalker(root, NodeFilter.SHOW_ELEMENT, null, false);
            let node;
            while (node = walker.nextNode()) {
              if (node.shadowRoot) found = found.concat(findInputs(node.shadowRoot));
            }
            return found;
          }
          return findInputs(document.body);
        });
        console.log("Values found in inputs:", verifyVals);
        if (verifyVals.some(v => v === "")) {
          throw new Error("Validation Failed: Some poll option inputs are blank in React state/DOM!");
        }

        await page.screenshot({ path: `${prefix}_filled.png` });

        // Click Done
        console.log("Clicking Done on Poll creator...");
        const clickedPollDone = await clickNativelyShadowRetry(page, (root) => {
          return Array.from(root.querySelectorAll('button')).find(b => {
            const txt = b.innerText ? b.innerText.trim() : '';
            const isVisible = b.offsetWidth > 0 || b.offsetHeight > 0 || window.getComputedStyle(b).display !== 'none';
            const isNotVideoJS = typeof b.className === 'string' && !b.className.includes('vjs-');
            const isDisabled = b.hasAttribute('disabled') || b.disabled || (typeof b.className === 'string' && b.className.includes('disabled'));
            return txt === 'Done' && isVisible && isNotVideoJS && !isDisabled;
          });
        });
        if (!clickedPollDone) throw new Error("Could not click Done on Poll creator");
        await new Promise(r => setTimeout(r, 2000));

      } else if (post.type === 'carousel') {
        console.log("Handling Carousel document upload...");
        let clickedDoc = await clickNativelyShadow(page, (root) => {
          const btns = Array.from(root.querySelectorAll('button'));
          return btns.find(b => b.ariaLabel && b.ariaLabel.includes('Add a document')) ||
                 btns.find(b => b.innerText && b.innerText.includes('Add a document')) ||
                 btns.find(b => b.innerText && b.innerText.includes('document'));
        });

        if (!clickedDoc) {
          await clickNativelyShadow(page, (root) => {
            return Array.from(root.querySelectorAll('button')).find(
              b => (b.ariaLabel && b.ariaLabel.includes('More')) || (b.innerText && b.innerText.includes('More'))
            );
          });
          await new Promise(r => setTimeout(r, 1500));
          clickedDoc = await clickNativelyShadow(page, (root) => {
            const btns = Array.from(root.querySelectorAll('button'));
            return btns.find(b => b.ariaLabel && b.ariaLabel.includes('Add a document')) ||
                   btns.find(b => b.innerText && b.innerText.includes('Add a document')) ||
                   btns.find(b => b.innerText && b.innerText.includes('document'));
          });
        }
        if (!clickedDoc) throw new Error("Could not find 'Add a document' button");
        await new Promise(r => setTimeout(r, 2000));

        const fileInputHandle = await page.evaluateHandle(() => {
          function findFileInput(root) {
            const walker = document.createTreeWalker(root, NodeFilter.SHOW_ELEMENT, null, false);
            let node;
            while (node = walker.nextNode()) {
              if (node.tagName === 'INPUT' && node.type === 'file') return node;
              if (node.shadowRoot) {
                const found = findFileInput(node.shadowRoot);
                if (found) return found;
              }
            }
            return null;
          }
          return findFileInput(document.body);
        });
        if (!fileInputHandle) throw new Error("Could not find file input in shadow DOM");
        const fileInput = fileInputHandle.asElement();
        await fileInput.uploadFile(post.assetPath);
        console.log("Document uploaded. Waiting 4s for processing...");
        await new Promise(r => setTimeout(r, 4000));

        // Title
        await waitForSelectorShadow(page, 'input.document-title-form__title-input, input[placeholder*="title to your document"]');
        const titleInput = await getElementShadow(page, 'input.document-title-form__title-input, input[placeholder*="title to your document"]');
        await titleInput.focus();
        await page.keyboard.type(post.title);
        await titleInput.dispose();
        console.log("Document title typed:", post.title);

        // Verify title
        const titleVal = await page.evaluate(() => {
          function findTitleInput(root) {
            const el = root.querySelector('input.document-title-form__title-input, input[placeholder*="title to your document"]');
            if (el) return el.value.trim();
            const walker = document.createTreeWalker(root, NodeFilter.SHOW_ELEMENT, null, false);
            let node;
            while (node = walker.nextNode()) {
              if (node.shadowRoot) {
                const val = findTitleInput(node.shadowRoot);
                if (val) return val;
              }
            }
            return null;
          }
          return findTitleInput(document.body);
        });
        console.log("Title value in DOM:", titleVal);
        if (!titleVal || titleVal === "") {
          throw new Error("Validation Failed: Document title input is blank!");
        }

        await page.screenshot({ path: `${prefix}_doc_uploaded.png` });

        // Click Done
        const clickedDocDone = await clickNativelyShadowRetry(page, (root) => {
          return Array.from(root.querySelectorAll('button')).find(b => {
            const txt = b.innerText ? b.innerText.trim() : '';
            const isVisible = b.offsetWidth > 0 || b.offsetHeight > 0 || window.getComputedStyle(b).display !== 'none';
            const isNotVideoJS = typeof b.className === 'string' && !b.className.includes('vjs-');
            const isDisabled = b.hasAttribute('disabled') || b.disabled || (typeof b.className === 'string' && b.className.includes('disabled'));
            return txt === 'Done' && isVisible && isNotVideoJS && !isDisabled;
          });
        });
        if (!clickedDocDone) throw new Error("Could not click Done on Document uploader");
        await new Promise(r => setTimeout(r, 3000));

      } else if (post.type === 'infographic') {
        console.log("Handling Infographic image upload...");
        const clickedMedia = await clickNativelyShadow(page, (root) => {
          const btns = Array.from(root.querySelectorAll('button'));
          return btns.find(b => b.ariaLabel && b.ariaLabel.includes('Add media')) ||
                 btns.find(b => b.innerText && b.innerText.includes('Add media')) ||
                 btns.find(b => b.innerText && b.innerText.includes('Photo')) ||
                 btns.find(b => b.ariaLabel && b.ariaLabel.includes('Photo'));
        });
        if (!clickedMedia) throw new Error("Could not find image upload button");
        await new Promise(r => setTimeout(r, 2000));

        const fileInputHandle = await page.evaluateHandle(() => {
          function findFileInput(root) {
            const walker = document.createTreeWalker(root, NodeFilter.SHOW_ELEMENT, null, false);
            let node;
            while (node = walker.nextNode()) {
              if (node.tagName === 'INPUT' && node.type === 'file') return node;
              if (node.shadowRoot) {
                const found = findFileInput(node.shadowRoot);
                if (found) return found;
              }
            }
            return null;
          }
          return findFileInput(document.body);
        });
        if (!fileInputHandle) throw new Error("Could not find file input in shadow DOM");
        const fileInput = fileInputHandle.asElement();
        await fileInput.uploadFile(post.assetPath);
        console.log("Image uploaded. Waiting 4s for processing...");
        await new Promise(r => setTimeout(r, 4000));

        await page.screenshot({ path: `${prefix}_image_uploaded.png` });

        // Click Next/Done in image editor
        const clickedImageNext = await clickNativelyShadowRetry(page, (root) => {
          return Array.from(root.querySelectorAll('button')).find(b => {
            const txt = b.innerText ? b.innerText.trim() : '';
            const isMatch = txt === 'Next' || txt === 'Done';
            const isVisible = b.offsetWidth > 0 || b.offsetHeight > 0 || window.getComputedStyle(b).display !== 'none';
            const isNotVideoJS = typeof b.className === 'string' && !b.className.includes('vjs-');
            const isDisabled = b.hasAttribute('disabled') || b.disabled || (typeof b.className === 'string' && b.className.includes('disabled'));
            return isMatch && isVisible && isNotVideoJS && !isDisabled;
          });
        });
        if (!clickedImageNext) throw new Error("Could not click Next/Done in image editor");
        await new Promise(r => setTimeout(r, 3000));
      }

      // ========== FILL CAPTION ==========
      console.log("Filling post caption text...");
      await waitForSelectorShadow(page, editorSelector, 15000);
      const editorEl = await getElementShadow(page, editorSelector);
      await editorEl.focus();

      // Clear contents
      await page.evaluate((el) => {
        el.focus();
        document.execCommand('selectAll', false, null);
        document.execCommand('delete', false, null);
      }, editorEl);
      await new Promise(r => setTimeout(r, 1000));

      // Type paragraph by paragraph
      const paragraphs = post.caption.split('\n');
      for (let i = 0; i < paragraphs.length; i++) {
        if (i > 0) {
          await page.keyboard.press('Enter');
          await new Promise(r => setTimeout(r, 150));
        }
        if (paragraphs[i]) {
          await page.keyboard.type(paragraphs[i]);
          await new Promise(r => setTimeout(r, 150));
        }
      }
      await new Promise(r => setTimeout(r, 2000));
      await editorEl.dispose();

      // Verify caption
      const editorText = await page.evaluate(() => {
        function findText(root) {
          const el = root.querySelector('.ql-editor');
          if (el) return el.innerText.trim();
          const walker = document.createTreeWalker(root, NodeFilter.SHOW_ELEMENT, null, false);
          let node;
          while (node = walker.nextNode()) {
            if (node.shadowRoot) {
              const txt = findText(node.shadowRoot);
              if (txt) return txt;
            }
          }
          return null;
        }
        return findText(document.body);
      });
      console.log("Caption text in editor (length):", editorText ? editorText.length : 0);
      if (!editorText || editorText.length < 5) {
        throw new Error("Validation Failed: Post caption in editor is blank or too short!");
      }

      await page.screenshot({ path: `${prefix}_draft_composer.png` });

      // ========== OPEN SCHEDULE MODAL ==========
      console.log("Opening Schedule Settings...");
      const clickedScheduleIcon = await clickNativelyShadow(page, (root) => {
        const modal = root.querySelector('.share-box, .artdeco-modal, [role="dialog"]');
        const container = modal || root;
        const buttons = Array.from(container.querySelectorAll('button'));
        const postBtn = buttons.find(b => b.innerText && b.innerText.trim() === 'Post');
        if (postBtn && postBtn.previousElementSibling) {
          return postBtn.previousElementSibling;
        }
        return buttons.find(b => b.ariaLabel && b.ariaLabel.includes('Schedule'));
      });
      if (!clickedScheduleIcon) throw new Error("Could not find or click Schedule post clock icon");
      await new Promise(r => setTimeout(r, 3000));

      // ========== SET DATE & TIME ==========
      console.log(`Setting schedule: Date=${post.date}, Time=${post.time}`);
      await fillFieldShadow(page, 'input[placeholder*="Date"], input[aria-label*="date"], input[id*="date"]', post.date);
      
      let normalizedTime = post.time;
      if (normalizedTime.startsWith('0')) {
        normalizedTime = normalizedTime.substring(1);
      }
      await fillTimeComboboxShadow(page, 'input[placeholder*="Time"], input[aria-label*="time"], input[id*="time"], input[role="combobox"]', normalizedTime);

      await page.screenshot({ path: `${prefix}_schedule_settings.png` });

      // Click Next
      console.log("Saving schedule settings (clicking Next)...");
      const clickedNext = await clickNativelyShadow(page, (root) => {
        return Array.from(root.querySelectorAll('button')).find(
          b => b.innerText && b.innerText.trim() === 'Next'
        );
      });
      if (!clickedNext) throw new Error("Could not click Next in schedule modal");
      await new Promise(r => setTimeout(r, 3000));

      await page.screenshot({ path: `${prefix}_final_draft.png` });

      // Click final Schedule
      console.log("Clicking final 'Schedule' button...");
      const clickedScheduleFinal = await clickNativelyShadow(page, (root) => {
        return Array.from(root.querySelectorAll('button')).find(
          b => b.innerText && b.innerText.trim() === 'Schedule'
        );
      });
      if (!clickedScheduleFinal) throw new Error("Could not find final 'Schedule' button in composer modal");
      
      console.log("Success! Waiting 6s for scheduling process to complete...");
      await new Promise(r => setTimeout(r, 6000));

      const isClosed = await page.evaluate(() => {
        function findEl(root, sel) {
          if (!root) return null;
          const el = root.querySelector(sel);
          if (el) return el;
          const walker = document.createTreeWalker(root, NodeFilter.SHOW_ELEMENT, null, false);
          let node;
          while (node = walker.nextNode()) {
            if (node.shadowRoot) {
              const found = findEl(node.shadowRoot, sel);
              if (found) return found;
            }
          }
          return null;
        }
        return !findEl(document.body, '.ql-editor');
      });
      if (!isClosed) throw new Error("composer editor did not close. Scheduling might have failed!");
      
      console.log(`✓ Successfully scheduled Post ${post.id}/${posts.length}!`);
    }

    console.log(`\n${'='.repeat(60)}`);
    console.log(`✓ ALL ${posts.length} POSTS HAVE BEEN SCHEDULED SUCCESSFULLY!`);
    console.log(`${'='.repeat(60)}`);
    console.log("\nSchedule Summary:");
    console.log("Day 1 (06/13): Carousel 9AM, Infographic 12PM, Collaborative Article 3PM, Poll 6PM");
    console.log("Day 2 (06/14): Tool Spotlight 9AM, Weekly Roundup 12PM, Plain English 3PM, Unfair Advantage 6PM");
    console.log("Day 3 (06/15): Career/Income 9AM, Hot Take 12PM, Steal This 3PM");
    process.exit(0);

  } catch (err) {
    console.error("Automator Exception:", err);
    try {
      const tmpDir = os.tmpdir();
      const dirs = fs.readdirSync(tmpDir).filter(name => name.startsWith('agent-browser-chrome-'));
      if (dirs.length > 0) {
        const latestDir = dirs.map(name => {
          const fullPath = path.join(tmpDir, name);
          return { path: fullPath, mtime: fs.statSync(fullPath).mtimeMs };
        }).sort((a, b) => b.mtime - a.mtime)[0].path;
        const portFile = path.join(latestDir, 'DevToolsActivePort');
        const content = fs.readFileSync(portFile, 'utf8');
        const port = content.split('\n')[0].trim();
        const errBrowser = await puppeteer.connect({ browserURL: `http://127.0.0.1:${port}` });
        const errPages = await errBrowser.pages();
        const errPage = errPages.find(p => p.url().includes('linkedin.com'));
        if (errPage) {
          await errPage.screenshot({ path: '/Users/apple/Documents/{{BRAND_SHORT_NAME}}-data/daily-linkedin-posts-pipeline/error_screenshot.png' });
          console.log("Saved error screenshot.");
        }
      }
    } catch (screenErr) {
      console.error("Failed to capture error screenshot:", screenErr);
    }
    process.exit(1);
  }
})();
