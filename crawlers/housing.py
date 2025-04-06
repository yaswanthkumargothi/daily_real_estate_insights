import asyncio
from playwright.async_api import Page, BrowserContext

async def after_goto(page: Page, context: BrowserContext, url: str, response, **kwargs):
    """Hook that executes after navigation completes - performs all the actions."""
    print(f"[HOOK] after_goto - Successfully loaded: {url}")
    
    try:
        # Wait for initial page load
        await asyncio.sleep(2)
        
        # Click on search input and fill it
        await page.click("div[data-q='search'] input[type='text']")
        await page.fill("div[data-q='search'] input[type='text']", 'Visakhapatnam')
        
        # Wait longer before clicking the search button
        await asyncio.sleep(1)
        
        # Use the data-testid attribute for more reliable button targeting
        await page.click("button[data-testid='buttonId']")
        
        # Wait longer for search results page to fully load
        print("Waiting for search results to load...")
        await page.wait_for_load_state("networkidle")
        await asyncio.sleep(5)

        # Try a more reliable way to find the filter dropdown (with verbose logging)
        print("Looking for filter dropdown...")
        
        # Try alternative selectors for the filter dropdown
        filter_dropdown_selectors = [
            '.input-container .css-gg4vpm',
            'div[data-q="sortBy"]',
            '.css-gg4vpm',
            'button[data-q="sortBy"]'
        ]
        
        for selector in filter_dropdown_selectors:
            try:
                print(f"Trying selector: {selector}")
                is_visible = await page.is_visible(selector, timeout=2000)
                if is_visible:
                    print(f"Found visible element with selector: {selector}")
                    await page.click(selector)
                    break
            except Exception as e:
                print(f"Selector {selector} failed: {e}")
        else:
            print("Could not find any matching filter dropdown element")
            await page.screenshot(path="search_results_debug.png")
        
        # After finding and clicking the filter dropdown, wait longer
        await asyncio.sleep(2)
        
        try:
            await page.click('text="Date Added"', timeout=10000)
            
            # Add significant wait time after completing all actions
            print("All actions completed, waiting to ensure data loads...")
            await asyncio.sleep(10)
        except Exception as e:
            print(f"Error clicking Date Added: {e}")
            await page.screenshot(path="date_added_error.png")
        
        print("[HOOK] All interactions completed successfully")
    except Exception as e:
        print(f"[HOOK] Error during interactions: {e}")
        # Take screenshot on error
        try:
            await page.screenshot(path="error_screenshot.png")
            print("Error screenshot saved")
        except:
            pass
    
    return page