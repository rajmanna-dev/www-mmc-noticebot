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

# Mongodb client initialization
client = MongoClient(config.MONGODB_URL)
database = client.mmc_noticebot
users_collection = database.users

previous_notice = None

# SMTP setup
sender_email = config.FROM
password = config.PASSWORD

# Cleanup expired tokens
def cleanup_expired_tokens():
    try:
        expired_cutoff = datetime.now() - timedelta(hours=1)
        users_collection.delete_many({'token_expiration': {'$lt': expired_cutoff}})
    except Exception as e:
        print("Cleanup expired tokens error: ", e)


# Send bulk emails
def send_mail(notice_title, notice_msg, subscribers):
    try:
        global smtp_server
        message = MIMEMultipart()
        message['From'] = sender_email
        message['Subject'] = notice_title
        message.attach(MIMEText(notice_msg, 'plain'))
        message['To'] = ', '.join(subscribers)

        smtp_server = smtplib.SMTP_SSL(config.MAIL_SERVER, 465)
        smtp_server.ehlo()
        smtp_server.login(sender_email, password)
        smtp_server.sendmail(sender_email, subscribers, message.as_string())
        smtp_server.quit()
        print(f"Mail sent from {sender_email} to {subscribers}") # TODO Remove this line of code later
    except smtplib.SMTPException as e:
        print("SMTP Error: ", e)


# Get text from notice pdf
def extract_data_from_pdf(file_link):
    try:
        r = requests.get(file_link)
        with open('temp.pdf', 'wb') as f:
            f.write(r.content)

        with pdfplumber.open("temp.pdf") as pdf:
            pdf_data = ''.join([page.extract_text() for page in pdf.pages])

        os.remove("temp.pdf")
        return pdf_data
    except Exception as e:
        print("Extract data from pdf error: ", e)


# Process the first row of notice table
def process_table_rows(row):
    try:
        notice_title = row.select_one('td:nth-of-type(2)').get_text()
        notice_link = config.DOMAIN + row.select_one('td:nth-of-type(3) a')['href'].replace(' ', '%20')
        return notice_title, notice_link
    except Exception as e:
        print("Process table rows error: ", e)


# Scrape the student notice page
def scrape_notice():
    try:
        url = config.NOTICE_URL
        page = requests.get(url)
        soup = BeautifulSoup(page.content, 'html.parser')
        tr = soup.find_all('tr')[1]  # Get the first row
        print('scraped!')

        global previous_notice
        if tr != previous_notice:
            print('checked!')
            notice_title, notice_link = process_table_rows(tr)
            notice_text = extract_data_from_pdf(notice_link)

            # If notice text is empty
            if not notice_text:
                notice_text = "Unable to fetch notice content."
            subscribed_users = [user.get('confirmed_email') for user in
                                users_collection.find({'confirmed_email': {'$exists': True}})]
            send_mail(notice_title, f"{notice_text}\nDownload this notice: {notice_link}", subscribed_users)
            previous_notice = tr
        else:
            # TODO Remove this line later
            print("Notice already sent!")
    except Exception as e:
        print(f"Scraping section Error: {e}")

scheduler = BackgroundScheduler()
scheduler.configure(timezone='Asia/Kolkata')
scheduler.add_job(scrape_notice, trigger='interval', minutes=30)
scheduler.add_job(cleanup_expired_tokens, trigger='cron', hour=3)
scheduler.start()

try:
    while True:
        sleep(60)
        print('Bot starting...')
except (KeyboardInterrupt, SystemExit):
    try:
        if smtp_server.sock:
            smtp_server.quit()
    except Exception as e:
        print(f"Error while quitting SMTP server: {e}")
    finally:
        scheduler.shutdown()
        client.close()
