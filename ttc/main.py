import requests
import json

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
import re


def teach(browser):
    try:
        browser.get('https://teveclub.hu/tanit.pet')
        tanit_gomb = browser.find_element(By.XPATH, "//input[@name='learn'][@type='submit']")
        tanit_gomb.click()
    except Exception as e: 
        print("valamiért nem sikerült tanítani") 


def feed(browser):
    def has_empty_slot():
        
        images = browser.find_elements(By.TAG_NAME, 'img')
        has_empty = False
        for image in images:
            match = re.search("/images/farm/kaja/\d*no.gif",image.get_attribute('src'))
            if match:
                has_empty = True

        return has_empty

    try:
        print("set drink and food")
        while has_empty_slot():
            etet_gomb = browser.find_element(By.XPATH, "//input[@name='etet'][@type='submit']")
            etet_gomb.click()
            print(f"fed")

    except Exception as e:
        print(f"ayy no : {e}")


print("hello")
print("\n----------------------------------------------")
print("selenium")

browser = webdriver.Firefox()
browser.get("https://teveclub.hu/")

f = open("config", encoding="utf-8")
config = (json.load(f)).get("teveclub")
username = config["username"]
password = config["password"]
f.close()

browser.find_element("name", "tevenev").send_keys(username)
browser.find_element("name", "pass").send_keys(password)
browser.find_element("name", "pass").send_keys(Keys.ENTER)


element_present = EC.presence_of_element_located((By.NAME, "menu0"))
WebDriverWait(browser, timeout=10).until(element_present)

print("logged in!")


browser.get('https://teveclub.hu/myteve.pet')

# Feed
feed(browser)

# Teach
teach(browser)

# change_food(browser)

print("goodbye")
# browser.close()
browser.quit()
