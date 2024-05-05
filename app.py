from flask import Flask, request, render_template
from pymongo import MongoClient
import re

app = Flask(__name__)


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
    success = False
    if request.method == 'POST':
        user_name = request.form['userName'].lower().replace(' ', '')
        user_email = request.form['userEmail'].lower()

        email_regex = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b')
        # Database connection code
        client = MongoClient('localhost', 27017)
        database = client.noticeBot
        users_collection = database.users

        check_errors = validate_user(user_name, user_email, email_regex, users_collection)
        if check_errors:
            client.close()
            return render_template('index.html', errors=check_errors)
        else:
            users_collection.insert_one({'username': user_name, 'useremail': user_email})
            client.close()
            success = True
    return render_template('index.html', errros=None, success=success)


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html')


if __name__ == '__main__':
    app.run(debug=True, host='192.168.0.101', port=8080)
