# MMC NoticeBot

MMC-NoticeBot is a Flask application for scraping notices from a student notice page, extracting information from PDF notices, and sending email notifications to subscribed users.

## Features

- **Notice Scraping**: Automatically scrapes the student notice page at regular intervals.
- **PDF Extraction**: Extracts text content from PDF notices linked on the student notice page.
- **Email Notifications**: Sends email notifications to subscribed users with notice content and links.

## Installation

1. Clone the repository:

   ```bash
   # Clone the repo

   git clone https://github.com/rajmanna-dev/MMC-NoticeBot.git
   ```

2. Install dependencies:

   ```bash
   # Upgrade pip

   pip install --upgrade pip

   # Install all the dependencies

   python3 -m pip install -r requirements.txt
   ```

3. Configure application settings in `.env` file for environment variables.

4. Run the application:

   ```bash
   # Run the flask app
   python app.py

   # Run the bot script
   python bot.py
   ```

## Configuration

You need to set up the following environment variables parameters in `.env`:

- `DOMAIN`: Domain of the website (e.g., 'http://mmccollege.co.in').
- `NOTICE_URL`: URL of the student notice page (e.g., 'http://mmccollege.co.in/NoticePage/Student%20Notice')
- `FORM_EMAIL`: Sender email address (e.g., example@example.com)
- `EMAIL_PASSWORD`: Sender email password.
- `MAIL_SERVER`: Your mail server (e.g., smtp.gmail.com)
- `MAIL_PORT`: Your mail server port (e.g., 587)
- `MAIL_USE_TLS`: Transport Layer Security (e.g., True or False)
- `FLASK_ENV`: Debug configuration (e.g., development or production)
- `SECRET_KEY`: YOUR_FLASK_SECRET_KEY
- `MONGODB_URL`: YOUR_MONGODB_DATABASE_URL

## Usage

1. Run the app using `python app.py`.
2. Run the bot using `python bot.py`.
3. The application will scrape the notice page, extract notice content from PDFs, and send email notifications to subscribed users.

## Docker Usage

`docker pull rajmannadev/mmc-noticebot-op:<tag>`

`docker-compose up --build -d`

Visit http://localhost:80

## Contributing

Contributions are welcome! If you'd like to contribute to MMC NoticeBot, please follow these steps:

1. Fork the repository.
2. Create a new branch (`git checkout -b feature/your-feature-name`).
3. Make your changes.
4. Commit your changes (`git commit -am 'Add new feature'`).
5. Push to the branch (`git push origin feature/your-feature-name`).
6. Create a new Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](license.txt) file for details.
