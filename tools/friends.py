__author__ = 'Cameron'
from flask import session, g
from tools import mysession, login
import sqlite3


def request_friend(friend):
    if mysession.check_session() == 'passed':
        c = g.db.cursor()
        username = session['username']
        status = entry_exists(username, friend)
        if status == 'none':
            data = (username, friend, 0)
            sql = "INSERT INTO friends (user1, user2, status) VALUES(?,?,?)"
            c.execute(sql, data)
            g.db.commit()
            return False
        elif status == 'accept':
            data = (1, username, friend, friend, username)
            sql = "UPDATE friends SET status = ? WHERE (user1 = ? and user2 = ?) or (user1 = ? and user2 = ?)"
            c.execute(sql, data)
            g.db.commit()
            return True
        elif status == 'friends':
            return True
    return False


def entry_exists(user, friend):
    c = g.db.cursor()
    data = (user, friend)
    query = "SELECT * FROM friends WHERE user1 = ? and user2 = ?"
    c.execute(query, data)
    row = c.fetchone
    if not row:
        data = (friend, user)
        query = "SELECT * FROM friends WHERE user1 = ? and user2 = ?"
        c.execute(query, data)
        row = c.fetchone
        if row:
            return 'accept'
        else:
            return 'none'
    else:
        if row[2] == 1:
            return 'friends'
        else:
            return 'ask'