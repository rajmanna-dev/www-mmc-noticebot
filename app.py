import re
import os
import logging
import smtplib
from uuid import uuid4
from pymongo import MongoClient
from email.mime.text import MIMEText
from datetime import datetime, timedelta
from email.mime.multipart import MIMEMultipart
from email_message import verification_email_content
from flask import Flask, request, render_template, redirect

logging.basicConfig(filename='app.log', level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')

app = Flask(__name__)

if os.environ.get('FLASK_ENV') == 'production':
    app.config['DEBUG'] = False
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
else:
    app.config['DEBUG'] = True


client = MongoClient(os.environ.get('MONGODB_URL'))
database = client.mmc_noticebot
users_collection = database.users
sender_email = os.environ.get('FROM')
password = os.environ.get('PASSWORD')

email_regex = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b')

def validate_user(username, useremail):
    errors = []
    if not username:
        errors.append('Name is required')
    elif len(username) < 3:
        errors.append('Name must contain at least three characters')
    elif len(username) > 255:
        errors.append('Bad input. Name is too long')

    if not useremail:
        errors.append('Email is required')
    elif len(useremail) > 255:
        errors.append('Bad input. Email is too long')
    elif not email_regex.match(useremail):
        errors.append('Invalid Email ID')
    elif users_collection.count_documents({'useremail': useremail.lower()}) != 0:
        errors.append('Email already exists')

    return errors


def send_verification_mail(username, useremail, verification_token):
    try:
        message = MIMEMultipart()
        message['From'] = sender_email
        message['To'] = useremail
        message['Subject'] = 'Email Verification Required for Your Account'
        verification_link = request.url_root + f"verify?token={verification_token}"
        message.attach(MIMEText(verification_email_content(username, verification_link), 'plain'))
        # SMTP Setup
        smtp_server = smtplib.SMTP_SSL(os.environ.get('MAIL_SERVER'), os.environ.get('MAIL_PORT'))
        smtp_server.ehlo()
        smtp_server.login(sender_email, password)
        smtp_server.sendmail(sender_email, useremail, message.as_string())
        smtp_server.quit()
        return True
    except smtplib.SMTPException as e:
        logging.error("Error while sending mail: %s", e)
        return False


@app.route('/', methods=['GET', 'POST'])
def index():
    message = False
    if request.method == 'POST':
        user_name = request.form['userName'].lower().replace(' ', '')
        user_email = request.form['userEmail'].lower()
        check_errors = validate_user(user_name, user_email)
        if check_errors:
            return render_template('index.html', errors=check_errors)
        else:
            verification_token = str(uuid4())
            token_expiration = datetime.now() + timedelta(hours=1)
            users_collection.insert_one({
                'username': user_name,
                'useremail': user_email,
                'verification_token': verification_token,
                'token_expiration': token_expiration
            })
            if send_verification_mail(user_name, user_email, verification_token):
                message = True
    return render_template('index.html', errors=None, message=message)


@app.route('/verify')
def verify_email():
    token = request.args.get('token')
    if token:
        user = users_collection.find_one({'verification_token': token})
        if user and user['token_expiration'] > datetime.now():
            users_collection.update_one(
                {'_id': user['_id']},
                {
                    '$unset': {'verification_token': '', 'token_expiration': ''},
                    '$set': {'confirmed_email': user['useremail']}
                },
                upsert=True
            )
            return redirect('/subscription-granted')
        else:
            return redirect('/token-expired')
    else:
        return redirect('/invalid-token')


@app.route('/subscription-granted')
def subscription_granted():
    return render_template('subscription_granted.html')


@app.route('/token-expired')
def token_expired():
    return render_template('token_expired.html')


@app.route('/invalid-token')
def invalid_token():
    return render_template('invalid_token.html')


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html')