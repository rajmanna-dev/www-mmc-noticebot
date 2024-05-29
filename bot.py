import os
import logging
import smtplib
import requests
import pdfplumber
import email_message
from time import sleep
from bs4 import BeautifulSoup
from pymongo import MongoClient
from email.mime.text import MIMEText
from datetime import datetime, timedelta
from email.mime.multipart import MIMEMultipart
from apscheduler.schedulers.background import BackgroundScheduler

logging.basicConfig(filename='bot.log', level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')

mail_server = os.environ.get('MAIL_SERVER')
mail_port = int(os.environ.get('MAIL_PORT'))
sender_email = os.environ.get('FROM', 'no-replay@gmail.com')
password = os.environ.get('PASSWORD')
previous_notice = None

mongo_url = os.environ.get('MONGODB_URL')
client = MongoClient(mongo_url)
db = client.mmc_noticebot


def cleanup_expired_tokens():
    try:
        expired_cutoff = datetime.now() - timedelta(hours=1)
        db.users.delete_many({'token_expiration': {'$lt': expired_cutoff}})
    except Exception as e:
        logging.error('Error occurs while trying to cleaning up expired tokens: %s', e)


def send_mail(notice_title, notice_msg, subscribers):
    if subscribers:
        for subscriber in subscribers:
            try:
                message = MIMEMultipart()
                message['From'] = sender_email
                message['To'] = subscriber
                message['Subject'] = notice_title
                message.attach(MIMEText(notice_msg, 'plain'))

                with smtplib.SMTP_SSL(mail_server, mail_port) as smtp_server:
                    smtp_server.login(sender_email, password)
                    smtp_server.sendmail(sender_email, subscriber, message.as_string())
                sleep(8)
            except smtplib.SMTPException as e:
                logging.error("Error occurs while trying to sending email: %s", e)


def extract_data_from_pdf(file_link):
    try:
        response = requests.get(file_link)
        response.raise_for_status()

        with open('temp.pdf', 'wb') as f:
            f.write(response.content)

        with pdfplumber.open("temp.pdf") as pdf:
            if len(pdf.pages) > 1:
                return None
            pdf_data = ''.join([page.extract_text() for page in pdf.pages])

        return pdf_data
    except (requests.RequestException, pdfplumber.PDFSyntaxError) as e:
        logging.error("Error occurs while trying to extracting data from notice pdf: %s", e)
        return None
    finally:
        if os.path.exists('temp.pdf'):
            os.remove('temp.pdf')


def process_table_rows(row):
    try:
        notice_title = row.select_one('td:nth-of-type(2)').get_text().strip()
        notice_link = os.environ.get('DOMAIN') + row.select_one('td:nth-of-type(3) a')['href'].replace(' ', '%20')
        return notice_title, notice_link
    except Exception as e:
        logging.error("Error occurs while trying to process notice content: %s", e)
        return None, None


def scrape_notice():
    global previous_notice
    try:
        response = requests.get(os.environ.get('NOTICE_URL'))
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        tr = soup.select('tr:nth-of-type(1)')[1]

        if tr != previous_notice:
            notice_title, notice_link = process_table_rows(tr)

            if notice_title and notice_link:
                notice_text = extract_data_from_pdf(notice_link) or email_message.unable_to_fetch_message

                subscribed_users = [user.get('confirmed_email') for user in
                                db.users.find({'confirmed_email': {'$exists': True}})]
                send_mail(notice_title, f'{notice_text}\nDownload this notice: {notice_link}', subscribed_users)
                previous_notice = tr
    except Exception as e:
        logging.error("Error occurs while trying to scrap the webpage: %s", e)


scheduler = BackgroundScheduler({'apscheduler.timezone': 'Asia/Kolkata'})
scheduler.add_job(scrape_notice, trigger='interval', minutes=15)
scheduler.add_job(cleanup_expired_tokens, trigger='cron', hour=3)
scheduler.start()

try:
    while True:
        sleep(60)
except (KeyboardInterrupt, SystemExit):
    scheduler.shutdown()
