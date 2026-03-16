const CDP = require('chrome-remote-interface');

const TWEET_TEXT = "Generated 200 social media posts using AI this month. Value: \u20AC8000 (market rate). Cost: \u20AC20 (ChatGPT). Margin: 99.75%. That's leverage. #AI #marketing";

async function waitFor(rt, selector, maxRetries = 15) {
  for (let i = 0; i < maxRetries; i++) {
    const res = await rt.evaluate({ expression: `!!document.querySelector('${selector}')` });
    if (res.result.value) return true;
    console.log(`Waiting for ${selector}... (${i+1}/${maxRetries})`);
    await new Promise(r => setTimeout(r, 2000));
  }
  return false;
}

(async () => {
  const client = await CDP({ port: 9222 });
  const { Target } = client;

  // Get list of targets to find an existing tab or create new
  const { targetId } = await Target.createTarget({ url: 'about:blank' });
  console.log('Target:', targetId);

  const newClient = await CDP({ port: 9222, target: targetId });
  const { Runtime: RT, Page: PG } = newClient;
  await PG.enable();

  // Navigate to compose
  await PG.navigate({ url: 'https://x.com/compose/post' });
  console.log('Navigating to compose...');

  // Wait for page load
  await new Promise(r => setTimeout(r, 5000));

  // Wait for the tweet textarea
  const found = await waitFor(RT, '[data-testid="tweetTextarea_0"]', 15);
  if (!found) {
    // Try alternative: contenteditable div
    console.log('Trying alternative selectors...');
    const altRes = await RT.evaluate({
      expression: `document.querySelector('[role="textbox"][contenteditable="true"]') ? 'found-textbox' : document.querySelector('.public-DraftEditor-content') ? 'found-draft' : 'not-found: ' + document.title`
    });
    console.log('Alt search:', altRes.result.value);
    
    if (altRes.result.value === 'not-found: ' + 'Log in to X') {
      console.log('ERROR: Not logged in!');
      await Target.closeTarget({ targetId });
      await newClient.close();
      await client.close();
      process.exit(1);
    }
  }

  await new Promise(r => setTimeout(r, 1000));

  // Try multiple approaches to insert text
  const insertResult = await RT.evaluate({
    expression: `
      (async () => {
        // Approach 1: tweetTextarea_0
        let el = document.querySelector('[data-testid="tweetTextarea_0"]');
        if (!el) {
          // Approach 2: contenteditable textbox
          el = document.querySelector('[role="textbox"][contenteditable="true"]');
        }
        if (!el) {
          // Approach 3: DraftEditor
          el = document.querySelector('.public-DraftEditor-content');
        }
        if (!el) {
          return 'no textarea found - page title: ' + document.title;
        }
        
        el.click();
        el.focus();
        await new Promise(r => setTimeout(r, 500));
        document.execCommand('insertText', false, ${JSON.stringify(TWEET_TEXT)});
        return 'text inserted via ' + (el.getAttribute('data-testid') || el.getAttribute('role') || el.className);
      })()
    `,
    awaitPromise: true
  });
  console.log('Insert result:', insertResult.result.value);

  if (insertResult.result.value.startsWith('no textarea')) {
    console.log('FAILED: Could not find textarea');
    await Target.closeTarget({ targetId });
    await newClient.close();
    await client.close();
    process.exit(1);
  }

  await new Promise(r => setTimeout(r, 2000));

  // Click tweet button
  const btnFound = await waitFor(RT, '[data-testid="tweetButton"]', 5);
  if (!btnFound) {
    console.log('Tweet button not found, trying alternatives...');
  }

  const btnResult = await RT.evaluate({
    expression: `
      (() => {
        const btn = document.querySelector('[data-testid="tweetButton"]');
        if (!btn) return 'button not found';
        btn.click();
        return 'clicked';
      })()
    `
  });
  console.log('Button result:', btnResult.result.value);

  await new Promise(r => setTimeout(r, 5000));

  await Target.closeTarget({ targetId });
  await newClient.close();
  await client.close();
  console.log('DONE');
})().catch(e => { console.error('ERROR:', e.message); process.exit(1); });
