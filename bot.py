import os
import config
import smtplib
import requests
import pdfplumber
from time import sleep
from bs4 import BeautifulSoup
from pymongo import MongoClient
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from apscheduler.schedulers.background import BackgroundScheduler


previous_notice = []
sender_email = config.FROM
password = config.PASSWORD


# Cleanup the expired tokens every day at 3:00
def cleanup_expired_tokens():
    expired_cutoff = datetime.now() - timedelta(hours=1)
    client = MongoClient('localhost', 27017)
    database = client.noticeBot
    users = database.users
    users.delete_many({'token_expiration': {'$lt': expired_cutoff}})
    client.close()


# Send bulk mails
def send_mail(notice_title, notice_msg, subscribers):
    with smtplib.SMTP(config.MAIL_SERVER, config.MAIL_PORT) as server:
        server.starttls()
        server.login(sender_email, password)

        for subscriber_email in subscribers:
            message = MIMEMultipart()
            message['From'] = sender_email
            message['To'] = subscriber_email
            message['Subject'] = notice_title

            body = notice_msg
            message.attach(MIMEText(body, 'plain'))

            text = message.as_string()
            server.sendmail(sender_email, subscriber_email, text)
            print(f"Mail sent from {sender_email} to {subscriber_email}")  # TODO Remove this line of code later
            sleep(5)  # sleep for 5 sec


# Get text from notice pdf
def extract_data_from_pdf(file_link):
    r = requests.get(file_link)
    with open('temp.pdf', 'wb') as f:
        f.write(r.content)

    with pdfplumber.open("temp.pdf") as pdf:
        text = ''.join([page.extract_text() for page in pdf.pages])

    os.remove("temp.pdf")
    return text


# Process the first row of notice table
def process_table_rows(row):
    notice_title = row.select_one('td:nth-of-type(2)').get_text()  # Get notice title
    notice_path = config.DOMAIN + row.select_one('td:nth-of-type(3) a')['href'].replace(' ', '%20')  # Get notice link
    return notice_title, notice_path


# Scrape the student notice page
def scrape_notice():
    url = config.NOTICE_URL
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')
    tr = soup.find_all('tr')[1]  # Get the first row

    global previous_notice
    if tr != previous_notice:
        notice_title, notice_link = process_table_rows(tr)
        notice_text = extract_data_from_pdf(notice_link)

        client = MongoClient('localhost', 27017)
        database = client.noticeBot
        users = database.users

        # If notice text is empty
        if not notice_text:
            notice_text = f"Unable to fetch notice content."
        if users.count_documents({}) != 0:
            subscribed_users = [user.get('confirmed_email') for user in users.find()]
            subscribed_users = [confirmed_email for confirmed_email in subscribed_users if confirmed_email]
            send_mail(notice_title, notice_text + "\n" + notice_link, subscribed_users)
        previous_notice = tr
    else:
        # TODO Remove this line later
        print("Notice already sent!")


scheduler = BackgroundScheduler()
scheduler.add_job(scrape_notice, 'interval', seconds=60)
scheduler.add_job(cleanup_expired_tokens, 'cron', hour=3)
scheduler.start()

while True:
    sleep(5)