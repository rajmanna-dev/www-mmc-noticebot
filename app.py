import re
import os
import logging
import smtplib
from uuid import uuid4
from dotenv import load_dotenv
from pymongo import MongoClient
from flask_talisman import Talisman
from email.mime.text import MIMEText
from datetime import datetime, timedelta
from email.mime.multipart import MIMEMultipart
from email_message import verification_email_content
from flask import Flask, request, render_template, redirect, url_for

load_dotenv()

logging.basicConfig(filename='app.log', level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')

app = Flask(__name__)
app.config['DEBUG'] = os.environ.get('FLASK_ENV') != 'production'
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')

# Talisman(app)  # TODO Uncomment it later

mail_server = os.environ.get('MAIL_SERVER')
mail_port = os.environ.get('MAIL_PORT')
sender_email = os.environ.get('FROM_EMAIL', 'no-replay@gmail.com')
password = os.environ.get('EMAIL_PASSWORD')

email_regex = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b')

mongo_url = os.environ.get('MONGODB_URL')
client = MongoClient(mongo_url)
db = client.mmc_noticebot

db.users.create_index('useremail', unique=True)

def validate_user(username, useremail):
    errors = []
    username = username.strip()
    useremail = useremail.strip().lower()

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
    elif db.users.count_documents({'useremail': useremail}) != 0:
        errors.append('Email already exists')

    return errors


def send_verification_mail(username, useremail, verification_token):
    try:
        message = MIMEMultipart()
        message['From'] = sender_email
        message['To'] = useremail
        message['Subject'] = 'Email Verification Required for Your Account'
        verification_link = url_for('verify_email', token=verification_token, _external=True)
        message.attach(MIMEText(verification_email_content(username, verification_link), 'plain'))

        with smtplib.SMTP_SSL(mail_server, mail_port) as smtp_server:
            smtp_server.login(sender_email, password)
            smtp_server.sendmail(sender_email, useremail, message.as_string())

        return True
    except smtplib.SMTPException as e:
        logging.error("Error occurs while trying to sending email: %s", e)
        return False


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        user_name = request.form['userName'].strip()
        user_email = request.form['userEmail'].strip().lower()
        errors = validate_user(user_name, user_email)
        if errors:
            return render_template('index.html', errors=errors)
        
        verification_token = str(uuid4())
        token_expiration = datetime.now() + timedelta(hours=1)

        try:
            db.users.insert_one({
                'username': user_name,
                'useremail': user_email,
                'verification_token': verification_token,
                'token_expiration': token_expiration
            })
        except errors.DuplicateKeyError:
            errors.append('Email already exists')
            return render_template('index.html', errors=errors)
        except Exception as e:
            logging.error("Error inserting user to DB: %s", e)
            errors.append('An error occurred. Please try again later.')
            return render_template('index.html', errors=errors)
        
        if send_verification_mail(user_name, user_email, verification_token):
            return render_template('index.html', message=True)
        else:
            errors.append('Failed to send verification email.')
            return render_template('index.html', errors=errors)
        
    return render_template('index.html', errors=None, message=False)


@app.route('/verify')
def verify_email():
    token = request.args.get('token')
    if token:
        user = db.users.find_one({'verification_token': token})
        if user and user['token_expiration'] > datetime.now():
            db.users.update_one(
                {'_id': user['_id']},
                {
                    '$unset': {'verification_token': '', 'token_expiration': ''},
                    '$set': {'confirmed_email': user['useremail']}
                })
            return redirect(url_for('subscription_granted'))
        else:
            return redirect(url_for('token_expired'))
    return redirect(url_for('invalid_token'))


@app.route('/blog')
def blog():
    return render_template('blog.html')


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
    return render_template('404.html'), 404