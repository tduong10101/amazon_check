import requests
import json
from selectorlib import Extractor
import smtplib, ssl
import time
import logging
import logging.handlers as handlers

logger = logging.getLogger('amazon_checker')
logger.setLevel(logging.INFO)
logHandler = handlers.RotatingFileHandler('amazon_checker.log',encoding='utf-8', maxBytes=50000, backupCount=2)
logHandler.setLevel(logging.INFO)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logHandler.setFormatter(formatter)
logger.addHandler(logHandler)

e = Extractor.from_yaml_file('selectors.yml')
HEADERS = {
        'authority': 'www.amazon.com',
        'pragma': 'no-cache',
        'cache-control': 'no-cache',
        'dnt': '1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.128 Safari/537.36',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'sec-fetch-site': 'none',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-dest': 'document',
        'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
    }

with open("cred.json",'r') as cred:
    cred_data = json.loads(cred.read())
    SENDER = cred_data['email']
    PASSWORD = cred_data['password']
    RECEIVER = cred_data['receiver']

def send_email(message):                       
    port = 587  # For starttls
    smtp_server = "smtp.mail.yahoo.com"
    sender_email = SENDER
    receiver_email = RECEIVER
    password = PASSWORD
    context = ssl.create_default_context()
    with smtplib.SMTP(smtp_server, port) as server:
        server.ehlo()  # Can be omitted
        server.starttls(context=context)
        server.ehlo()  # Can be omitted
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, message)  
    logger.info(f"Message sent from {sender_email} to {receiver_email}")

def scrape(url):
    r = requests.get(url, headers = HEADERS)
    if r.status_code > 500:
        logger.error("Page %s must have been blocked by Amazon as the status code was %d"%(url,r.status_code))
        return None
    return e.extract(r.text)

while True:
    with open("urls.txt","r") as urllist:
        for url in urllist.readlines():
            data = scrape(url)
            if not(data['product_not_availble']):
                message = f"Subject: {data['name']} is available on Amazon!\n\n {data['name']} is available! Get it now! Current price is {data['price']}\n\nLink: {url}"
                send_email(message)
                logger.info(f"Message subject: {data['name']} is available on Amazon!")

    logger.info("Script completed with no issue! Sleeping for 15 minutes")
    time.sleep(900)