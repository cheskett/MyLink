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

def circles_page_db(username, db, bool1, bool2):
    try:
        c = db.cursor()
        t = (username,)
        c.execute('Select cname From circles WHERE creator=?', t)
        circles=[]
        for row in c:
            circles.append(row[0])

        return render_template('circle_page.html', circles=circles, removed=bool1, exists=bool2)
    except sqlite3.OperationalError:
        traceback.print_exc()
    return render_template('circle_page.html', circles=circles)


def circle_create(username,name,db):
    try:
        c=db.cursor()
        t=(name,username,)
        c.execute('SELECT * FROM circles WHERE cname=? AND creator=?',t)
        for row in c:
            return circles_page_db(username, db, False, True)
        c.execute('INSERT INTO circles (cname, creator) VALUES (?,?)',t)
        db.commit()
        return circle_edit(username, name ,db, False, False, False)
    except sqlite3.OperationalError:
        traceback.print_exc()
    return circles_page_db(username, db, False, False)


def circle_edit(username, name ,db, removed, added, exists):
    friends=[]
    friendsc=[]
    heldID=-1
    try:
        c=db.cursor()
        t=(name,username,)
        c.execute('SELECT cid FROM circles WHERE cname=? AND creator=?',t)
        for row in c:
            heldID=row[0]
        if heldID==-1:
            print("Fail" +  username + " " + name)
            return circles_page_db(username, db, False, False)

        t=(heldID,)
        c.execute('SELECT user From circle_members WHERE cid=?',t)
        #print(c)
        for row in c:
            #print(row)
            friendsc.append(row[0])

        t = (username,)
        c.execute('SELECT user1 FROM friends WHERE user2=? AND status=1', t)
        for row in c:
            friends.append(row[0])
        c.execute('SELECT user2 FROM friends WHERE user1=? AND status=1', t)
        for row in c:
            friends.append(row[0])
        return render_template('circle_edit.html', friends=friends,friendsc=friendsc, circle=name, removed=removed, added=added, exists=exists)
    except sqlite3.OperationalError:
        traceback.print_exc()
    return circles_page_db(username, db, False, False)

def circle_remove(username,name ,db):
    heldID=-1
    try:
        c=db.cursor()
        t=(name,username,)
        c.execute('SELECT cid FROM circles WHERE cname=? AND creator=?',t)
        for row in c:
            heldID=row[0]
        if heldID==-1:
            return circles_page_db(username, db, False, False)

        c.execute('DELETE FROM circles WHERE cname=? AND creator=?',t)
        t=(heldID,)
        c.execute('DELETE FROM circle_members WHERE cid=?',t)
        db.commit()
        return circles_page_db(username, db, True, False)
    except sqlite3.OperationalError:
        traceback.print_exc()
    return circles_page_db(username, db, False, False)

def circle_add_f(username,name, circle ,db):
    heldID=-1
    test=-1
    try:
        c=db.cursor()
        t=(circle,username,)
        c.execute('SELECT cid FROM circles WHERE cname=? AND creator=?',t)
        for row in c:
            heldID=row[0]
        if heldID==-1:
            #print("FAIL")
            return circles_page_db(username, db, False, False)
        t=(heldID, name,)
        c.execute('SELECT * FROM circle_members WHERE cid=? AND user=?',t)
        for row in c:
            test=1
        if test==1:
            return circle_edit(username, circle ,db, False, False, True)
        c.execute('INSERT INTO circle_members VALUES (?, ?)',t)
        db.commit()
        return circle_edit(username, circle ,db, False, True, False)
    except sqlite3.OperationalError:
        traceback.print_exc()
    return circle_edit(username, circle ,db, False, False, False)#or F, F, T

def circle_remove_f(username,name, circle ,db):
    heldID=-1
    test=-1
    try:
        c=db.cursor()
        t=(circle,username,)
        c.execute('SELECT cid FROM circles WHERE cname=? AND creator=?',t)
        for row in c.fetchall():
            heldID=row[0]
        if heldID==-1:
            return circles_page_db(username, db, False, False)
        t=(heldID, name)
        c.execute('SELECT * FROM circle_members WHERE cid=? AND user=?',t)
        for row in c.fetchall():
            test=1
        if test==-1:
            return circle_edit(username, circle ,db, False, False, False)
        c.execute('DELETE FROM circle_members WHERE  cid=? AND user=?',t)
        db.commit()
        return circle_edit(username, circle ,db, True, False, False)
    except sqlite3.OperationalError:
        traceback.print_exc()
    return circle_edit(username, circle ,db, False, False, False)#or F, F, T

def your_posts_home(username,db):
    posts=[]

    try:
        c=db.cursor()
        t=(username,)
        c.execute('SELECT postTitle, user, postText FROM Posts WHERE user=?',t)
        for row in c.fetchall():
            post = (row[0], row[1], row[2])
            posts.append(post)
        return render_template('your_posts_home.html',posts=posts)
    except sqlite3.OperationalError:
        traceback.print_exc()
    return render_template('your_posts_home.html',posts=posts)

def friends_posts_home(username,db):
    posts=[]
    try:
        c=db.cursor()
        t=(username,)
        c.execute('SELECT postTitle, user, postText FROM Posts WHERE postid= ANY(SELECT postid From postTarget \
        WHERE cid= ANY( Select cid From circle_members WHERE user=?))',t)
        for row in c.fetchall():
            post = (row[0], row[1], row[2])
            posts.append(post)
        return render_template('friends_posts_home.html', posts=posts)
    except sqlite3.OperationalError:
        traceback.print_exc()
    return render_template('friends_posts_home.html', posts=posts)

def create_post_db(username,db):
    return render_template('friends_posts_home.html')