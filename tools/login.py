import traceback
from validate_email import validate_email
from flask import Flask, render_template, session, g

from tools import mysession
import sqlite3


__author__ = 'Cameron'
app = Flask(__name__)

# Get Databasedir
MYLOGIN = "smit1618"
DATABASE = 'picture_share.db'
IMAGEPATH = 'images'


def register_user(user, passwd, pass2):
    c = g.db.cursor()
    is_valid = validate_email(user, verify=True)
    if is_valid & passwd == pass2:
        tup = (user, passwd, 'N')
        c.execute('INSERT INTO users (?,?,?)', tup)
        if c.rowcount == 1:
            return render_template("email_sent.html", user=user)
        else:
            return render_template('register.html', error='Username already exists')
    else:
        return render_template('register.html', error="Not a valid email address")


def check_password(user, passwd, db):
    try:
        conn = db
        c = conn.cursor()

        t = (user,)
        c.execute('SELECT * FROM users  WHERE email=?', t)

        row = stored_password = c.fetchone()
        conn.close()

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

