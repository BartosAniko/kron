import requests
from bs4 import BeautifulSoup


def get_title(x):
    soup = BeautifulSoup(x.text, 'html.parser')
    return soup.find('title').get_text()


with requests.Session() as s:

    # Login
    print("Try to log in...")
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    payload = "tevenev=xxx&pass=xxx&x=15&y=27&login=Gyere%21"
    response = s.post("https://teveclub.hu/", headers=headers, data=payload, allow_redirects = False)
    location = response.headers.get('Location')
    login = s.get(location)
    if "Az én tevém" in get_title(login):
        print("Login success.")


    # TODO: feed     

    # # Navigate teach page
    # teach_page = s.get("https://teveclub.hu/tanit.pet")
    # if "Tanítás" in get_title(teach_page):
    #     print("You are in the teach page")   

    # Click on teach
    payload = "farmdoit=tanit&learn=Tanulj+teve%21"
    teach = s.post("https://teveclub.hu/tanit.pet", data=payload)
    # TODO : what is doing? 
    if teach.status_code == 200:
        print("Teach was success.")
    else:
        print("Something went wrong")
    