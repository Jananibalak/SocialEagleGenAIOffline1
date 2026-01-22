import pyautogui
import time
import webbrowser
import sys
import os

pyautogui.FAILSAFE = True


def click_image(image_path, timeout=25, confidence=0.75):
    print(f"🔍 Searching for image: {image_path}")
    start = time.time()

    while time.time() - start < timeout:
        try:
            loc = pyautogui.locateCenterOnScreen(image_path, confidence=confidence)
            if loc:
                print(f"✅ Found {image_path} at {loc}")
                pyautogui.moveTo(loc)
                time.sleep(0.4)
                pyautogui.click(loc)
                return True
        except Exception as e:
            print("❌ locateCenterOnScreen error:", e)
            return False

        time.sleep(1)

    print(f"❌ Timeout: {image_path} not found.")
    return False


print("🚀 Opening SocialEagle website...")
webbrowser.open("https://socialeagle.ai/")
time.sleep(4)

#print("🖥 Maximizing window...")
#pyautogui.hotkey("win", "up")
#time.sleep(2)

print("🔎 Setting zoom 100%...")
pyautogui.hotkey("ctrl", "0")
time.sleep(1)

# small scroll to ensure menu visible
pyautogui.scroll(-300)
time.sleep(2)

# 1) Click Contact button
if not click_image("contact_button.png", timeout=35, confidence=0.95):
    print("❌ Contact button not found.")
    pyautogui.screenshot("debug_contact_not_found.png")
    sys.exit()

time.sleep(5)

# 2) Press TAB 2 times
print("⌨ Pressing TAB 2 times...")
pyautogui.press("tab")
time.sleep(0.4)
pyautogui.press("tab")
time.sleep(0.6)

# 3) Type "eagle"
print("⌨ Typing text: eagle")
pyautogui.write("Eagle", interval=0.08)
time.sleep(1)

# ✅ Focus modal by clicking screen center
screen_w, screen_h = pyautogui.size()
pyautogui.click(screen_w // 2, screen_h // 2)
time.sleep(1)

# 4) Scroll down
print("🌀 Scrolling down...")
pyautogui.scroll(-900)
time.sleep(2)

# 5) Click Submit button
if not click_image("submit_button.png", timeout=30, confidence=0.70):
    print("❌ Submit button not found.")
    pyautogui.screenshot("debug_submit_not_found.png")
    sys.exit()

time.sleep(4)

# 6) Screenshot
output_file = "socialeagle_after_submit.png"
pyautogui.screenshot(output_file)
os.startfile(output_file)
print("✅ Screenshot saved as:", output_file)
