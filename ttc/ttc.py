import json
import re
import smtplib
import time
import boto3

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
from selenium.webdriver.firefox.options import Options
from email.mime.text import MIMEText


def send_email(subject, message):
    f = open("config", encoding="utf-8")
    config = (json.load(f)).get("email")

    subject = config.get("default_subject", "My email")
    sender = config.get("from", "test@gmail.com")
    to = config.get("to", "test@gmail.com")
    smtp = config.get("smtp", "smtp.gmail.com")
    port = config.get("port", 465)
    username = config.get("username", "user")
    password = config.get("password", "pass")

    msg = MIMEText(message)
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = to

    with smtplib.SMTP_SSL(smtp, port) as smtp_server:
        smtp_server.login(username, password)
        smtp_server.sendmail(sender, to, msg.as_string())


def teach(browser):
    print("Try to teach poor guy")
    try:
        browser.get("https://teveclub.hu/tanit.pet")
        tanit_gomb = browser.find_element(
            By.XPATH, "//input[@name='learn'][@type='submit']"
        )
        tanit_gomb.click()
    except Exception as e:
        print(f"The teaching was unsuccessful: {e!r}")
        send_email("Kron notification", f"Problem with camel teaching: {e!r}")


def feed(browser):
    def has_empty_slot():

        images = browser.find_elements(By.TAG_NAME, "img")
        has_empty = False
        for image in images:
            match = re.search("/images/farm/kaja/\d*no.gif", image.get_attribute("src"))
            if match:
                has_empty = True

        return has_empty

    print("Try to give food and drink")
    try:
        while has_empty_slot():
            etet_gomb = browser.find_element(
                By.XPATH, "//input[@name='etet'][@type='submit']"
            )
            etet_gomb.click()
            print(f"+")

    except Exception as e:
        print(f"The feeding was unsuccessful: {e!r}")
        send_email("Kron notification", f"Problem with camel feeding: {e!r}")


def camel_handler(config_json):
    try:
        st = time.time()
        # Read the config file

        username = config_json["username"]
        password = config_json["password"]
        f.close()

        # Create webdriver
        firefox_options = Options()
        firefox_options.add_argument("--headless")
        firefox_options.add_argument("--no-sandbox")
        firefox_options.add_argument("--disable-gpu")
        browser = webdriver.Firefox(options=firefox_options)

        # Log in
        browser.get("https://teveclub.hu/")
        browser.find_element("name", "tevenev").send_keys(username)
        browser.find_element("name", "pass").send_keys(password)
        browser.find_element("name", "pass").send_keys(Keys.ENTER)
        # Wait to logged in
        element_present = EC.presence_of_element_located((By.NAME, "menu0"))
        WebDriverWait(browser, timeout=10).until(element_present)
        browser.get("https://teveclub.hu/myteve.pet")
        print("Logged in successfully")

        # Feed
        feed(browser)

        # Teach
        teach(browser)

        # change_food(browser) later
        browser.quit()
        print("Quit successfully")
        # es.send_email("Kron notification", "Camel cared.")

        # get the end time
        et = time.time()

        # get the execution time
        elapsed_time = et - st
        print("Execution time:", elapsed_time, "seconds")
    except Exception as e:
        print(f"Something went wrong: {e!r}")
        send_email("Kron notification", f"Problem with camel-care script: {e!r}")


def lambda_handler(event, context):
    print(event)
    # config = {
    #     "teveclub": {"username": "sütiii", "password": "hivojel"},
    #     "ncore": {},
    #     "email": {
    #         "default_subject": "Kron notification",
    #         "from": "sutike949@gmail.com",
    #         "to": "sutike949@gmail.com",
    #         "smtp": "smtp.gmail.com",
    #         "username": "sutike949@gmail.com",
    #         "password": "wdhf vqmy jsbo mhjg",
    #         "port": 465,
    #     },
    # }


    ssm = boto3.client('ssm')
    config = ssm.get_parameter(Name='config', WithDecryption=True)
    print(config)
    camel_handler(config)


if __name__ == "__main__":
    f = open(config_file, encoding="utf-8")
    config = (json.load(f)).get("teveclub")
    camel_handler(config)
