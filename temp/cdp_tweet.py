"""Post a tweet via CDP WebSocket directly."""
import asyncio
import json
import sys
import websockets

CDP_WS = "ws://127.0.0.1:18800/devtools/page/8E54FD0600FD1CF9CBDAD6426A19F907"
TARGET_ID = "8E54FD0600FD1CF9CBDAD6426A19F907"

TWEET_TEXT = 'AI voice agents are crossing the "uncanny valley." They sound human. They pause. They laugh. Customer support is about to change forever. Are you ready? #voiceai #tech'

async def cdp_send(ws, method, params=None, mid=None):
    if mid is None:
        cdp_send.counter = getattr(cdp_send, 'counter', 0) + 1
        mid = cdp_send.counter
    msg = {"id": mid, "method": method}
    if params:
        msg["params"] = params
    await ws.send(json.dumps(msg))
    while True:
        resp = json.loads(await ws.recv())
        if resp.get("id") == mid:
            return resp
        # skip events

async def main():
    # First get the correct target - use the home page we opened
    import aiohttp
    async with aiohttp.ClientSession() as session:
        async with session.get("http://127.0.0.1:18800/json") as resp:
            pages = await resp.json()
    
    target = None
    for p in pages:
        if p.get("type") == "page" and "x.com" in p.get("url", ""):
            target = p
            break
    
    if not target:
        print("ERROR: No x.com tab found")
        sys.exit(1)
    
    ws_url = target["webSocketDebuggerUrl"]
    print(f"Connecting to: {ws_url}")
    
    async with websockets.connect(ws_url, max_size=50*1024*1024) as ws:
        # Navigate to compose
        print("Navigating to compose/post...")
        result = await cdp_send(ws, "Page.navigate", {"url": "https://x.com/compose/post"})
        print(f"Navigate result: {result}")
        
        await asyncio.sleep(3)
        
        # Check if compose loaded
        result = await cdp_send(ws, "Runtime.evaluate", {
            "expression": "document.title + ' | ' + window.location.href"
        })
        print(f"Page: {result.get('result', {}).get('result', {}).get('value', 'unknown')}")
        
        # Click on textarea
        result = await cdp_send(ws, "Runtime.evaluate", {
            "expression": """
                (function() {
                    const el = document.querySelector('[data-testid="tweetTextarea_0"]');
                    if (!el) return 'NO_TEXTAREA';
                    el.click();
                    el.focus();
                    return 'CLICKED';
                })()
            """
        })
        print(f"Click textarea: {result.get('result', {}).get('result', {}).get('value', 'unknown')}")
        
        await asyncio.sleep(1)
        
        # Find the contenteditable div and focus it
        result = await cdp_send(ws, "Runtime.evaluate", {
            "expression": """
                (function() {
                    const el = document.querySelector('[data-testid="tweetTextarea_0"] [contenteditable="true"]');
                    if (!el) {
                        // Try the div directly
                        const div = document.querySelector('.public-DraftEditor-content, [contenteditable="true"][role="textbox"]');
                        if (!div) return 'NO_EDITABLE';
                        div.focus();
                        return 'FOCUSED_ALT';
                    }
                    el.focus();
                    return 'FOCUSED';
                })()
            """
        })
        print(f"Focus: {result.get('result', {}).get('result', {}).get('value', 'unknown')}")
        
        await asyncio.sleep(0.5)
        
        # Insert text using execCommand
        escaped_text = TWEET_TEXT.replace("\\", "\\\\").replace("'", "\\'").replace('"', '\\"').replace('\n', '\\n')
        result = await cdp_send(ws, "Runtime.evaluate", {
            "expression": f"""
                (function() {{
                    const text = "{escaped_text}";
                    const result = document.execCommand('insertText', false, text);
                    return result ? 'INSERTED' : 'FAILED';
                }})()
            """
        })
        print(f"Insert text: {result.get('result', {}).get('result', {}).get('value', 'unknown')}")
        
        await asyncio.sleep(1)
        
        # Verify text was inserted
        result = await cdp_send(ws, "Runtime.evaluate", {
            "expression": """
                (function() {
                    const el = document.querySelector('[data-testid="tweetTextarea_0"]');
                    return el ? el.textContent : 'NO_ELEMENT';
                })()
            """
        })
        print(f"Textarea content: {result.get('result', {}).get('result', {}).get('value', 'unknown')}")
        
        # Click tweet button
        result = await cdp_send(ws, "Runtime.evaluate", {
            "expression": """
                (function() {
                    const btn = document.querySelector('[data-testid="tweetButton"]');
                    if (!btn) return 'NO_BUTTON';
                    btn.click();
                    return 'CLICKED';
                })()
            """
        })
        print(f"Click tweet button: {result.get('result', {}).get('result', {}).get('value', 'unknown')}")
        
        await asyncio.sleep(3)
        
        # Check final URL
        result = await cdp_send(ws, "Runtime.evaluate", {
            "expression": "window.location.href"
        })
        print(f"Final URL: {result.get('result', {}).get('result', {}).get('value', 'unknown')}")
        
        print("DONE")

if __name__ == "__main__":
    asyncio.run(main())
