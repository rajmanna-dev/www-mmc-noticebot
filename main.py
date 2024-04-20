import os
import smtplib
import requests
import schedule
import pdfplumber
from time import sleep
from bs4 import BeautifulSoup
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import config

previous_notice = []


def send_mail(notice_title, notice_msg, peoples):
    sender_email = config.FROM
    password = config.PASSWORD

    for receiver_email in peoples:
        message = MIMEMultipart()
        message['From'] = sender_email
        message['To'] = receiver_email
        message['Subject'] = notice_title

        body = notice_msg
        message.attach(MIMEText(body, 'plain'))

        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(sender_email, password)
            text = message.as_string()
            server.sendmail(sender_email, receiver_email, text)
            print(f'sent to {receiver_email}')


def extract_data_from_pdf(file_link):
    r = requests.get(file_link)
    with open('temp.pdf', 'wb') as f:
        f.write(r.content)

    with pdfplumber.open("temp.pdf") as pdf:
        text = ''.join([page.extract_text() for page in pdf.pages])

    os.remove("temp.pdf")
    return text


def process_table_rows(row):
    # Notice title
    notice_title = row.select_one('td:nth-of-type(2)').get_text()
    # Notice link
    notice_path = config.DOMAIN + row.select_one('td:nth-of-type(3) a')['href'].replace(' ', '%20')
    return notice_title, notice_path


def scrape_notice():
    url = config.NOTICE_URL
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')
    tr = soup.find_all('tr')[1]

    global previous_notice
    if tr != previous_notice:
        notice_title, notice_link = process_table_rows(tr)
        notice_text = extract_data_from_pdf(notice_link)
        send_mail(notice_title, notice_text, ['rajmanna7734@gmail.com', 'raj9163cu@gmail.com'])
        previous_notice = tr
    else:
        print("Notice already sent!")


if __name__ == '__main__':
    schedule.every().hour.do(scrape_notice)
    while True:
        schedule.run_pending()
        sleep(900)
