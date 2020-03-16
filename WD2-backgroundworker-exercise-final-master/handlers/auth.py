import hashlib
import os
import uuid
from flask import Blueprint, render_template, request, redirect, url_for, make_response

from models.user import User
from models.settings import db
from utils.email_helper import send_email

auth_handlers = Blueprint("auth", __name__)


@auth_handlers.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("auth/login.html")

    elif request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        # get password hash out of password
        password_hash = hashlib.sha256(password.encode()).hexdigest()

        # get user from database by her/his username and password
        user = db.query(User).filter_by(username=username).first()

        if not user:
            return "This user does not exist"
        else:
            # if user exists, check if password hashes match
            if password_hash == user.password_hash:
                user.session_token = str(uuid.uuid4())  # if password hashes match, create a session token
                db.add(user)
                db.commit()

                # save user's session token into a cookie
                response = make_response(redirect(url_for('topic.index')))
                response.set_cookie("session_token", user.session_token)  # you might want to set httponly=True on production

                return response
            else:
                return "Your password is incorrect!"


@auth_handlers.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "GET":
        return render_template("auth/signup.html")

    elif request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        email_address = request.form.get("email-address")
        repeat = request.form.get("repeat")

        if password != repeat:
            return "Passwords do not match! Go back and try again."

        user = User(username=username, password_hash=hashlib.sha256(password.encode()).hexdigest(),
                    session_token=str(uuid.uuid4()), email_address=email_address, verification_token=str(uuid.uuid4()))
        db.add(user)  # add to the transaction (user is not yet in a database)
        db.commit()  # commit the transaction into the database (user is now added in the database)

        # verification email message
        subject = "Verify your email address"
        domain = "{}.herokuapp.com".format(os.getenv("HEROKU_APP_NAME"))  # TODO: set HEROKU_APP_NAME config var on Heroku!
        print("Domain: " + str(domain))
        text = "Hi! Click on this link to verify your email address: {0}/verify-email/{1}".format(domain, user.verification_token)

        # send verification email
        send_email(receiver_email=user.email_address, subject=subject, text=text)

        # save user's session token into a cookie
        response = make_response(redirect(url_for('topic.index')))
        response.set_cookie("session_token", user.session_token)  # you might want to set httponly=True on production

        return response


@auth_handlers.route("/verify-email/<token>", methods=["GET"])
def verify_email(token):
    user = db.query(User).filter_by(verification_token=token).first()

    if user:
        user.verified = True
        db.add(user)
        db.commit()

    return render_template("auth/email_verification_result.html", verified=user.verified)
