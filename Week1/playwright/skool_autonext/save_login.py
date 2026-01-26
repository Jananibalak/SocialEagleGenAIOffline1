from playwright.sync_api import sync_playwright

URL = "https://www.skool.com/social-eagle-ai-6384/classroom"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()

    page.goto(URL)

    input("👉 Login manually in browser, then press ENTER here...")

    context.storage_state(path="skool_state.json")
    print("✅ Saved session: skool_state.json")

    browser.close()
