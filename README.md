# NoticeBot

NoticeBot is a Python application for scraping notices from a student notice page, extracting information from PDF notices, and sending email notifications to subscribed users.

## Features

- **Notice Scraping**: Automatically scrapes the student notice page at regular intervals.
- **PDF Extraction**: Extracts text content from PDF notices linked on the student notice page.
- **Email Notifications**: Sends email notifications to subscribed users with notice content and links.

## Installation

1. Clone the repository:

   ```bash
   # Clone the repo
   
   git clone https://github.com/rajmanna-dev/MMC-Notice-Automation.git
    ```
2. Install dependencies:

    ```bash
   # Install all the dependencies
   
    pip install -r requirements.txt
    ```
3. Configure application settings in `config.py`.
4. Run the application:

   ```bash
   # Run the web-app
   python app.py
   
   # Run the bot script
   python bot.py
   ```
   
## Configuration

You need to set up the following configuration parameters in `config.py`:

- `FORM`: Sender email address for sending notifications.
- `PASSWORD`: Sender email password.
- `NOTICE_URL`: URL of the student notice page.
- `DOMAIN`: Domain of the website (e.g., `'https://example.com'`).

## Usage

1. Run the bot using `python bot.py`.
2. The application will scrape the notice page, extract notice content from PDFs, and send email notifications to subscribed users.

## Contributing

Contributions are welcome! If you'd like to contribute to MMC-Notice-Bot, please follow these steps:

1. Fork the repository.
2. Create a new branch (`git checkout -b feature/your-feature-name`).
3. Make your changes.
4. Commit your changes (`git commit -am 'Add new feature'`).
5. Push to the branch (`git push origin feature/your-feature-name`).
6. Create a new Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](license.txt) file for details.

## Credits

MMC Notice Bot was created by Educational Toolkit for Students (ETS).