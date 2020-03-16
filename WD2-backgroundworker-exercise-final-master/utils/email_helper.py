import os
from tasks import send_email_task


def send_email(receiver_email, subject, text):
    if os.getenv('REDIS_URL'):  # basically, if the web app is on Heroku, call the "send email" task
        send_email_task(receiver_email, subject, text)
    else:  # but if you're on localhost, just simulate sending email in the console
        print("You are on localhost, so the email will not be really sent.")
        print("---------------EMAIL MESSAGE----------------")
        print("Email recipient: {}".format(receiver_email))
        print("Subject: {}".format(subject))
        print(text)
        print("---------------EMAIL MESSAGE----------------")
