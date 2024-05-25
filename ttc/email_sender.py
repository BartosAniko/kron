import smtplib
import json
from email.mime.text import MIMEText

def send_email(subject, message):
    f = open("config", encoding="utf-8")
    config = (json.load(f)).get("email")

    subject = config.get("default_subject","My email")
    sender = config.get("from","test@gmail.com")
    to = config.get("to","test@gmail.com")
    smtp = config.get("smtp","smtp.gmail.com")
    port = config.get("port", 465)
    username = config.get("username", "user")
    password = config.get("password", "pass")

    msg = MIMEText(message)
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = to

    with smtplib.SMTP_SSL(smtp, port) as smtp_server:
       smtp_server.login(username, password)
       smtp_server.sendmail(sender, to, msg.as_string())


def send_sns(message):
    sns = boto3.resource("sns")
    topic = sns.create_topic(Name=SNS_TOPIC)
    response = topic.publish(Message=message)


def send_alert(LOCAL_RUN, message):
    if LOCAL_RUN:
        send_email("alert from kron", message)
    else:
        send_sns(message)

