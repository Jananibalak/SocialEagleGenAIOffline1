from playwright.sync_api import sync_playwright
import time

def extract_metadata(page):
    metadata = {}
    metadata["title"] = page.title()

    # all <meta name="...">
    meta_name = page.locator("meta[name]")
    for i in range(meta_name.count()):
        name = meta_name.nth(i).get_attribute("name")
        content = meta_name.nth(i).get_attribute("content")
        if name and content:
            metadata[f"name:{name}"] = content

    # all <meta property="...">
    meta_prop = page.locator("meta[property]")
    for i in range(meta_prop.count()):
        prop = meta_prop.nth(i).get_attribute("property")
        content = meta_prop.nth(i).get_attribute("content")
        if prop and content:
            metadata[f"property:{prop}"] = content

    return metadata


def save_metadata(url, metadata, file_name="website_metadata.txt"):
    with open(file_name, "w", encoding="utf-8") as f:
        f.write(f"Website URL: {url}\n")
        f.write("=" * 70 + "\n\n")
        for k, v in metadata.items():
            f.write(f"{k}: {v}\n")


with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()

    # 1) Open bing
    page.goto("https://www.bing.com", wait_until="domcontentloaded")

    # 2) Accept cookies popup (if it comes)
    try:
        page.locator("text=Accept").first.click(timeout=3000)
    except:
        pass

    # 3) Wait for search box and type query
    query = "SocialEagle AIsele "

    search_box = page.locator("#sb_form_q")
    search_box.wait_for(state="visible", timeout=10000)
    search_box.click()
    search_box.fill(query)
    search_box.press("Enter")

    # 4) Wait for results page
    page.wait_for_load_state("domcontentloaded")

    # 5) Wait for first valid result link
    # Using CSS selector (much more stable than XPath)
    first_result = page.locator("#b_results li.b_algo h2 a").first
    first_result.wait_for(state="visible", timeout=15000)

    first_url = first_result.get_attribute("href")
    print("✅ First result URL:", first_url)

    # 6) Open the first URL
    page.goto(first_url, wait_until="domcontentloaded")
    time.sleep(3)

    # 7) Extract metadata
    metadata = extract_metadata(page)

    # 8) Save to text file
    save_metadata(page.url, metadata, "website_metadata.txt")

    print("✅ Metadata saved to website_metadata.txt")

    browser.close()
