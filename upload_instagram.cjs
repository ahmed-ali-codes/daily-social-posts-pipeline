const puppeteer = require('puppeteer-core');
const fs = require('fs');
const path = require('path');
const os = require('os');

// IG Posts from generated content
const posts = [
  {
    id: 1,
    type: 'single',
    caption: `This one stat changes how Dubai businesses compete ⚡\n\nBusinesses that blog 11+ times a month get 3x more traffic 🤖\nMost UAE businesses are still doing this manually.\nThe ones that aren't? They're closing deals while their competitors are sleeping.\nAI automation isn't the future for Dubai's top SMBs. It's the present.\n\nFollow @{{BRAND_SHORT_NAME_LOWER}} for daily AI insights 👇\n\n#DubaiAI #UAEBusiness #AIAutomation #DubaiTech #GCCBusiness #WhatsAppAutomation #UAEStartups #DubaiFounders #{{BRAND_SHORT_NAME}}AI #BusinessAutomation`,
    images: [
      path.join(__dirname, 'instagram-image-1.png')
    ]
  },
  {
    id: 2,
    type: 'carousel',
    caption: `AI Email Automation myths that cost Dubai businesses real money 💸\nSwipe to see what's actually true in 2026.\nSave this before your competitor figures it out ⬇\n\n#DubaiAI #UAEBusiness #AIAutomation #DubaiTech #GCCStartups #{{BRAND_SHORT_NAME}}AI #BusinessGrowth #UAEFounders`,
    images: [
      path.join(__dirname, 'instagram-carousel-01.png'),
      path.join(__dirname, 'instagram-carousel-02.png'),
      path.join(__dirname, 'instagram-carousel-03.png'),
      path.join(__dirname, 'instagram-carousel-04.png'),
      path.join(__dirname, 'instagram-carousel-05.png')
    ]
  },
  {
    id: 3,
    type: 'single',
    caption: `The gap between you and your competitor is closing every day they automate and you don't. 🔥\nUAE businesses that move fast on AI are already seeing the results.\nBook a free audit — link in bio.\n\n#DubaiAI #UAEBusiness #AIAutomation #DubaiEntrepreneur #GCCBusiness #{{BRAND_SHORT_NAME}}AI #DubaiStartups #BusinessGrowthUAE #AIAgency #DigitalDubai`,
    images: [
      path.join(__dirname, 'instagram-image-3.png')
    ]
  }
];

async function sleep(ms) { return new Promise(r => setTimeout(r, ms)); }

async function findAndClickText(page, text) {
  const clicked = await page.evaluate((btnText) => {
    const btns = Array.from(document.querySelectorAll('div[role="button"], button'));
    const btn = btns.find(b => b.innerText && b.innerText.toLowerCase().includes(btnText.toLowerCase()));
    if (btn) {
      btn.click();
      return true;
    }
    return false;
  }, text);
  return clicked;
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
    let page = pages.find(p => p.url().includes('instagram.com'));
    if (!page) page = pages[0];
    await page.bringToFront();

    console.log("Navigating to Instagram home...");
    await page.goto('https://www.instagram.com/', { waitUntil: 'domcontentloaded', timeout: 15000 });
    await sleep(5000);
    console.log("Refreshing to clear any errors...");
    await page.reload({ waitUntil: 'domcontentloaded' });
    await sleep(5000);

    for (const post of posts) {
      console.log(`\\n==================================================`);
      console.log(`Drafting Instagram Post ${post.id}/${posts.length}`);
      console.log(`==================================================`);
      
      // Close any open modals first
      await page.keyboard.press('Escape');
      await sleep(1000);

      // Click "Create" on sidebar
      console.log("Clicking 'Create' button...");
      let createClicked = await page.evaluate(() => {
        const svgs = Array.from(document.querySelectorAll('svg[aria-label="New post"]'));
        if (svgs.length > 0) {
          const btn = svgs[0].closest('a') || svgs[0].closest('div[role="button"]') || svgs[0].closest('div');
          if (btn) { btn.click(); return true; }
        }
        return false;
      });
      if (!createClicked) {
        // Alternative method
        createClicked = await findAndClickText(page, 'Create');
      }
      
      if (!createClicked) {
        console.log("Could not find 'Create' button. Is Instagram loaded properly?");
        continue;
      }
      await sleep(3000);
      
      // Click "Post" if a menu pops up (New post vs Live vs Reel)
      await page.evaluate(() => {
        const items = Array.from(document.querySelectorAll('span'));
        const postItem = items.find(i => i.innerText === 'Post');
        if (postItem) {
          const btn = postItem.closest('div[role="button"]') || postItem.closest('a');
          if (btn) btn.click();
        }
      });
      await sleep(3000);

      // Upload Media
      console.log("Finding hidden file input...");
      const fileInput = await page.$('input[type="file"][accept*="image"]');
      if (fileInput) {
        console.log(`Uploading ${post.images.length} images...`);
        // Filter out non-existent files
        const validImages = post.images.filter(img => fs.existsSync(img));
        if (validImages.length === 0) {
          console.log("ERROR: No valid image files found for this post. Skipping.");
          await page.keyboard.press('Escape');
          await sleep(1000);
          continue;
        }
        await fileInput.uploadFile(...validImages);
        console.log("Images uploaded to DOM.");
      } else {
        console.log("Could not find file input. Skipping post.");
        continue;
      }
      
      console.log("Waiting for crop/edit UI to load...");
      await sleep(5000);

      // We are on "Crop" screen. Click Next
      console.log("Clicking Next (from Crop to Filter)...");
      await findAndClickText(page, 'Next');
      await sleep(3000);

      // We are on "Filter" screen. Click Next
      console.log("Clicking Next (from Filter to Caption)...");
      await findAndClickText(page, 'Next');
      await sleep(5000);

      // We are on "Caption" screen. Type caption.
      console.log("Typing caption...");
      let editor = await page.$('div[aria-label="Write a caption..."]');
      if (!editor) editor = await page.$('div[contenteditable="true"], textarea');
      
      if (editor) {
        await editor.click();
        await sleep(1000);
        for (const char of post.caption) {
          if (char === '\\n') {
            await page.keyboard.down('Shift');
            await page.keyboard.press('Enter');
            await page.keyboard.up('Shift');
          } else {
            await page.keyboard.type(char, { delay: 10 });
          }
        }
      } else {
        console.log("Warning: Could not find caption input.");
      }
      await sleep(2000);

      // Note: Scheduling natively on Instagram Web is very hit-or-miss depending on the account type.
      // To be safe, we will just open Advanced Settings and try to find Schedule. If not, we will leave it as a draft for the user to confirm.
      console.log("Looking for Advanced Settings to Schedule...");
      const advancedSettings = await findAndClickText(page, 'Advanced settings');
      if (advancedSettings) {
        await sleep(2000);
        const scheduleToggle = await page.evaluate(() => {
          const els = Array.from(document.querySelectorAll('span, div'));
          const schedText = els.find(e => e.innerText && e.innerText.includes('Schedule this post'));
          if (schedText) {
            const container = schedText.closest('div');
            const inputs = container ? Array.from(container.querySelectorAll('input')) : [];
            if (inputs.length > 0) {
              inputs[0].click();
              return true;
            }
          }
          return false;
        });
        
        if (scheduleToggle) {
          console.log("Toggled 'Schedule this post' on.");
          // Complex to set exact date in their custom calendar dropdown automatically via simple script.
          // Because IG uses a complex custom Date Picker.
          console.log("WARNING: Because Instagram's Web Date Picker is highly complex, the script will leave it open for you to verify.");
        } else {
          console.log("Schedule option not found. Your account might not support web scheduling, or it's hidden.");
        }
      }

      console.log(`\\n========================================================================`);
      console.log(`ATTENTION: Post ${post.id} is ready in the composer!`);
      console.log(`Please manually verify the schedule date (June 25, 2026) and click SHARE.`);
      console.log(`I will wait 45 seconds for you to click Share and let it upload...`);
      console.log(`========================================================================\\n`);
      
      // Pause for 45s to let user click Share
      await sleep(45000);
      
      // Dismiss any "Post Shared" modals
      await page.keyboard.press('Escape');
      await sleep(2000);
      await page.keyboard.press('Escape');
      await sleep(2000);
    }

    console.log(`\\n${'='.repeat(60)}`);
    console.log(`✓ INSTAGRAM POSTING SEQUENCE COMPLETE!`);
    console.log(`${'='.repeat(60)}\\n`);

    await browser.disconnect();
  } catch (err) {
    console.error("Scheduler failed:", err);
  }
})();
