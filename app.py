from flask import Flask, request, render_template
from datetime import datetime, timedelta
from flask_mail import Mail, Message
from pymongo import MongoClient
from uuid import uuid4
import re

import config

app = Flask(__name__)

app.config.update(dict(
    MAIL_SERVER=config.MAIL_SERVER,
    MAIL_PORT=config.MAIL_PORT,
    MAIL_USE_TLS=config.MAIL_USE_TLS,
    MAIL_USERNAME=config.FROM,
    MAIL_PASSWORD=config.PASSWORD,
))

mail = Mail(app)


def validate_user(username, useremail, email_regex, collection_name):
    errors = []
    # Varify username
    if not username:
        errors.append('Name is required')
    elif len(username) < 2:
        errors.append('Name must contain at least two characters')
    # Varify useremail
    if not useremail:
        errors.append('Email is required')
    elif not email_regex.match(useremail):
        errors.append('Invalid Email ID')
    else:
        existing_user = collection_name.find_one({'useremail': useremail.lower()})
        if existing_user:
            errors.append('Email already exists')
    return errors


@app.route('/', methods=['GET', 'POST'])
def index():
    message = ""
    if request.method == 'POST':
        user_name = request.form['userName'].lower().replace(' ', '')
        user_email = request.form['userEmail'].lower()

        email_regex = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b')
        verification_token = str(uuid4())
        token_expiration = datetime.now() + timedelta(hours=1)

        # Database connection code
        client = MongoClient('localhost', 27017)
        database = client.noticeBot
        users_collection = database.users

        check_errors = validate_user(user_name, user_email, email_regex, users_collection)
        if check_errors:
            client.close()
            return render_template('index.html', errors=check_errors)
        else:
            users_collection.insert_one(
                {'username': user_name, 'useremail': user_email, 'verification_token': verification_token, 'token_expiration': token_expiration})
            client.close()
            try:
                msg = Message('Email Verification Required for Your Account', sender=config.FROM,
                              recipients=[user_email])
                verification_link = request.url_root + f"verify?token={verification_token}"
                msg.body = f'''Dear {request.form['userName']},\n\nI hope this message finds you well.\n\nWe kindly request your attention to complete the verification process for your email associated with our platform. This step ensures the security and integrity of your account.\n\nPlease click on the following link to verify your email (expired after 1 hour): {verification_link}\n\nShould you encounter any difficulties or have any questions, please do not hesitate to reach out to our support team for assistance.\n\nThank you for your cooperation.'''
                mail.send(msg)
                message = "An email verification is sent to your email"
            except Exception as e:
                message = "Please try again with another email address"
    return render_template('index.html', errros=None, message=message)


@app.route('/verify')
def verify_email():
    token = request.args.get('token')
    if token:
        # Database connection code
        client = MongoClient('localhost', 27017)
        database = client.noticeBot
        users_collection = database.users

        user = users_collection.find_one({'verification_token': token})
        if user:
            if user.get('token_expiration') and user['token_expiration'] > datetime.now():
                users_collection.update_one({'_id': user['_id']}, {'$unset': {'verification_token': '', 'token_expiration': ''}})
                users_collection.update_one({'_id': user['_id']}, {'$set': {'confirmed_email': user['useremail']}}, upsert=True)
                client.close()
                return "<div style='text-align:center; margin-top: 5rem;'><h1>Email is verified successfully.</h1><br><h2>Thanks for Subscribing Us.</h2></div>"
            else:
                return "<div style='text-align:center; margin-top: 5rem;'><h1>Verification link has expired. </h1><br><h2>Please request a new verification email.</h2></div>"
        else:
            return "<div style='text-align:center; margin-top: 5rem;'><h1>Invalid token or user not found!</h1></div>"
    else:
        return "<div style='text-align:center; margin-top: 5rem;'><h1>Invalid token!</h1></div>"


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html')


if __name__ == '__main__':
    app.run(debug=True, host='192.168.0.101', port=8080)
