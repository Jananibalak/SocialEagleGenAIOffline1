from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
driver = webdriver.Chrome()
driver.get("https://the-internet.herokuapp.com/")
element=driver.find_element(By.XPATH,'//*[@id="content"]/ul/li[6]/a')

##wait

#wait = WebDriverWait(driver,10)
#element = wait.until(EC.presence_of_element_located((By.XPATH,'//*[@id="content"]/ul/li[6]/a')))

#element.click()

#Interactions
element.click()
#element.send_keys('socialeagle')
#element.clear()

driver.save_screenshot("demo.png")

driver.back()
driver.forward()
driver.refresh()