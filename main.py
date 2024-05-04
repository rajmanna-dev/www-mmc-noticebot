import os
import smtplib
import requests
import schedule
import pdfplumber
from time import sleep
from bs4 import BeautifulSoup # type: ignore
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from concurrent.futures import ThreadPoolExecutor

import config

previous_notice = []


# Send bulk mails
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
            print(f'sent to {receiver_email}') # remove this line later
            sleep(5) # sleep for 5 sec


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
    notice_title = row.select_one('td:nth-of-type(2)').get_text() # Get notice title
    notice_path = config.DOMAIN + row.select_one('td:nth-of-type(3) a')['href'].replace(' ', '%20') # Get notice link
    return notice_title, notice_path


# Scrape the student notice page
def scrape_notice():
    url = config.NOTICE_URL
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')
    tr = soup.find_all('tr')[1] # Get the first row

    global previous_notice
    if tr != previous_notice:
        notice_title, notice_link = process_table_rows(tr)
        notice_text = extract_data_from_pdf(notice_link)
        # TODO Emails should be dynamic
        send_mail(notice_title, notice_text, ['rajmanna7734@gmail.com', 'raj9163cu@gmail.com'])
        previous_notice = tr
    else:
        print("Notice already sent!")


# Main
def main():
    with ThreadPoolExecutor(max_workers=2) as executor:
        schedule.every(20).seconds.do(scrape_notice) #NOTE change the time later
        while True:
            schedule.run_pending()
            sleep(5) #NOTE change the time later


if __name__ == '__main__':
    main()
    
