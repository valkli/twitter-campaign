const { chromium } = require('playwright');
(async () => {
  const browser = await chromium.connectOverCDP('http://localhost:9222');
  const contexts = browser.contexts();
  const context = contexts[0];
  const page = await context.newPage();
  await page.goto('https://x.com/compose/post');
  await page.waitForTimeout(3000);

  const editable = page.locator('[contenteditable="true"][role="textbox"]').first();
  await editable.click();
  await page.waitForTimeout(500);

  const text = "Generated 200 social media posts using AI this month. Value: \u20AC8000 (market rate). Cost: \u20AC20 (ChatGPT). Margin: 99.75%. That's leverage. #AI #marketing";
  await page.evaluate((t) => document.execCommand('insertText', false, t), text);
  await page.waitForTimeout(1500);

  await page.evaluate(() => document.querySelector('[data-testid="tweetButton"]').click());
  await page.waitForTimeout(4000);

  console.log('TWEET_POSTED_OK');
  await page.close();
  await browser.close();
})().catch(e => { console.error('ERROR:', e.message); process.exit(1); });
