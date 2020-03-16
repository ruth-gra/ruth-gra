import os

from flask import Blueprint, render_template, request, redirect, url_for

from models.comment import Comment
from models.topic import Topic
from models.user import User
from models.settings import db
from utils.redis_helper import create_csrf_token, validate_csrf

topic_handlers = Blueprint("topic", __name__)


@topic_handlers.route("/")
def index():
    # check if user is authenticated based on session_token
    session_token = request.cookies.get("session_token")
    user = db.query(User).filter_by(session_token=session_token).first()

    # get topics
    topics = db.query(Topic).all()

    return render_template("topic/index.html", user=user, topics=topics)


@topic_handlers.route("/create-topic", methods=["GET", "POST"])
def topic_create():
    # get current user (author)
    session_token = request.cookies.get("session_token")
    user = db.query(User).filter_by(session_token=session_token, verified=True).first()

    # only logged in users can create a topic
    if not user:
        return redirect(url_for('auth.login'))

    if request.method == "GET":
        csrf_token = create_csrf_token(user.username)

        return render_template("topic/topic_create.html", user=user, csrf_token=csrf_token)

    elif request.method == "POST":
        csrf = request.form.get("csrf")

        if validate_csrf(csrf, user.username):
            title = request.form.get("title")
            text = request.form.get("text")

            # create a Topic object
            topic = Topic.create(title=title, text=text, author=user)

            return redirect(url_for('topic.index'))
        else:
            return "CSRF token is not valid!"


@topic_handlers.route("/topic/<topic_id>", methods=["GET"])
def topic_details(topic_id):
    topic = db.query(Topic).get(int(topic_id))  # get topic from db by ID

    # get current user (author)
    session_token = request.cookies.get("session_token")
    user = db.query(User).filter_by(session_token=session_token).first()

    # get comments for this topic
    comments = db.query(Comment).filter_by(topic=topic).all()

    # START test background tasks (TODO: delete this code later)
    #if os.getenv('REDIS_URL'):
     #   from tasks import get_random_num
      #  get_random_num()
    # END test background tasks

    return render_template("topic/topic_details.html", topic=topic, user=user,
                           csrf_token=create_csrf_token(user.username), comments=comments)


@topic_handlers.route("/topic/<topic_id>/edit", methods=["GET", "POST"])
def topic_edit(topic_id):
    topic = db.query(Topic).get(int(topic_id))  # get topic from db by ID

    # START test background tasks (TODO: delete this code later)
    if os.getenv('REDIS_URL'):
        from utils.email_helper import get_random_num_next
        get_random_num_next()
    # END test background tasks

    if request.method == "GET":
        return render_template("topic/topic_edit.html", topic=topic)

    elif request.method == "POST":
        title = request.form.get("title")
        text = request.form.get("text")

        # get current user (author)
        session_token = request.cookies.get("session_token")
        user = db.query(User).filter_by(session_token=session_token, verified=True).first()

        # check if user is logged in and user is author
        if not user:
            return redirect(url_for('auth.login'))
        elif topic.author.id != user.id:
            return "You are not the author!"
        else:
            # update the topic fields
            topic.title = title
            topic.text = text
            db.add(topic)
            db.commit()

            return redirect(url_for('topic.topic_details', topic_id=topic_id))


@topic_handlers.route("/topic/<topic_id>/delete", methods=["GET", "POST"])
def topic_delete(topic_id):
    topic = db.query(Topic).get(int(topic_id))  # get topic from db by ID

    if request.method == "GET":
        return render_template("topic/topic_delete.html", topic=topic)

    elif request.method == "POST":
        # get current user (author)
        session_token = request.cookies.get("session_token")
        user = db.query(User).filter_by(session_token=session_token, verified=True).first()

        # check if user is logged in and user is author
        if not user:
            return redirect(url_for('auth.login'))
        elif topic.author.id != user.id:
            return "You are not the author!"
        else:  # if user IS logged in and current user IS author
            # delete topic
            db.delete(topic)
            db.commit()
            return redirect(url_for('topic.index'))
