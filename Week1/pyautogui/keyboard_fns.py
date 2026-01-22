import pyautogui
import time
##Keyboard 
x,y=pyautogui.position()
print(f'{x},{y}')

#pyautogui.write("pip list")
#pyautogui.press("enter")
#time.sleep(16)
#pyautogui.write("clear")
#pyautogui.press("enter")
#pyautogui.click(287,102)
#pyautogui.hotkey('ctrl','a')

location_img=pyautogui.locateOnScreen('agentimg.jpg', confidence=0.34, grayscale=True)
pyautogui.click(pyautogui.center(location_img))

print(pyautogui.size())

screen_img=pyautogui.screenshot()
screen_img.save("demo_screenshot.jpg")