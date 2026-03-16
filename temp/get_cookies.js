const CDP = require('chrome-remote-interface');

(async () => {
  const client = await CDP({ port: 9222 });
  const { Network } = client;
  
  const { cookies } = await Network.getCookies({ urls: ['https://x.com', 'https://twitter.com'] });
  
  const authToken = cookies.find(c => c.name === 'auth_token');
  const ct0 = cookies.find(c => c.name === 'ct0');
  
  if (authToken) console.log('AUTH_TOKEN=' + authToken.value);
  else console.log('AUTH_TOKEN=NOT_FOUND');
  
  if (ct0) console.log('CT0=' + ct0.value);
  else console.log('CT0=NOT_FOUND');
  
  await client.close();
})().catch(e => { console.error('ERROR:', e.message); process.exit(1); });
