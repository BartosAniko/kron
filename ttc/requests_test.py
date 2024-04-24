import requests
from bs4 import BeautifulSoup

HEADERS = {'Content-Type': 'application/x-www-form-urlencoded'}

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
    soup = BeautifulSoup(x.text, 'html.parser')
    for span in soup.find_all('span'):
        if span.get('class')[0]=="kiem" and name in span.get_text():
            return True
    return False


with requests.Session() as s:

    # Login
    print("Try to log in...")
    payload = "here is name and pass"
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


    