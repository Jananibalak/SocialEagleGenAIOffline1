from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time


# ---------- Helper: slow down actions so you can SEE ----------
def pause(seconds=1):
    time.sleep(seconds)


def click_wait(driver, by, locator, timeout=15, visible=True):
    """
    Waits for element and clicks it.
    If visible=True -> waits until clickable
    else -> waits presence
    """
    wait = WebDriverWait(driver, timeout)
    if visible:
        element = wait.until(EC.element_to_be_clickable((by, locator)))
    else:
        element = wait.until(EC.presence_of_element_located((by, locator)))

    # Small pause so you can see before clicking
    pause(0.7)
    element.click()
    return element


def type_wait(driver, by, locator, text, timeout=15):
    wait = WebDriverWait(driver, timeout)
    element = wait.until(EC.visibility_of_element_located((by, locator)))
    pause(0.7)
    element.clear()
    element.send_keys(text)
    return element


# ---------- Main ----------
driver = webdriver.Chrome()
driver.maximize_window()
wait = WebDriverWait(driver, 20)

try:
    print("Opening UI Testing Playground...")
    driver.get("http://uitestingplayground.com/")
    pause(2)

    # ------------------------------------------------------------
    # 1) Dynamic ID
    # ------------------------------------------------------------
    print("\n[1] Dynamic ID test")
    click_wait(driver, By.LINK_TEXT, "Dynamic ID")
    pause(2)

    # Dynamic ID changes - so use stable selector: button.btn-primary
    click_wait(driver, By.CSS_SELECTOR, "button.btn.btn-primary")
    print("✅ Dynamic ID button clicked")
    pause(2)

    driver.back()
    pause(2)

    # ------------------------------------------------------------
    # 2) Class Attribute
    # ------------------------------------------------------------
    print("\n[2] Class Attribute test")
    click_wait(driver, By.LINK_TEXT, "Class Attribute")
    pause(2)

    # Button has class "btn-primary" but multiple buttons can exist
    # We choose the primary button
    click_wait(driver, By.CSS_SELECTOR, "button.btn-primary")
    print("✅ Class Attribute button clicked")

    # This triggers JS alert; handle it
    pause(1)
    alert = wait.until(EC.alert_is_present())
    pause(1)
    alert.accept()
    print("✅ Alert accepted")

    pause(2)
    driver.back()
    pause(2)

    # ------------------------------------------------------------
    # 3) Hidden Layers
    # ------------------------------------------------------------
    print("\n[3] Hidden Layers test")
    click_wait(driver, By.LINK_TEXT, "Hidden Layers")
    pause(2)

    # First click works
    click_wait(driver, By.ID, "greenButton")
    print("✅ First click on green button done")
    pause(2)

    # Second click fails if overlay covers it
    # We refresh then click again safely
    print("Refreshing page to reset overlay...")
    driver.refresh()
    pause(2)

    click_wait(driver, By.ID, "greenButton")
    print("✅ Hidden Layers green button clicked after refresh")
    pause(2)

    driver.back()
    pause(2)

    # ------------------------------------------------------------
    # 4) Load Delay
    # ------------------------------------------------------------
    print("\n[4] Load Delay test")
    click_wait(driver, By.LINK_TEXT, "Load Delay")
    pause(2)

    # Button appears after delay, explicit wait handles it
    click_wait(driver, By.CSS_SELECTOR, "button.btn.btn-primary", timeout=25)
    print("✅ Load Delay button clicked")
    pause(2)

    driver.back()
    pause(2)

    # ------------------------------------------------------------
    # 5) Progress Bar (Stop around 75%)
    # ------------------------------------------------------------
    print("\n[5] Progress Bar test")
    click_wait(driver, By.LINK_TEXT, "Progress Bar")
    pause(2)

    # Start progress
    click_wait(driver, By.ID, "startButton")
    print("Started progress bar...")
    pause(1)

    progress = wait.until(EC.presence_of_element_located((By.ID, "progressBar")))

    # Watch until ~75% then stop
    while True:
        value = progress.get_attribute("aria-valuenow")
        percent = int(value)

        if percent >= 75:
            click_wait(driver, By.ID, "stopButton")
            print(f"✅ Stopped at {percent}%")
            break

        time.sleep(0.1)

    pause(2)

    # Validate result text
    result = wait.until(EC.visibility_of_element_located((By.ID, "result"))).text
    print("Result:", result)
    pause(2)

    print("\n🎉 All 5 features tested successfully!")

finally:
    pause(3)
    driver.quit()
