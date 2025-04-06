import asyncio
from playwright.async_api import Page, BrowserContext

async def after_goto(page: Page, context: BrowserContext, url: str, response, **kwargs):
    """Hook that executes after navigation completes - performs actions for 99acres site."""
    print(f"[HOOK] 99acres - Successfully loaded: {url}")
    
    try:
        # Wait for the page to load properly
        await asyncio.sleep(1)
        
        # Click on search button - updated selector
        await page.click("#plotIndex > section.mb-search > div > div.mb-search-container > div.mb-search__wrap > div.mb-search__btn")
        
        # Wait for search results to load
        await asyncio.sleep(1)
        
        # Apply filter for sorting by date - updated selectors
        await page.click("#body > div.container-fluid > div > div > div.mb-srp__left > div.mb-srp__tabs > div > div.mb-srp__tabs__sortby--title")
        
        # Click on the specific sort option (4th option in the dropdown)
        await page.click("#body > div.container-fluid > div > div > div.mb-srp__left > div.mb-srp__tabs > div > div.mb-srp__tabs__sortby__dd.box-shadow > ul > li:nth-child(4)")

        await asyncio.sleep(3)
        
        print("[HOOK] 99acres - All interactions completed successfully")
    except Exception as e:
        print(f"[HOOK] 99acres - Error during interactions: {e}")
    
    return page