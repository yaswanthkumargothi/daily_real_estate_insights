import asyncio
import sys
import os
import time
import traceback


asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
print("Set WindowsSelectorEventLoopPolicy for better compatibility with Playwright.")

# Import crawler-related dependencies
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode
from crawlers.housing import after_goto as housing_after_goto
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

async def crawl_housing():
    """Crawl housing.com for properties"""
    print("\n========== CRAWLING HOUSING.COM ==========")
    
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

    session_id = "hn_session"
    
    # Configure the crawler run
    crawler_run_config = CrawlerRunConfig(
        magic=True,
        simulate_user=True, 
        css_selector='[data-testid="card-container"]',
        mean_delay=2.0,
        session_id=session_id,
        page_timeout=120000,
        cache_mode=CacheMode.BYPASS
    )
    
    try:
        async with AsyncWebCrawler(config=browser_cfg) as crawler:
            # Set the hook
            crawler.crawler_strategy.set_hook("after_goto", housing_after_goto)
            
            # Run the crawler on housing.com
            url = "https://housing.com/in/buy/plots-in-visakhapatnam"
            result = await crawler.arun(url, config=crawler_run_config)
            
            if result.success:
                print("\nCrawled URL:", result.url)
                print("HTML length:", len(result.html))
                
                # Save markdown to a file
                if result.markdown:
                    markdown_file = os.path.join("data", "housing_properties.md")
                    os.makedirs(os.path.dirname(markdown_file), exist_ok=True)
                    with open(markdown_file, "w", encoding="utf-8") as f:
                        f.write(result.markdown)
                    print(f"Markdown content saved to {markdown_file}")
                    print(f"First 500 characters of housing.com markdown content:")
                    print(result.markdown[:500])
                else:
                    print("No markdown content available from housing.com.")
            else:
                print("Error crawling housing.com:", result.error_message)

            # Close the browser after crawling
            if hasattr(crawler, 'browser') and crawler.browser:
                await crawler.browser.close()
                print("Housing.com browser instance closed.")
            else:
                print("No browser instance to close for Housing.com.")

    except Exception as e:
        print(f"Exception during housing.com crawl: {e}")
        traceback.print_exc()

async def main():
    try:
        await crawl_housing()
        print("\n========== HOUSING CRAWLING COMPLETED ==========")
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