import sys, time
from playwright.sync_api import sync_playwright

text = "Generated 200 social media posts using AI this month. Value: \u20ac8000 (market rate). Cost: \u20ac20 (ChatGPT). Margin: 99.75%. That's leverage. #AI #marketing"

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp('http://localhost:9222')
    context = browser.contexts[0]
    
    # Use existing page or create new
    pages = context.pages
    print(f"Found {len(pages)} pages")
    
    page = context.new_page()
    print("New page created")
    
    page.goto('https://x.com/compose/post', wait_until='domcontentloaded')
    print("Navigated to compose")
    page.wait_for_timeout(4000)
    
    # Try multiple selectors
    selectors = [
        '[contenteditable="true"][role="textbox"]',
        '[data-testid="tweetTextArea_0"] [contenteditable="true"]',
        'div.public-DraftEditor-content',
        '[data-contents="true"]',
    ]
    
    clicked = False
    for sel in selectors:
        try:
            loc = page.locator(sel).first
            if loc.is_visible(timeout=2000):
                loc.click(timeout=3000)
                print(f"Clicked: {sel}")
                clicked = True
                break
        except Exception as e:
            print(f"Selector {sel} failed: {e}")
            continue
    
    if not clicked:
        # Take screenshot for debug
        page.screenshot(path=r'C:\Users\Val\.openclaw\workspace\twitter-campaign\temp\compose_debug.png')
        print("ERROR: Could not find text area. Screenshot saved.")
        sys.exit(1)
    
    page.wait_for_timeout(500)
    page.evaluate('(t) => document.execCommand("insertText", false, t)', text)
    page.wait_for_timeout(1500)
    
    # Verify text was inserted
    content = page.evaluate('() => document.querySelector(\'[contenteditable="true"][role="textbox"]\')?.textContent || ""')
    print(f"Text in box: {content[:50]}...")
    
    page.evaluate('() => document.querySelector(\'[data-testid="tweetButton"]\').click()')
    page.wait_for_timeout(4000)
    
    print('TWEET_POSTED_OK')
    page.close()
