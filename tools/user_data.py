import sqlite3
import html
import traceback
from tools.login import change_col_db
from flask import Flask, render_template, session, g, current_app as app, url_for

__author__ = 'Shade390'


def change_user_info(username, form, db):

    age = form['age']
    date = form['date']
    relationship = form['relationship']
    occupation = form['occupation']
    education = form['education']
    desc = form['desc']
    home = form['home']
    phone = form['phone']

    if age:
        print('change age: ' + age)
        change_col_db(username, "age", age, db)
    if date:
        print('change date: ' + date)
        change_col_db(username, "date", date, db)
    if relationship:
        print('change relationship: ' + relationship)
        change_col_db(username, "relationship", relationship, db)
    if occupation:
        print('change occupation: ' + occupation)
        change_col_db(username, "occupation", occupation, db)
    if education:
        print('change education: ' + education)
        change_col_db(username, "education", education, db)
    if desc:
        print('change desc: ' + desc)
        change_col_db(username, "desc", desc, db)
    if home:
        print('change home: ' + home)
        change_col_db(username, "home", home, db)
    if phone:
        print('change phone: ' + phone)
        change_col_db(username, "phone", phone, db)


def friends_data(username, db, bool):
    friends=[]
    requested=[]
    requests=[]
    try:
        c = db.cursor()
        #friends
        t = (username,)
        c.execute('SELECT user1 FROM friends WHERE user2=? AND status=1', t)
        for row in c:
            friends.append(row[0])
        c.execute('SELECT user2 FROM friends WHERE user1=? AND status=1', t)
        for row in c:
            friends.append(row[0])


        #requests to you
        c.execute('SELECT user1 FROM friends WHERE user2=? AND status=0', t)
        for row in c:
            requests.append(row[0])


        #requests from you
        c.execute('SELECT user2 FROM friends WHERE user1=? AND status=0', t)
        for row in c:
            requested.append(row[0])

    except sqlite3.OperationalError:
        traceback.print_exc()
    return render_template('friends_page.html', friends=friends, requests=requests, requested=requested, bool=bool)


def unfriend(username,other, db):
    try:
        c = db.cursor()
        t = (username,other, other, username)
        c.execute('Delete FROM friends WHERE (user1=? AND user2=?) OR (user1=? AND user2=?) ', t)
        db.commit()
        return friends_data(username, db, True)
    except sqlite3.OperationalError:
        traceback.print_exc()
    return friends_data(username, db, False)

def circles_page_db(username, db):
    try:
        c = db.cursor()
        t = (username,)
        c.execute('Select cname From circles WHERE creator=?', t)
        circles=[]
        for row in c:
            circles.append(row[0])

        return render_template('circle_page.html', circles=circles)
    except sqlite3.OperationalError:
        traceback.print_exc()
    return render_template('circle_page.html', circles=circles)


def circle_create(username,name,db):
    return circle_edit(username, name ,db)

def circle_edit(username, name ,db):
    friends=[]
    return render_template('circle_edit.html', friends=friends)

def circle_remove(username,name ,db):
    return 0