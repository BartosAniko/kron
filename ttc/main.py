import requests
import json

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
import re


def login_request():

    payload_tc = {
        "tevenev": "x",
        "pass": "y",
        "login": "Gyere!",
    }

    with requests.session() as s:

        resp = s.get("https://teveclub.hu", headers={"Connection": "keep-alive"})
        session_id = resp.cookies.get_dict().get("SESSION_ID")

        headers = resp.headers
        print(f"URL: {resp.url}")
        print(f"KUKI: {resp.cookies.get_dict()}\n")
        print(f"HEDÖR: {resp.headers}\n")
        print(f"ID: {session_id}\n")

        response_post = s.post(
            "https://teveclub.hu/", data=payload_tc, cookies={"SESSION_ID": session_id}
        )
        session_id = response_post.cookies.get_dict().get("SESSION_ID")
        print(f"URL: {response_post.url}")


def teach(browser):
    # browser.get("https://www.teveclub.hu/tanit.pet")
    # browser.find_element("css", "css=table:nth-child(1) > tbody > tr > td:nth-child(1) > a:nth-child(3) > img").click()
    # browser.navigate().to("https://www.teveclub.hu/tanit.pet");
    browser.find_element("alt", "Tanítom a tevémet!").click()
    # browser.cli
    # elems = browser.find_elements_by_css_selector(".sc-eYdvao.kvdWiq [href]")
    # links = [elem.get_attribute('href') for elem in elems]
    # elems = WebDriverWait(browser,10).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".sc-eYdvao.kvdWiq [href]")))

    return None


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
config = json.load(f)
username = config["username"]
password = config["password"]
f.close()

browser.find_element("name", "tevenev").send_keys(username)
browser.find_element("name", "pass").send_keys(password)
browser.find_element("name", "pass").send_keys(Keys.ENTER)


element_present = EC.presence_of_element_located((By.NAME, "menu0"))
WebDriverWait(browser, timeout=10).until(element_present)

print("logged in!")

# Teach
# teach(browser)

# Feed
feed(browser)

# change_food(browser)

print("goodbye")
