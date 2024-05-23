import boto3
import json
import requests
import re
from bs4 import BeautifulSoup


HEADERS = {"Content-Type": "application/x-www-form-urlencoded"}
LOCAL_RUN = False
SNS_TOPIC = "alertme"

STATUS = []
ERRORS = []


def sns_sender(message):
    sns = boto3.resource("sns")
    topic = sns.create_topic(Name=SNS_TOPIC)
    response = topic.publish(Message=message)


def _print(text):
    global STATUS
    STATUS.append(text)
    print(text)


def _error(text):
    global ERRORS
    ERRORS.append(text)


def get_title(x):
    soup = BeautifulSoup(x.text, "html.parser")
    return soup.find("title").get_text()


def get_food_drink_empty(x):
    soup = BeautifulSoup(x.text, "html.parser")
    kaja = pia = None
    no = 0
    for img in soup.find_all("img"):
        src = img.get("src")
        if "/images/farm/kaja/" in src:
            if "no" in src[18:-4]:
                no += 1
            kaja = src[18:-4].replace("no", "")
        if "/images/farm/pia/" in src:
            pia = src[17:-4].replace("no", "")
    return [kaja, pia, no]


def free_list_next(x, actual):
    soup = BeautifulSoup(x.text, "html.parser")
    free_list = []
    for ingyenes_str in soup.find_all(string="Ingyenes!"):
        parent = ingyenes_str.find_parent("td")
        inputs = parent.find("input")
        if len(free_list) > 0 and free_list[-1] == actual:
            return inputs.get("value")
        free_list.append(inputs.get("value"))
    return free_list[0]


def is_highlighted(x, name):
    soup = BeautifulSoup(x.text, "html.parser")
    for span in soup.find_all("span"):
        if 'class="kiem"':
            if name in span.get_text():
                return True
    return False


def get_next_trick(x):
    _print("get the cheapest trick")
    soup = BeautifulSoup(x.text, "html.parser")
    smallest = 1000
    id = ""
    for span in soup.find_all("select"):
        if span.get("name") == "tudomany":
            for option in span.find_all("option"):
                result = re.search(r".*value=\"(\d*)\".*\((\d*) lecke", str(option))
                actual = int(result.group(2))
                if actual < smallest:
                    smallest = actual
                    id = result.group(1)
    return id


def lambda_handler(event, context):
    global LOCAL_RUN
    LOCAL_RUN = event.get("local_run", False)
    try:
        # 1 - get secrets
        if not LOCAL_RUN:
            client = boto3.client("ssm")
            parameter = client.get_parameter(Name="kron_secrets", WithDecryption=True)
            login_payload = (
                json.loads(parameter.get("Parameter", {}).get("Value", {}))
                .get("teveclub", {})
                .get("login")
            )
        else:
            with open("config.json") as f:
                login_payload = (json.load(f)).get("teveclub", {}).get("login")

        with requests.Session() as s:
            # 2 - Login
            _print("Try to log in...")
            payload = login_payload
            response = s.post(
                "https://teveclub.hu/",
                headers=HEADERS,
                data=payload,
                allow_redirects=False,
            )
            location = response.headers.get("Location")
            login = s.get(location)
            if "Az én tevém" in get_title(login):
                _print("Login success.")
            else:
                _error("Something went wrong in login")
                _print("Something went wrong in login")

            # 3 - Get actual food, drink and count empty slot
            food_drink_empty = get_food_drink_empty(login)
            food = food_drink_empty[0]
            drink = food_drink_empty[1]
            empty = food_drink_empty[2]

            # 4 - Feed
            feed = s.post(
                "https://teveclub.hu/myteve.pet",
                headers=HEADERS,
                data=f"kaja={empty}&pia={empty}&etet=Mehet%21",
            )
            if get_food_drink_empty(feed)[2] == 0:
                _print(f"Feed was success: added {empty} amount")
            else:
                _error(f"Feed/ give drink wasn't success. Amount: {empty}")

            # 5 - Change food
            food_menu = s.get("https://teveclub.hu/setfood.pet")
            next_food = free_list_next(food_menu, food)
            set_food = s.post(
                "https://teveclub.hu/setfood.pet",
                headers=HEADERS,
                data=f"kaja={next_food}",
            )
            # 6 - Change drink
            drink_menu = s.get("https://teveclub.hu/setdrink.pet")
            next_drink = free_list_next(drink_menu, drink)
            set_drink = s.post(
                "https://teveclub.hu/setdrink.pet",
                headers=HEADERS,
                data=f"kaja={next_drink}",
            )

            after_feed = get_food_drink_empty(set_drink)
            if food != after_feed[0] and drink != after_feed[1]:
                _print("Food and drink was changed.")
            else:
                global ERRORS
                ERRORS.append("Can't change the food.")

            # 7 - Teach
            payload = "farmdoit=tanit&learn=Tanulj+teve%21"
            teach = s.post(
                "https://teveclub.hu/tanit.pet", headers=HEADERS, data=payload
            )
            teach_result = s.get(location)
            if not is_highlighted(teach_result, "Tanítás"):
                _print("Teach was success.")
            else:
                _error("Can't teach.. Try to teach a new trick")
                _print("Choose a 'cheap' trick")
                teach = s.get("https://teveclub.hu/tanit.pet")
                next_trick = get_next_trick(teach)
                _error(f"Next trick is: {next_trick}")
                _print(f"Next trick is: {next_trick}")
                payload = f"tudomany={next_trick}&learn=Tanulj+teve%21"
                teach = s.post(
                    "https://teveclub.hu/tanit.pet", headers=HEADERS, data=payload
                )

            teach_result2 = s.get(location)
            if is_highlighted(teach_result2, "Tanítás"):
                _error("Teach still highlighted!")

            if not LOCAL_RUN and len(ERRORS) > 0:
                sns_sender(f"Teve is not ok:  {', '.join(ERRORS)}")
    except Exception as e:
        if not LOCAL_RUN:
            sns_sender(f"Something wrong with camel: {e}, {', '.join(ERRORS)}")

        # Todo: Egyszam jatek
    print("\n\n")
    return 0


# For testing purposes when not running on Lambda
if __name__ == "__main__":
    event = {"local_run": True}
    lambda_handler(event, None)
