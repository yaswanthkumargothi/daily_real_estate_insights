import asyncio
import sys
import os
import time
import traceback


asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
print("Set WindowsSelectorEventLoopPolicy for better compatibility with Playwright.")

# Import crawler-related dependencies
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode
from crawlers.magicbricks import after_goto as magicbricks_after_goto

async def crawl_magicbricks():
    """Crawl magicbricks.com for properties"""
    print("\n========== CRAWLING MAGICBRICKS.COM ==========")
    
    # Configure the browser
    browser_cfg = BrowserConfig(
        headless=False,
        verbose=True,
        browser_type="firefox",
        user_agent="random",
        use_persistent_context=False,
        ignore_https_errors=True,
        user_data_dir=None,
    )

    session_id = "mb_session"
    
    # Configure the crawler run
    crawler_run_config = CrawlerRunConfig(
        magic=True,
        simulate_user=True, 
        css_selector='div.mb-srp__card',
        mean_delay=0.5,
        cache_mode=CacheMode.BYPASS,
        session_id=session_id,
        page_timeout=30000
    )
    
    try:
        async with AsyncWebCrawler(config=browser_cfg) as crawler:
            # Set the hook
            crawler.crawler_strategy.set_hook("after_goto", magicbricks_after_goto)
            
            # Run the crawler on magicbricks URL
            url = "https://www.magicbricks.com/property-for-sale-rent-in-Visakhapatnam/Plots-Land-Visakhapatnam"
            result = await crawler.arun(url, config=crawler_run_config)
            
            if result.success:
                print("\nCrawled URL:", result.url)
                print("HTML length:", len(result.html))
                
                # Save markdown to a file
                if result.markdown:
                    markdown_file = os.path.join("data", "magicbricks_properties.md")
                    os.makedirs(os.path.dirname(markdown_file), exist_ok=True)
                    with open(markdown_file, "w", encoding="utf-8") as f:
                        f.write(result.markdown)
                    print(f"Markdown content saved to {markdown_file}")
                    print(f"First 500 characters of magicbricks.com markdown content:")
                    print(result.markdown[:500])
                else:
                    print("No markdown content available from magicbricks.com.")
            else:
                print("Error crawling magicbricks.com:", result.error_message)

            # Close the browser after crawling
            if hasattr(crawler, 'browser') and crawler.browser:
                await crawler.browser.close()
                print("Magicbricks.com browser instance closed.")
            else:
                print("No browser instance to close for Magicbricks.com.")

    except Exception as e:
        print(f"Exception during magicbricks.com crawl: {e}")
        traceback.print_exc()

async def main():
    try:
        await crawl_magicbricks()
        print("\n========== MAGICBRICKS CRAWLING COMPLETED ==========")
    except Exception as e:
        print(f"Exception in main: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nCrawling interrupted by user.")
    except Exception as e:
        print(f"Fatal error: {e}")
        traceback.print_exc()
    finally:
        # Add a small delay before exiting to allow cleanup
        time.sleep(0.5)
        print("Exiting program.")