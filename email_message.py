def verification_email_content(username, verification_link):
    return f'''Hello {username},

I hope this message finds you well.

We kindly request your attention to complete the verification process for your email associated with our platform. This step ensures the security and integrity of your account.

Please click on the following link to verify your email (expired after 1 hour):
{verification_link}

Should you encounter any difficulties or have any questions, please do not hesitate to reach out to our support team for assistance.

Thank you for your cooperation.'''
