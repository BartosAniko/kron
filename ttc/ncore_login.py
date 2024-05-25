import requests
import json
from bs4 import BeautifulSoup
import boto3
import email_sender

def login_to_ncore(LOCAL_RUN=False):
    with requests.Session() as s:
        print("Try to log in...")

        if not LOCAL_RUN:
            client = boto3.client("ssm")
            parameter = client.get_parameter(Name="kron_secrets", WithDecryption=True)
            login_payload = (
                json.loads(parameter.get("Parameter", {}).get("Value", {}))
                .get("ncore", {})
                .get("login")
            )
        else:
            with open("config.json") as f:
                login_payload = (json.load(f)).get("ncore", {}).get("login")

        response = s.post(
            "https://ncore.pro/login.php?honnan=/hitnrun.php?id=312639",
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            data=login_payload,
            allow_redirects=True,
        )
        soup = BeautifulSoup(response.text, "html.parser")
        points = -1
        for span in soup.find_all("a"):
            if 'href="wiki.php?action=read&amp;id=33"' in str(span):
                points = int(span.text)

        if points >= 0 and response.status_code == 200:
            print(points)
        else:
            email_sender.send_alert(LOCAL_RUN, "Problem with ncore login")

