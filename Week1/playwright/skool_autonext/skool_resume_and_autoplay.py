from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
from urllib.parse import urlparse, parse_qs


START_URL = "https://www.skool.com/social-eagle-ai-6384/classroom"
SIDEBAR_ROOT = "div.styled__CourseMenuWrapper-sc-1penv8o-1"


# ---------------------------
# URL helpers
# ---------------------------
def get_md_from_url(url: str):
    try:
        qs = parse_qs(urlparse(url).query)
        return qs.get("md", [None])[0]
    except:
        return None


# ---------------------------
# Desktop viewport + maximize
# ---------------------------
def maximize_window(context, page):
    cdp = context.new_cdp_session(page)

    window_id = cdp.send("Browser.getWindowForTarget")["windowId"]
    cdp.send("Browser.setWindowBounds", {"windowId": window_id, "bounds": {"windowState": "maximized"}})
    page.wait_for_timeout(800)

    bounds = cdp.send("Browser.getWindowBounds", {"windowId": window_id})["bounds"]
    w = bounds.get("width", 1400)
    h = bounds.get("height", 900)

    # force relayout
    cdp.send("Browser.setWindowBounds", {"windowId": window_id, "bounds": {"width": w - 80, "height": h - 80}})
    page.wait_for_timeout(500)

    cdp.send("Browser.setWindowBounds", {"windowId": window_id, "bounds": {"windowState": "maximized"}})
    page.wait_for_timeout(800)

    page.evaluate("() => window.dispatchEvent(new Event('resize'))")
    page.wait_for_timeout(800)


def force_desktop_viewport(context, page, width=1920, height=1000):
    cdp = context.new_cdp_session(page)
    cdp.send("Emulation.setDeviceMetricsOverride", {
        "width": width,
        "height": height,
        "deviceScaleFactor": 1,
        "mobile": False
    })
    page.wait_for_timeout(500)
    page.evaluate("() => window.dispatchEvent(new Event('resize'))")
    page.wait_for_timeout(800)


# ---------------------------
# Sidebar lesson locators
# ---------------------------
def lesson_links(page):
    return page.locator(f'{SIDEBAR_ROOT} a[href*="/classroom/"][href*="md="]')


def is_completed(anchor):
    try:
        return anchor.locator('[class*="ModuleCompletedIcon"]').count() > 0
    except:
        return False


# ---------------------------
# scrolling
# ---------------------------
def js_scroll_down(page, px=900):
    page.evaluate(f"window.scrollBy(0, {px});")
    page.wait_for_timeout(350)


def js_scroll_to_top(page):
    page.evaluate("window.scrollTo(0, 0);")
    page.wait_for_timeout(800)


def js_scroll_sidebar_into_view(page):
    try:
        page.locator(SIDEBAR_ROOT).scroll_into_view_if_needed(timeout=5000)
    except:
        pass
    page.wait_for_timeout(300)


# ---------------------------
# ✅ Expand sections SAFE (LIMITED rounds - no endless toggle loop)
# ---------------------------
def expand_all_sections_safe(page, rounds=2):
    """
    Expands collapsible sections safely WITHOUT clicking lessons.
    Click ONLY arrow icon SVG.
    Limited rounds to avoid expand/collapse infinite toggling.
    """
    print("📂 Expanding collapsible sections safely (limited rounds)...")
    js_scroll_sidebar_into_view(page)
    js_scroll_to_top(page)

    for r in range(rounds):
        icons = page.locator(
            f"{SIDEBAR_ROOT} div[class*='MenuItemTitleWrapper'] div[class*='SetIcon'] svg"
        )
        n = icons.count()
        if n == 0:
            print("⚠️ No section toggle icons found.")
            return

        clicked = 0
        for i in range(n):
            ico = icons.nth(i)
            try:
                ico.scroll_into_view_if_needed(timeout=1500)
                page.wait_for_timeout(60)
                ico.click(timeout=800, force=True)
                clicked += 1
                page.wait_for_timeout(80)
            except:
                pass

        print(f"✅ Expand round {r+1}: clicked {clicked} arrows")
        js_scroll_down(page, 1400)

    js_scroll_to_top(page)
    page.wait_for_timeout(400)


def load_all_lessons_until_stable(page, max_rounds=180):
    """
    Loads lessons by scrolling ONLY (no repeated expand toggles).
    Stops when link count stable.
    """
    print("📥 Loading all lessons (scroll only)...")
    js_scroll_sidebar_into_view(page)
    js_scroll_to_top(page)

    last_count = -1
    stable = 0

    for _ in range(max_rounds):
        count = lesson_links(page).count()

        if count == last_count:
            stable += 1
        else:
            stable = 0

        if stable >= 10:
            break

        last_count = count
        js_scroll_down(page, 900)

    js_scroll_to_top(page)
    page.wait_for_timeout(800)
    print(f"✅ Lessons loaded. Total visible links: {lesson_links(page).count()}")


# ---------------------------
# click safe
# ---------------------------
def click_anchor_safe(page, anchor):
    try:
        anchor.scroll_into_view_if_needed(timeout=5000)
        page.wait_for_timeout(250)
        anchor.wait_for(state="visible", timeout=5000)
        anchor.click(timeout=5000)
    except:
        try:
            anchor.click(force=True, timeout=5000)
        except:
            pass


# ---------------------------
# Resume / Next
# ---------------------------
def resume_from_first_uncompleted(page):
    print("🔎 Searching for first uncompleted lesson...")

    js_scroll_to_top(page)

    # Expand + Load (two passes)
    expand_all_sections_safe(page, rounds=2)
    load_all_lessons_until_stable(page, max_rounds=200)

    expand_all_sections_safe(page, rounds=1)
    load_all_lessons_until_stable(page, max_rounds=140)

    links = lesson_links(page)
    count = links.count()
    print(f"📌 Total lessons loaded: {count}")

    if count == 0:
        print("❌ No lessons found.")
        return False

    for i in range(count):
        a = links.nth(i)
        if not is_completed(a):
            title = ""
            try:
                title = a.inner_text(timeout=1500).strip()
            except:
                pass

            print(f"➡️ Resuming from lesson #{i+1}: {title}")
            click_anchor_safe(page, a)
            page.wait_for_timeout(3500)
            return True

    print("🏁 All lessons completed already.")
    return False


def wait_for_lesson_change(page, old_url, timeout=25000):
    try:
        page.wait_for_function(
            "(oldUrl) => window.location.href !== oldUrl",
            arg=old_url,
            timeout=timeout
        )
    except:
        pass
    page.wait_for_timeout(2500)


def click_next_lesson(page):
    """
    IMPORTANT:
    - NO section re-expand here.
    - NO heavy reload here.
    - Just click next lesson using already loaded sidebar list.
    """
    links = lesson_links(page)
    count = links.count()

    if count == 0:
        print("❌ No lesson links available.")
        return False

    current_md = get_md_from_url(page.url)
    current_index = -1

    if current_md:
        for i in range(count):
            href = links.nth(i).get_attribute("href") or ""
            if f"md={current_md}" in href:
                current_index = i
                break

    if current_index == -1:
        print("⚠️ Current lesson not detected. Falling back to first uncompleted...")
        for i in range(count):
            if not is_completed(links.nth(i)):
                old_url = page.url
                click_anchor_safe(page, links.nth(i))
                wait_for_lesson_change(page, old_url)
                return True
        return False

    nxt = current_index + 1
    if nxt >= count:
        print("🏁 Reached end of loaded lessons.")
        return False

    old_url = page.url
    click_anchor_safe(page, links.nth(nxt))
    wait_for_lesson_change(page, old_url)
    return True


# ---------------------------
# VIDEO Logic (Thumbnail -> Player)
# ---------------------------
def detect_any_video_player(page):
    try:
        return page.evaluate("""
            () => {
                if (document.querySelector("video")) return true;
                if (document.querySelector("mux-video")) return true;
                if (document.querySelector("mux-player")) return true;
                return false;
            }
        """)
    except:
        return False


def click_thumbnail_to_load_video(page):
    thumb = page.locator("div[class*='ThumbnailImage']").first
    if thumb.count() == 0:
        return False

    try:
        thumb.scroll_into_view_if_needed(timeout=5000)
        page.wait_for_timeout(300)
        thumb.click(force=True, timeout=5000)
        page.wait_for_timeout(2000)
        print("▶️ Clicked thumbnail to load video.")
        return True
    except:
        return False


def force_start_video(page):
    # focus play
    try:
        page.keyboard.press("Space")
    except:
        pass

    try:
        page.evaluate("""
            () => {
                const v = document.querySelector("video");
                if (v) {
                    try { v.muted = true; v.volume = 0; } catch(e){}
                    try { v.playbackRate = 1.0; } catch(e){}
                    try { v.play().catch(()=>{}); } catch(e){}
                }

                const mv = document.querySelector("mux-video") || document.querySelector("mux-player");
                if (mv) {
                    try { mv.muted = true; mv.volume = 0; } catch(e){}
                    try { mv.play().catch(()=>{}); } catch(e){}
                }
            }
        """)
    except:
        pass

'''
def wait_video_ready(page, timeout=35000):
    try:
        page.wait_for_function("""
            () => {
                const v = document.querySelector("video");
                if (v && v.duration && v.duration > 5) return true;

                const mv = document.querySelector("mux-video");
                if (mv && mv.duration && mv.duration > 5) return true;

                return false;
            }
        """, timeout=timeout)
        return True
    except PlaywrightTimeoutError:
        return False
'''

def wait_video_ready(page, timeout=60000):
    """
    Consider video ready if either:
    - duration loads
    - OR video element exists
    - OR currentTime starts moving
    """
    try:
        page.wait_for_function("""
            () => {
                const v = document.querySelector("video");
                const mv = document.querySelector("mux-video");
                const p = v || mv;

                if (!p) return false;

                // duration ok
                if (p.duration && p.duration > 5) return true;

                // currentTime moving => definitely playing
                if (p.currentTime && p.currentTime > 0.5) return true;

                // player exists (Mux may hide duration for long time)
                return true;
            }
        """, timeout=timeout)
        return True
    except:
        return False


def keep_video_alive_until_end(page, max_video_wait_minutes=120):
    timeout_ms = max_video_wait_minutes * 60 * 1000
    start_time = page.evaluate("() => Date.now()")

    while True:
        now = page.evaluate("() => Date.now()")
        if now - start_time > timeout_ms:
            print("⏳ Timeout reached. Skipping...")
            return "timeout"

        ended = page.evaluate("""
            () => {
                const v = document.querySelector("video");
                if (v && v.duration && v.duration > 5) {
                    return v.ended === true || (v.currentTime >= v.duration - 0.5);
                }

                const mv = document.querySelector("mux-video");
                if (mv && mv.duration && mv.duration > 5) {
                    return mv.ended === true || (mv.currentTime >= mv.duration - 0.5);
                }

                return false;
            }
        """)
        if ended:
            print("✅ Video completed.")
            return "ended"

        paused = page.evaluate("""
            () => {
                const v = document.querySelector("video");
                if (v && v.duration && v.duration > 5) return v.paused === true;

                const mv = document.querySelector("mux-video");
                if (mv && mv.duration && mv.duration > 5) return mv.paused === true;

                return false;
            }
        """)
        if paused:
            print("⏸️ Paused detected -> resuming...")
            force_start_video(page)

        page.wait_for_timeout(3000)


def wait_for_video_end_or_skip(page, max_video_wait_minutes=120):
    page.wait_for_timeout(2000)

    if not detect_any_video_player(page):
        click_thumbnail_to_load_video(page)
        page.wait_for_timeout(1500)

    if not detect_any_video_player(page):
        print("📄 No video detected. Skipping...")
        return "no-video"

    force_start_video(page)

    if not wait_video_ready(page):
        print("⚠️ Video duration not loaded. Skipping...")
        return "duration-fail"

    print("🎬 Video running... waiting until it ends.")
    return keep_video_alive_until_end(page, max_video_wait_minutes=max_video_wait_minutes)


# ---------------------------
# MAIN
# ---------------------------
def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=False,
            slow_mo=120,
            args=[
                "--autoplay-policy=no-user-gesture-required",
                "--disable-features=PreloadMediaEngagementData,MediaEngagementBypassAutoplayPolicies",
            ],
        )

        context = browser.new_context(
            storage_state="skool_state.json",
            viewport={"width": 1920, "height": 1000},
            is_mobile=False,
            device_scale_factor=1,
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        )

        page = context.new_page()

        maximize_window(context, page)
        force_desktop_viewport(context, page)

        page.goto(START_URL, wait_until="domcontentloaded", timeout=60000)
        page.wait_for_timeout(5000)

        # ✅ Skool SPA: never use networkidle
        page.reload(wait_until="domcontentloaded", timeout=60000)
        page.wait_for_timeout(5000)

        print("✅ Classroom opened")

        resumed = resume_from_first_uncompleted(page)
        if not resumed:
            browser.close()
            return

        # ✅ Autoplay loop
        while True:
            wait_for_video_end_or_skip(page)

            try:
                page.keyboard.press("Escape")
            except:
                pass

            page.wait_for_timeout(1500)

            # ✅ If reached end of currently loaded lessons,
            # scroll further down once, load more lessons, then try again
            if not click_next_lesson(page):
                print("📌 Trying to load more lessons by scrolling deeper...")
                js_scroll_down(page, 2500)
                page.wait_for_timeout(1500)
                load_all_lessons_until_stable(page, max_rounds=120)

                if not click_next_lesson(page):
                    print("🏁 Done. No next lesson.")
                    break

        browser.close()


if __name__ == "__main__":
    main()
