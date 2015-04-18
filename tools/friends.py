__author__ = 'Cameron'
from flask import session, g
from tools import mysession, login


def request_friend(friend):
    if mysession.check_session() == 'passed':
        c = g.db.cursor()
        username = session['username']
        data = (username, friend, 0)
        sql = "INSERT INTO friends (user1, user2, status) VALUES(?,?,?)"
        c.execute(sql, data)
        g.db.commit()


