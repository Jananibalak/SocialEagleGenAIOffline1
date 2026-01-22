import pyautogui
import time
print("imported pyautogui")

#pyautogui.click(100,100)
pyautogui.rightClick(100,100)

x,y=pyautogui.position()
print(f'{x},{y}')

pyautogui.doubleClick(200,200)
# --- Dragging to absolute coordinates ---
# Move to the start point without clicking first (optional but recommended)
pyautogui.moveTo(100, 100) 
# Drag from the current position to (300, 300) over 2 seconds, holding the left button
pyautogui.dragTo(300, 300, duration=2, button='left') 

time.sleep(1) # Pause to observe the action

# --- Dragging relative to the current position ---
# Drag 200 pixels to the right and 0 pixels down over 1 second
pyautogui.drag(200, 0, duration=1, button='left') 

time.sleep(1)

# Drag back to the approximate start area using relative coordinates
pyautogui.drag(-400, -200, duration=2, button='left')

#scroll
pyautogui.scroll(1000)


