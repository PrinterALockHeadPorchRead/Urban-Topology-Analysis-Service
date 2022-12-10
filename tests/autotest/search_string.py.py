from selenium import webdriver
import time
from selenium.webdriver.common.by import By


link = "http://localhost:4200/"
browser = webdriver.Chrome()
browser.get(link)

search_string = browser.find_element(By.XPATH, "/html/body/town-finder/div/app-city-list/div/form/input")
search_string.send_keys("Москва")
knop = browser.find_element(By.XPATH, "/html/body/town-finder/div/app-city-list/div/form/button/span").click()
time.sleep(2)
test = browser.find_element(By.XPATH, "/html/body/town-finder/div/app-city-list/div/div/a/div[2]/h2").text
test_1 = "Москва"
if test == test_1:
        print("Verification was successful")
else:
        print("Verification failed")
browser.quit()



