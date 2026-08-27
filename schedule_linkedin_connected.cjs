const puppeteer = require('puppeteer-core');
const fs = require('fs');
const path = require('path');

// Posts to schedule from today's generated content
const posts = [
  {
    id: 1,
    type: 'TEXT',
    channel: '{{AUTHOR_NAME}} LinkedIn',
    caption: `Here is what I learned building custom lead gen engines after scraping city planning commission minutes\n\nA month ago, a civil engineer PM got laid off and started building. Instead of jumping to standard automation tools, they coded custom scrapers in Python.\n\nThey realized city planning documents are a goldmine. The minutes list rezoning requests. Rezoning requests mean land development. Land development means new builders, attorneys, and contractors are about to get hired.\n\nBy writing a script that reads these minutes, extracts the affected businesses, and enriches the contact info, they built a highly targeted pipeline.\n\nThree lessons from this:\n- Mine review data. Look at local trades businesses to spot cities with genuine labor shortages.\n- Avoid building spam engines. Keep email lists short and clean. apollo exports are often dirty and increase bounce rates.\n- Code your gateway. Using a Telegram gateway to manually review comment bot outputs keeps interactions authentic.\n\nDM me if you are trying to automate lead sourcing. I am building similar flows this week.\n\n#builderjourney #leadgeneration #automation`,
    date: getScheduleDate(0),
    time: '08:00'
  },
  {
    id: 2,
    type: 'TEXT',
    channel: '{{AUTHOR_NAME}} LinkedIn',
    caption: `Vibe-coded automations are quietly breaking UAE business operations\n\nI keep talking to local founders who hired an "expert" to build n8n or Make scenarios. Three months later, the whole system stops working.\n\nHere are the 4 main reasons these setups fail in production:\n- Happy path thinking. Most builders plan for things to go right. The minute there is a timeout or a missing field, the entire pipeline crashes.\n- Zero error handling. There are no alerts when a run fails. The client only finds out when a customer complains.\n- Lack of modularity. Huge scenarios that are impossible to edit. If you change one node, the whole system misfires.\n- No documentation. No comments, no readme, no explanation of keys.\n\nWe need to stop treating business automation like a quick weekend hobby. If you are trusting your core operations to automated workflows, you need real software engineering principles.\n\n#automation #softwareengineering #dubaimarket`,
    date: getScheduleDate(0),
    time: '12:00'
  },
  {
    id: 3,
    type: 'CAROUSEL',
    channel: '{{AUTHOR_NAME}} LinkedIn',
    caption: `Building automation tools that find hidden data. Here is the 5-step framework to extract leads from public city minutes.\n\n#buildinpublic #automation #softwareengineering`,
    pdfPath: path.resolve(__dirname, './carousel-routine/output/2026-06-24/carousel-branded/linkedin-carousel-2026-06-24.pdf'),
    date: getScheduleDate(0),
    time: '17:00'
  },
  {
    id: 4,
    type: 'TEXT',
    channel: '{{AUTHOR_NAME}} LinkedIn',
    caption: `The work that makes you money is rarely the work that makes you feel productive\n\nIt is easy to spend five hours optimizing your dashboard. Or tweaking CSS. Or reviewing new productivity software. At the end of the day, you feel like you did a lot.\n\nBut none of those hours brought in a single customer.\n\nThe most valuable work usually feels uncomfortable:\n- Following up on warm leads\n- Asking past clients for referrals\n- Pitching regional businesses\n- Doing direct outreach\n\nStop hiding behind easy setup tasks. Focus on the hard activities that grow the business.\n\n#productivity #entrepreneurship #solopreneur`,
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

(async () => {
  const port = 56472; // Dynamically injected based on DevToolsActivePort
  console.log(`Connecting to existing browser on port ${port}...`);
  let browser;
  try {
    browser = await puppeteer.connect({ browserURL: `http://127.0.0.1:${port}` });
  } catch (err) {
    console.error("Failed to connect to the browser. Make sure it's still running.");
    process.exit(1);
  }

  const pages = await browser.pages();
  // Find a linkedin page or use the first page
  let page = pages.find(p => p.url().includes('linkedin.com'));
  if (!page) {
    page = pages[0];
  }
  await page.bringToFront();

  // Ensure we are on the feed
  console.log('Navigating to feed...');
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
      await page.goto('https://www.linkedin.com/feed/', { waitUntil: 'domcontentloaded', timeout: 15000 });
      await sleep(2000);

      // Click "Start a post" button
      const postButton = await page.$('button.share-box-feed-entry__trigger');
      if (postButton) {
        await postButton.click();
      } else {
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
        // Clean out existing content just in case
        await page.keyboard.down('Meta');
        await page.keyboard.press('a');
        await page.keyboard.up('Meta');
        await page.keyboard.press('Backspace');
        await sleep(200);

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
            const titleInput = await page.$('input[placeholder*="title"]');
            if (titleInput) {
              await titleInput.type('AI City Minute Parser — 5 Steps', { delay: 30 });
              await sleep(500);
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

        await page.evaluate(() => {
          const btns = [...document.querySelectorAll('button')];
          const confirm = btns.find(b => b.textContent.trim() === 'Schedule' || b.textContent.trim() === 'Next');
          if (confirm) confirm.click();
        });
        await sleep(2000);
        console.log(`✅ Post ${post.id} scheduled for ${post.date} at ${post.time}`);
      } else {
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
      await page.keyboard.press('Escape');
      await sleep(1000);
    }
  }

  console.log(`\n${'='.repeat(60)}`);
  console.log('SCHEDULING COMPLETE');
  console.log(`${'='.repeat(60)}`);
  
  await browser.disconnect();
})();
