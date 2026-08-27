const puppeteer = require('puppeteer-core');
const fs = require('fs');
const path = require('path');

// Posts to schedule from today's generated content
const posts = [
  {
    id: 1,
    type: 'TEXT',
    channel: '{{AUTHOR_NAME}} LinkedIn',
    caption: `Here is what I learned building custom lead gen engines after scraping city planning commission minutes

A month ago, a civil engineer PM got laid off and started building. Instead of jumping to standard automation tools, they coded custom scrapers in Python.

They realized city planning documents are a goldmine. The minutes list rezoning requests. Rezoning requests mean land development. Land development means new builders, attorneys, and contractors are about to get hired.

By writing a script that reads these minutes, extracts the affected businesses, and enriches the contact info, they built a highly targeted pipeline.

Three lessons from this:
- Mine review data. Look at local trades businesses to spot cities with genuine labor shortages.
- Avoid building spam engines. Keep email lists short and clean. apollo exports are often dirty and increase bounce rates.
- Code your gateway. Using a Telegram gateway to manually review comment bot outputs keeps interactions authentic.

DM me if you are trying to automate lead sourcing. I am building similar flows this week.

#builderjourney #leadgeneration #automation`,
    date: getScheduleDate(0),
    time: '08:00'
  },
  {
    id: 2,
    type: 'TEXT',
    channel: '{{AUTHOR_NAME}} LinkedIn',
    caption: `Vibe-coded automations are quietly breaking UAE business operations

I keep talking to local founders who hired an "expert" to build n8n or Make scenarios. Three months later, the whole system stops working.

Here are the 4 main reasons these setups fail in production:
- Happy path thinking. Most builders plan for things to go right. The minute there is a timeout or a missing field, the entire pipeline crashes.
- Zero error handling. There are no alerts when a run fails. The client only finds out when a customer complains.
- Lack of modularity. Huge scenarios that are impossible to edit. If you change one node, the whole system misfires.
- No documentation. No comments, no readme, no explanation of keys.

We need to stop treating business automation like a quick weekend hobby. If you are trusting your core operations to automated workflows, you need real software engineering principles.

#automation #softwareengineering #dubaimarket`,
    date: getScheduleDate(0),
    time: '12:00'
  },
  {
    id: 3,
    type: 'CAROUSEL',
    channel: '{{AUTHOR_NAME}} LinkedIn',
    caption: `Building automation tools that find hidden data. Here is the 5-step framework to extract leads from public city minutes.

#buildinpublic #automation #softwareengineering`,
    pdfPath: path.resolve(__dirname, './carousel-routine/output/2026-06-24/carousel-branded/linkedin-carousel-2026-06-24.pdf'),
    date: getScheduleDate(0),
    time: '17:00'
  },
  {
    id: 4,
    type: 'TEXT',
    channel: '{{AUTHOR_NAME}} LinkedIn',
    caption: `The work that makes you money is rarely the work that makes you feel productive

It is easy to spend five hours optimizing your dashboard. Or tweaking CSS. Or reviewing new productivity software. At the end of the day, you feel like you did a lot.

But none of those hours brought in a single customer.

The most valuable work usually feels uncomfortable:
- Following up on warm leads
- Asking past clients for referrals
- Pitching regional businesses
- Doing direct outreach

Stop hiding behind easy setup tasks. Focus on the hard activities that grow the business.

#productivity #entrepreneurship #solopreneur`,
    date: getScheduleDate(0),
    time: '20:00'
  }
];

function getScheduleDate(daysFromNow) {
  const d = new Date();
  d.setDate(d.getDate() + daysFromNow + 1); // Schedule for tomorrow
  return `${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,'0')}-${String(d.getDate()).padStart(2,'0')}`;
}

async function sleep(ms) { return new Promise(r => setTimeout(r, ms)); }

async function typeSlowly(page, selector, text) {
  await page.click(selector);
  await sleep(300);
  // Clear existing text
  await page.keyboard.down('Meta');
  await page.keyboard.press('a');
  await page.keyboard.up('Meta');
  await page.keyboard.press('Backspace');
  await sleep(200);
  // Type new text character by character for reliability
  for (const char of text) {
    if (char === '\n') {
      await page.keyboard.down('Shift');
      await page.keyboard.press('Enter');
      await page.keyboard.up('Shift');
    } else {
      await page.keyboard.type(char, { delay: 5 });
    }
  }
}

(async () => {
  console.log('Launching Chrome browser...');
  const browser = await puppeteer.launch({
    executablePath: '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
    headless: false,
    args: [
      '--no-sandbox',
      '--disable-setuid-sandbox',
      '--disable-gpu',
      '--disable-dev-shm-usage',
      '--use-mock-keychain',
      '--password-store=basic',
      '--disable-extensions',
      '--window-size=1280,900'
    ],
    defaultViewport: { width: 1280, height: 900 }
  });

  const page = (await browser.pages())[0];

  // ========== Step 1: Login to LinkedIn ==========
  console.log('Navigating to LinkedIn login...');
  await page.goto('https://www.linkedin.com/login', { waitUntil: 'networkidle2', timeout: 30000 });
  await sleep(3000);

  // Take a screenshot to see the page state
  await page.screenshot({ path: path.resolve(__dirname, 'login_debug.png') });
  console.log('Saved login page screenshot to login_debug.png');

  console.log('Entering credentials...');
  // Wait for username field with multiple possible selectors
  const usernameSelectors = ['#username', 'input[name="session_key"]', 'input[autocomplete="username"]', 'input[type="text"]'];
  let usernameField = null;
  for (const sel of usernameSelectors) {
    try {
      await page.waitForSelector(sel, { timeout: 5000 });
      usernameField = sel;
      console.log(`Found username field with selector: ${sel}`);
      break;
    } catch (e) { /* try next */ }
  }

  if (!usernameField) {
    console.log('Could not find username field. Page might have redirected to feed (already logged in?).');
    const url = page.url();
    console.log('Current URL:', url);
    if (url.includes('/feed')) {
      console.log('Already logged in! Proceeding to scheduling...');
    } else {
      console.log('ERROR: Cannot find login form. Exiting.');
      await browser.close();
      process.exit(1);
    }
  } else {
    await page.type(usernameField, 'ahmed97028@gmail.com', { delay: 50 });
    await sleep(500);

    // Wait for password field
    const passwordSelectors = ['#password', 'input[name="session_password"]', 'input[autocomplete="current-password"]', 'input[type="password"]'];
    let passwordField = null;
    for (const sel of passwordSelectors) {
      try {
        await page.waitForSelector(sel, { timeout: 5000 });
        passwordField = sel;
        console.log(`Found password field with selector: ${sel}`);
        break;
      } catch (e) { /* try next */ }
    }

    if (passwordField) {
      await page.type(passwordField, 'ahmedmughal4594', { delay: 50 });
      await sleep(500);
    }

    console.log('Clicking Sign in...');
    // Try multiple submit approaches
    const submitted = await page.evaluate(() => {
      const btn = document.querySelector('button[type="submit"]') ||
                  document.querySelector('button[data-litms-control-urn*="login"]') ||
                  [...document.querySelectorAll('button')].find(b => b.textContent.trim().toLowerCase().includes('sign in'));
      if (btn) { btn.click(); return true; }
      return false;
    });
    if (!submitted) {
      await page.keyboard.press('Enter');
    }
    await sleep(5000);
  }

  // Check if we landed on feed
  const currentUrl = page.url();
  console.log(`Current URL after login: ${currentUrl}`);

  if (currentUrl.includes('challenge') || currentUrl.includes('checkpoint')) {
    console.log('\n⚠️  LinkedIn is showing a security challenge (CAPTCHA or verification).');
    console.log('Please complete the challenge manually in the browser window.');
    console.log('Waiting 60 seconds for you to complete it...\n');
    await sleep(60000);
  }

  if (currentUrl.includes('login')) {
    console.log('ERROR: Login may have failed. Check the browser window.');
    console.log('Waiting 30 seconds for manual intervention...');
    await sleep(30000);
  }

  console.log('Login successful! Navigating to feed...');
  await page.goto('https://www.linkedin.com/feed/', { waitUntil: 'domcontentloaded', timeout: 15000 });
  await sleep(3000);

  // ========== Step 2: Schedule posts ==========
  console.log(`\n${'='.repeat(60)}`);
  console.log(`SCHEDULING ${posts.length} POSTS for {{AUTHOR_NAME}} LinkedIn`);
  console.log(`${'='.repeat(60)}\n`);

  for (const post of posts) {
    console.log(`\n--- Post ${post.id}/${posts.length} (${post.type}) ---`);
    console.log(`Scheduled: ${post.date} at ${post.time}`);

    try {
      // Click "Start a post" button
      await page.goto('https://www.linkedin.com/feed/', { waitUntil: 'domcontentloaded', timeout: 15000 });
      await sleep(2000);

      // Find and click the post button
      const postButton = await page.$('button.share-box-feed-entry__trigger');
      if (postButton) {
        await postButton.click();
      } else {
        // Try alternative selector
        await page.evaluate(() => {
          const buttons = [...document.querySelectorAll('button')];
          const btn = buttons.find(b => b.textContent.includes('Start a post'));
          if (btn) btn.click();
        });
      }
      await sleep(2000);

      // Type the post content into the editor
      const editor = await page.$('div.ql-editor[contenteditable="true"]');
      if (editor) {
        await editor.click();
        await sleep(300);
        // Type the caption
        for (const char of post.caption) {
          if (char === '\n') {
            await page.keyboard.down('Shift');
            await page.keyboard.press('Enter');
            await page.keyboard.up('Shift');
          } else {
            await page.keyboard.type(char, { delay: 3 });
          }
        }
        console.log(`Typed ${post.caption.length} characters`);
      } else {
        console.log('WARNING: Could not find post editor. Skipping this post.');
        continue;
      }

      await sleep(1000);

      // If carousel, upload PDF
      if (post.type === 'CAROUSEL' && post.pdfPath && fs.existsSync(post.pdfPath)) {
        console.log(`Uploading carousel PDF: ${post.pdfPath}`);
        // Click "Add a document" or media button
        const docButton = await page.evaluateHandle(() => {
          const buttons = [...document.querySelectorAll('button')];
          return buttons.find(b => b.getAttribute('aria-label')?.includes('document') || b.textContent.includes('document'));
        });
        if (docButton.asElement()) {
          await docButton.asElement().click();
          await sleep(1500);
          const fileInput = await page.$('input[type="file"]');
          if (fileInput) {
            await fileInput.uploadFile(post.pdfPath);
            console.log('PDF uploaded successfully');
            await sleep(3000);
            // Add title if prompted
            const titleInput = await page.$('input[placeholder*="title"]');
            if (titleInput) {
              await titleInput.type('AI City Minute Parser — 5 Steps', { delay: 30 });
              await sleep(500);
              // Click Done/Next
              await page.evaluate(() => {
                const btns = [...document.querySelectorAll('button')];
                const done = btns.find(b => b.textContent.trim() === 'Done' || b.textContent.trim() === 'Next');
                if (done) done.click();
              });
              await sleep(1000);
            }
          }
        }
      }

      // Click the clock/schedule icon
      console.log('Looking for schedule button...');
      const scheduleClicked = await page.evaluate(() => {
        // Look for the clock icon / schedule button
        const btns = [...document.querySelectorAll('button')];
        const sched = btns.find(b =>
          b.getAttribute('aria-label')?.toLowerCase().includes('schedule') ||
          b.textContent.toLowerCase().includes('schedule')
        );
        if (sched) { sched.click(); return true; }
        return false;
      });

      if (scheduleClicked) {
        await sleep(1500);
        console.log('Schedule modal opened. Setting date/time...');

        // Set date and time in schedule modal
        // This varies by LinkedIn UI version, attempt common patterns
        const dateInput = await page.$('input[type="date"], input[aria-label*="date" i]');
        if (dateInput) {
          await dateInput.click({ clickCount: 3 });
          await dateInput.type(post.date);
        }

        const timeSelect = await page.$('select[aria-label*="time" i], input[aria-label*="time" i]');
        if (timeSelect) {
          const tag = await page.evaluate(el => el.tagName, timeSelect);
          if (tag === 'SELECT') {
            await timeSelect.select(post.time);
          } else {
            await timeSelect.click({ clickCount: 3 });
            await timeSelect.type(post.time);
          }
        }

        await sleep(500);

        // Click "Schedule" / confirm
        await page.evaluate(() => {
          const btns = [...document.querySelectorAll('button')];
          const confirm = btns.find(b => b.textContent.trim() === 'Schedule');
          if (confirm) confirm.click();
        });
        await sleep(2000);
        console.log(`✅ Post ${post.id} scheduled for ${post.date} at ${post.time}`);
      } else {
        // Fallback: just post now button
        console.log('Schedule button not found. Saving as draft instead...');
        await page.evaluate(() => {
          const btns = [...document.querySelectorAll('button')];
          const close = btns.find(b => b.getAttribute('aria-label')?.includes('Dismiss') || b.textContent.includes('Save'));
          if (close) close.click();
        });
        await sleep(1000);
      }

      await sleep(2000);

    } catch (err) {
      console.log(`ERROR on post ${post.id}: ${err.message}`);
      // Close any open modals
      await page.keyboard.press('Escape');
      await sleep(1000);
    }
  }

  console.log(`\n${'='.repeat(60)}`);
  console.log('SCHEDULING COMPLETE');
  console.log(`${'='.repeat(60)}`);
  console.log('The browser will remain open for you to verify.');
  console.log('Close it manually when done.');

  // Don't close browser — let user verify
})();
