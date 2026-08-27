const puppeteer = require('puppeteer-core');
const fs = require('fs');
const path = require('path');
const os = require('os');
const cp = require('child_process');

async function sleep(ms) { return new Promise(r => setTimeout(r, ms)); }

(async () => {
  console.log('Launching Google Chrome...');
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

  const pages = await browser.pages();
  const page = pages[0];

  try {
    console.log('Navigating to LinkedIn login page...');
    await page.goto('https://www.linkedin.com/login', { waitUntil: 'networkidle2', timeout: 30000 });
    await sleep(3000);

    // Take screenshot
    await page.screenshot({ path: path.resolve(__dirname, 'login_debug.png') });
    console.log('Saved page screenshot to login_debug.png');

    const url = page.url();
    if (url.includes('/feed') || url.includes('/company/')) {
      console.log('Already logged in!');
    } else {
      console.log('Entering username/email...');
      const usernameSelectors = ['#username', 'input[name="session_key"]', 'input[autocomplete="username"]', 'input[type="text"]'];
      let usernameField = null;
      for (const sel of usernameSelectors) {
        try {
          await page.waitForSelector(sel, { timeout: 3000 });
          usernameField = sel;
          break;
        } catch (e) {}
      }

      if (usernameField) {
        await page.type(usernameField, 'ahmed97028@gmail.com', { delay: 50 });
        await sleep(500);

        const passwordSelectors = ['#password', 'input[name="session_password"]', 'input[autocomplete="current-password"]', 'input[type="password"]'];
        let passwordField = null;
        for (const sel of passwordSelectors) {
          try {
            await page.waitForSelector(sel, { timeout: 3000 });
            passwordField = sel;
            break;
          } catch (e) {}
        }

        if (passwordField) {
          await page.type(passwordField, 'ahmedmughal4594', { delay: 50 });
          await sleep(500);
        }

        console.log('Clicking Sign in...');
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
      } else {
        console.log('Could not find username field. Might be already logged in or showing alternative page.');
      }
    }

    // Wait for the user to complete challenge / login if it is not finished
    console.log('Verifying login status...');
    const startTime = Date.now();
    const timeoutMs = 120000; // 2 minutes
    let loggedIn = false;

    while (Date.now() - startTime < timeoutMs) {
      const currentUrl = page.url();
      console.log(`Current URL: ${currentUrl}`);
      
      // Save debug screenshot to see if there is a CAPTCHA or 2FA
      await page.screenshot({ path: path.resolve(__dirname, 'login_debug.png') });

      if (currentUrl.includes('/feed') || currentUrl.includes('/company/') || currentUrl.includes('/mynetwork/')) {
        loggedIn = true;
        break;
      }

      if (currentUrl.includes('challenge') || currentUrl.includes('checkpoint')) {
        console.log('\n⚠️  LinkedIn is showing a security challenge (CAPTCHA or 2FA verification code).');
        console.log('Please solve the challenge in the opened Chrome browser window.');
      } else if (currentUrl.includes('login')) {
        console.log('Still on login page. If login failed, please enter details manually in the browser.');
      }

      console.log(`Waiting for authentication... (${Math.round((timeoutMs - (Date.now() - startTime)) / 1000)}s remaining)`);
      await sleep(5000);
    }

    if (!loggedIn) {
      throw new Error('Authentication timeout. Could not log in to LinkedIn.');
    }

    console.log('Authentication successful! Proceeding to run pipeline...');
    
    // Now we run bash run_pipeline.sh as a child process
    console.log('\n======================================================');
    console.log('RUNNING BASH PIPELINE SCRIPT');
    console.log('======================================================\n');
    
    // We execute the pipeline synchronously so we capture output and hold the browser open
    cp.execSync('bash run_pipeline.sh', { stdio: 'inherit' });
    
    console.log('\n======================================================');
    console.log('✓ PIPELINE COMPLETED SUCCESSFULLY!');
    console.log('======================================================\n');

  } catch (error) {
    console.error('\n❌ Error occurred:', error.message);
    try {
      await page.screenshot({ path: path.resolve(__dirname, 'error_debug.png') });
      console.log('Saved error screenshot to error_debug.png');
    } catch (_) {}
  } finally {
    console.log('Closing browser...');
    await browser.close();
  }
})();
