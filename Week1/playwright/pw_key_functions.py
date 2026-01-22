from playwright.async_api import async_playwright
import asyncio
async def playwright_fn():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        pages = await browser.new_page()

        #navigaton
        await pages.goto("https://www.google.com")
        
        await pages.wait_for_timeout(10000)
        await browser.close()

if __name__=="__main__":
    asyncio.run(playwright_fn())