import boto3
import json
import requests
import re
from bs4 import BeautifulSoup


HEADERS = {'Content-Type': 'application/x-www-form-urlencoded'}
LOCAL_RUN = False

def get_title(x):
    soup = BeautifulSoup(x.text, 'html.parser')
    return soup.find('title').get_text()


def get_food_drink_empty(x):
    soup = BeautifulSoup(x.text, 'html.parser')
    kaja=pia=None
    no=0
    for img in soup.find_all('img'):
        src = img.get('src')
        if "/images/farm/kaja/" in src:
            if 'no' in src[18:-4]:
                no += 1
            kaja=src[18:-4].replace('no','')
        if "/images/farm/pia/" in src:
            pia=src[17:-4].replace('no','')
    return [kaja, pia, no]


def free_list_next(x, actual):
    soup = BeautifulSoup(x.text, 'html.parser')
    free_list = []
    for ingyenes_str in soup.find_all(string = 'Ingyenes!'):
        parent = ingyenes_str.find_parent("td")
        inputs = parent.find('input')
        if len(free_list)>0 and free_list[-1] == actual:
            return inputs.get('value')
        free_list.append(inputs.get('value'))
    return free_list[0]


def is_highlighted(x, name):
    # Todo: write this function better
    soup = BeautifulSoup(x.text, 'html.parser')
    for span in soup.find_all('span'):
        if "class=\"kiem\"":
            if name in span.get_text():
                return True
    return False

def get_next_trick(x):
    print('get the cheapest trick')
    soup = BeautifulSoup(x.text, 'html.parser')
    smallest = 1000
    id=""
    for span in soup.find_all('select'):
        if span.get('name') == "tudomany":
            for option in span.find_all('option'):
                result = re.search(r".*value=\"(\d*)\".*\((\d*) lecke", str(option))
                actual = int(result.group(2))
                if(actual<smallest):
                    smallest = actual
                    id = result.group(1)
                    print(str(option))
    return id


def lambda_handler(event, context):
    print("\n\n")
    global LOCAL_RUN
    LOCAL_RUN = event.get('local_run', False)
    if not LOCAL_RUN:
        client = boto3.client('ssm')
        parameter = client.get_parameter(Name='kron_secrets', WithDecryption=True)
        login_payload = json.loads(parameter.get('Parameter',{}).get('Value',{})).get('teveclub',{}).get('login')
    else:
        with open('config.json') as f:
            login_payload = (json.load(f)).get('teveclub',{}).get('login')
    

        # print(login_payload)
    
    with requests.Session() as s:
        # Login
        print("Try to log in...")
        payload = login_payload
        response = s.post("https://teveclub.hu/", headers=HEADERS, data=payload, allow_redirects = False)
        location = response.headers.get('Location')
        login = s.get(location)
        if "Az én tevém" in get_title(login):
            print("Login success.")
        else:
            print('Something went wrong in login')

        # Get actual food, drink and count empty slot
        food_drink_empty = get_food_drink_empty(login)
        food = food_drink_empty[0]
        drink = food_drink_empty[1]
        empty = food_drink_empty[2]
        
        # Feed
        feed = s.post("https://teveclub.hu/myteve.pet", headers=HEADERS, data=f"kaja={empty}&pia={empty}&etet=Mehet%21")
        if get_food_drink_empty(feed)[2] == 0:
            print(f"Feed was success: added {empty} amount")

        # Change food 
        food_menu = s.get("https://teveclub.hu/setfood.pet")
        next_food = free_list_next(food_menu, food)
        set_food = s.post("https://teveclub.hu/setfood.pet", headers = HEADERS, data=f"kaja={next_food}")
        # Change drink
        drink_menu = s.get("https://teveclub.hu/setdrink.pet")
        next_drink = free_list_next(drink_menu, drink)
        set_drink = s.post("https://teveclub.hu/setdrink.pet", headers = HEADERS, data=f"kaja={next_drink}")

        after_feed = get_food_drink_empty(set_drink)
        if food != after_feed[0] and drink != after_feed[1]:
            print("Food and drink was changed.")

        # Teach
        payload = "farmdoit=tanit&learn=Tanulj+teve%21"
        teach = s.post("https://teveclub.hu/tanit.pet",  headers = HEADERS, data=payload)
        teach_result = s.get(location)
        if not is_highlighted(teach_result, "Tanítás"):
            print("Teach was success.")
        else:
            print("Choose a 'cheap' trick")
            teach = s.get("https://teveclub.hu/tanit.pet")
            next_trick=get_next_trick(teach)
            payload=f"tudomany={next_trick}&learn=Tanulj+teve%21"
            teach = s.post("https://teveclub.hu/tanit.pet",  headers = HEADERS, data=payload)
        
        teach_result = s.get(location)
        print(is_highlighted(teach_result, "Tanítás"))

        # Todo: Egyszam jatek   
    print("\n\n")
    return 0

# For testing purposes when not running on Lambda
if __name__ == "__main__":
    event = {
        'local_run': True
    }
    lambda_handler(event, None)
