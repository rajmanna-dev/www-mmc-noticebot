from flask import Flask, request, render_template
from pymongo import MongoClient
import re

app = Flask(__name__)

client = MongoClient('localhost', 27017)
database = client.noticeBot
users = database.users

errors = []


def validate_user(username, useremail):
    if username == '':
        errors.append('Name is required')
    elif len(username) < 2:
        errors.append('Name must contain at least two characters')

    regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'
    if useremail == '':
        errors.append('Email is required')
    elif not re.match(regex, useremail):
        errors.append('Invalid Email ID')
    return errors


@app.route('/', methods=['GET', 'POST'])
def index():
    warnings = None
    if request.method == 'POST':
        check_errors = validate_user(request.form['userName'], request.form['userEmail'])
        if check_errors:
            warnings = check_errors
        else:
            users.insert_one({'username': request.form['userName'].lower().replace(' ', ''), 'useremail': request.form['userEmail'].lower()})
            print('Inserted!')

    return render_template('index.html', warnings=warnings)


if __name__ == '__main__':
    app.run(debug=True, host='192.168.0.101', port=8080)
