const CDP = require('chrome-remote-interface');

(async () => {
  const client = await CDP({ port: 9222 });
  const { Target, Network } = client;

  // Create a tab, navigate to x.com to load cookies
  const { targetId } = await Target.createTarget({ url: 'https://x.com' });
  console.log('Opening x.com...');
  
  await new Promise(r => setTimeout(r, 8000));

  // Now get cookies from the browser
  const { cookies } = await Network.getCookies({ urls: ['https://x.com', 'https://twitter.com', 'https://api.x.com'] });
  
  console.log('Total cookies found:', cookies.length);
  
  const authToken = cookies.find(c => c.name === 'auth_token');
  const ct0 = cookies.find(c => c.name === 'ct0');
  
  if (authToken) console.log('AUTH_TOKEN=' + authToken.value);
  else console.log('AUTH_TOKEN=NOT_FOUND');
  
  if (ct0) console.log('CT0=' + ct0.value);
  else console.log('CT0=NOT_FOUND');

  // Check page title
  const tabClient = await CDP({ port: 9222, target: targetId });
  const titleRes = await tabClient.Runtime.evaluate({ expression: 'document.title' });
  console.log('Page title:', titleRes.result.value);

  await Target.closeTarget({ targetId });
  await tabClient.close();
  await client.close();
})().catch(e => { console.error('ERROR:', e.message); process.exit(1); });
