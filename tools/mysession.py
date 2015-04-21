#!/usr/bin/python

# Import the CGI, string, sys modules
import cgi, string, sys, os, re, random
import cgitb;

cgitb.enable()  # for troubleshooting
import sqlite3
from flask import current_app as app, g, session


def create_session(user):
    # Store random string as session number
    # Number of characters in session string
    n = 20
    char_set = string.ascii_uppercase + string.digits
    sess = str(''.join(random.sample(char_set, n)))

    conn = sqlite3.connect(app.config['DATABASE'])
    c = conn.cursor()

    # Try to get old session
    t = (user,)
    c.execute('SELECT * FROM sessions  WHERE user=?', t)
    row = c.fetchone()
    if not row:
        # No session for this user. Create one
        s = (user, sess)
        c.execute('INSERT INTO sessions VALUES (?,?)', s)
    else:
        # Update current session
        s = (sess, user)
        c.execute('UPDATE sessions  SET session =? WHERE user =?', s)

    conn.commit()
    conn.close()

    return sess


def check_session():
    if 'username' in session and 'string' in session:
        username = session['username']
        sess = session['string']
        session_stored = read_session_string(username)
        if session_stored == sess:
            return "passed"

    return "failed"


def read_session_string(user):
    # conn = sqlite3.connect(app.config['DATABASE'])
    c = g.db.cursor()  # conn.cursor()

    # Try to get old session
    t = (user,)
    c.execute('SELECT * FROM sessions  WHERE user =?', t)
    row = c.fetchone()
    # conn.close()

    if not row:
        return 'no session'

    return row[1]


def logout(user):
    # conn = sqlite3.connect(app.config['DATABASE'])
    c = g.db.cursor()  # conn.cursor()

    # Try to get old session
    t = (user,)
    # c.execute('SELECT * FROM sessions  WHERE user =?', t)
    c.execute('DELETE FROM sessions WHERE user =?', t)


