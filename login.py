import cgi, string, sys, os, re, random
import cgitb
import traceback
import mysession
from flask import Flask, render_template, g, session, redirect, url_for

cgitb.enable()  # for troubleshooting
import sqlite3

__author__ = 'Cameron'
app = Flask(__name__)

# Get Databasedir
MYLOGIN = "smit1618"
DATABASE = 'picture_share.db'
IMAGEPATH = 'images'


def login_form():
    html = """

<HTML>
<HEAD>
<TITLE>Info Form</TITLE>
</HEAD>

<BODY BGCOLOR = white>

<center><H2>PictureShare User Administration</H2></center>

<H3>Type User and Password:</H3>

<TABLE BORDER = 0>
<FORM METHOD=post ACTION="/trylogin">
<TR><TH>Username:</TH><TD><INPUT TYPE=text NAME="username"></TD><TR>
<TR><TH>Password:</TH><TD><INPUT TYPE=password NAME="password"></TD></TR>
</TABLE>

<INPUT TYPE=hidden NAME="action" VALUE="login">
<INPUT TYPE=submit VALUE="Enter">
</FORM>
</BODY>
</HTML>
"""
    print_html_content_type()
    print(html)
    return html
    #return render_template("login.html")


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

    #username=form["username"].value

    # Read image
    with open(IMAGEPATH + '/user1/test.jpg', 'rb') as content_file:
        content = content_file.read()

    # Send header and image content
    hdr = "Content-Type: image/jpeg\nContent-Length: %d\n\n" % len(content)
    print(hdr + content)


def print_html_content_type():
    # Required header that tells the browser how to render the HTML.
    print("Content-Type: text/html\n\n")


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

