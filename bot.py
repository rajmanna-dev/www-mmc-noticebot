import os
import config
import smtplib
import requests
import pdfplumber
from time import sleep
from bs4 import BeautifulSoup
from pymongo import MongoClient
from email.mime.text import MIMEText
from datetime import datetime, timedelta
from email.mime.multipart import MIMEMultipart
from apscheduler.schedulers.background import BackgroundScheduler

client = MongoClient(os.environ.get('MONGODB_URL'))
database = client.mmc_noticebot
users_collection = database.users

previous_notice = []
sender_email = os.environ.get('FROM')
password = os.environ.get('PASSWORD')
smtp_server = smtplib.SMTP(os.environ.get('MAIL_SERVER'), os.environ.get('MAIL_PORT'))
smtp_server.starttls()
smtp_server.login(sender_email, password)


def cleanup_expired_tokens():
    expired_cutoff = datetime.now() - timedelta(hours=1)
    users_collection.delete_many({'token_expiration': {'$lt': expired_cutoff}})
    client.close()


def send_mail(notice_title, notice_msg, subscribers):
    message = MIMEMultipart()
    message['From'] = sender_email
    message['Subject'] = notice_title
    message.attach(MIMEText(notice_msg, 'plain'))
    message['To'] = ', '.join(subscribers)
    smtp_server.sendmail(sender_email, subscribers, message.as_string())


def extract_data_from_pdf(file_link):
    r = requests.get(file_link)
    with open('temp.pdf', 'wb') as f:
        f.write(r.content)

    with pdfplumber.open("temp.pdf") as pdf:
        pdf_data = ''.join([page.extract_text() for page in pdf.pages])

    os.remove("temp.pdf")
    return pdf_data


def process_table_rows(row):
    notice_title = row.select_one('td:nth-of-type(2)').get_text()
    notice_link = config.DOMAIN + row.select_one('td:nth-of-type(3) a')['href'].replace(' ', '%20')
    return notice_title, notice_link


def scrape_notice():
    url = config.NOTICE_URL
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')
    tr = soup.find_all('tr')[1]

    global previous_notice
    if tr != previous_notice:
        notice_title, notice_link = process_table_rows(tr)
        notice_text = extract_data_from_pdf(notice_link)

        if not notice_text:
            notice_text = f"Unable to fetch notice content."
        subscribed_users = [user.get('confirmed_email') for user in
                            users_collection.find({'confirmed_email': {'$exists': True}})]
        send_mail(notice_title, f'{notice_text}\nDownload this notice: {notice_link}', subscribed_users)
        previous_notice = tr


scheduler = BackgroundScheduler()
scheduler.add_job(scrape_notice, 'interval', minutes=30)
scheduler.add_job(cleanup_expired_tokens, 'cron', hour=3)
scheduler.start()

try:
    while True:
        sleep(5)
except (KeyboardInterrupt, SystemExit):
    scheduler.shutdown()
    smtp_server.quit()
    client.close()
