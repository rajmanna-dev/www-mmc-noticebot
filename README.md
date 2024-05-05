# NoticeBot

NoticeBot is a Python application for scraping notices from a student notice page, extracting information from PDF notices, and sending email notifications to subscribed users.

## Features

- **Notice Scraping**: Automatically scrapes the student notice page at regular intervals.
- **PDF Extraction**: Extracts text content from PDF notices linked on the student notice page.
- **Email Notifications**: Sends email notifications to subscribed users with notice content and links.

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/your-username/notice-bot.git
    ```
2. Install dependencies:

    ```pip
    pip install -r requirements.txt
    ```
3. Configure application settings in config.py
4. Run the application:

   ```python
   python main.py
```