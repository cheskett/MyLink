import traceback
from validate_email import validate_email
from flask import Flask, render_template, session, g, current_app as app, url_for
from itsdangerous import URLSafeSerializer
from tools import mysession
from tools import email
import sqlite3


__author__ = 'Cameron'

# Get Databasedir
MYLOGIN = "smit1618"
DATABASE = 'picture_share.db'
IMAGEPATH = 'images'


def register_user(user, passwd, pass2):
    c = g.db.cursor()
    is_valid = validate_email(user)
    if is_valid & (passwd == pass2):
        tup = (user, passwd, 'N')
        c.execute('INSERT INTO users (email, password, active) \
                                 VALUES (?,?,?)', tup)
        if c.rowcount == 1:
            g.db.commit()
            payload = get_payload_url(user)
            email.send_register_email(user, payload)
            return render_template("email_sent.html", user=user)
        else:
            return render_template('register.html', error='Username already exists')
    else:
        return render_template('register.html', error="Not a valid email address")


def get_serializer(secret_key=None):
    if secret_key is None:
        secret_key = app.config["SECRET_KEY"]
    return URLSafeSerializer(secret_key)


def get_payload_url(user):
    serializer = get_serializer()
    payload = serializer.dumps(user)
    return url_for('activate_user', payload=payload, _external=True)


def send_registration_email(user):
    return


def user_exists(user):
    c = g.db.cursor()
    t = (user,)
    c.execute('SELECT * FROM users  WHERE email=?', t)
    row = c.fetchone()
    if row:
        return True
    return False


def set_user_active(user):
    c = g.db.cursor()
    t = ("Y", user)
    c.execute('UPDATE users SET active = ? WHERE email=?', t)
    g.db.commit()


def check_password(user, passwd, db):
    try:
        conn = db
        c = conn.cursor()

        t = (user,)
        c.execute('SELECT * FROM users  WHERE email=?', t)

        row = stored_password = c.fetchone()
        #conn.close()

        if row:
            stored_password = row[1]
        if stored_password == passwd:
            return "passed"
    except sqlite3.OperationalError:
        traceback.print_exc()

    return "failed"


def create_new_session(user):
    return mysession.create_session(user)


def show_image(form):
    if mysession.check_session(form) != "passed":
        return login_form()

    # Your code should get the user album and picture and verify that the image belongs to this
    # user and this album before loading it

    # username=form["username"].value

    # Read image
    with open(IMAGEPATH + '/user1/test.jpg', 'rb') as content_file:
        content = content_file.read()

    # Send header and image content
    hdr = "Content-Type: image/jpeg\nContent-Length: %d\n\n" % len(content)
    print(hdr + content)


##############################################################
# Define main function.
def login_post(username, password, db):
    if check_password(username, password, db) == "passed":
        # session = create_new_session(username)
        session["username"] = username
        session["string"] = create_new_session(username)
        print(session["username"])
        print(session["string"])
        return render_template("picture_options.html", user=username)
    else:
        return render_template("login.html",
                               login_failed='Yes')


def change_password_db(user, passwd, db):
    try:
        conn = db
        c = conn.cursor()

        t = (passwd,user,)
        c.execute('UPDATE users SET password=? WHERE email=?', t)
        conn.commit()

        #conn.close()
    except sqlite3.OperationalError:
        traceback.print_exc()

