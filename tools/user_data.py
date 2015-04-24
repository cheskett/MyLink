import sqlite3
import html
import traceback
from tools.login import change_col_db
from flask import Flask, render_template, session, g, current_app as app, url_for
from tools import pictures

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
    friends = []
    requested = []
    requests = []
    try:
        c = db.cursor()
        # friends
        t = (username,)
        c.execute('SELECT user1 FROM friends WHERE user2=? AND status=1', t)
        for row in c:
            friends.append(row[0])
        c.execute('SELECT user2 FROM friends WHERE user1=? AND status=1', t)
        for row in c:
            friends.append(row[0])


        # requests to you
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


def unfriend(username, other, db):
    try:
        c = db.cursor()
        t = (username, other, other, username)
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
        circles = []
        for row in c:
            circles.append(row[0])

        return render_template('circle_page.html', circles=circles, removed=bool1, exists=bool2)
    except sqlite3.OperationalError:
        traceback.print_exc()
    return render_template('circle_page.html', circles=circles)


def circle_create(username, name, db):
    try:
        c = db.cursor()
        t = (name, username,)
        c.execute('SELECT * FROM circles WHERE cname=? AND creator=?', t)
        for row in c:
            return circles_page_db(username, db, False, True)
        c.execute('INSERT INTO circles (cname, creator) VALUES (?,?)', t)
        db.commit()
        return circle_edit(username, name, db, False, False, False)
    except sqlite3.OperationalError:
        traceback.print_exc()
    return circles_page_db(username, db, False, False)


def circle_edit(username, name, db, removed, added, exists):
    friends = []
    friendsc = []
    heldID = -1
    try:
        c = db.cursor()
        t = (name, username,)
        c.execute('SELECT cid FROM circles WHERE cname=? AND creator=?', t)
        for row in c:
            heldID = row[0]
        if heldID == -1:
            print("Fail" + username + " " + name)
            return circles_page_db(username, db, False, False)

        t = (heldID,)
        c.execute('SELECT user From circle_members WHERE cid=?', t)
        # print(c)
        for row in c:
            # print(row)
            friendsc.append(row[0])

        t = (username,)
        c.execute('SELECT user1 FROM friends WHERE user2=? AND status=1', t)
        for row in c:
            friends.append(row[0])
        c.execute('SELECT user2 FROM friends WHERE user1=? AND status=1', t)
        for row in c:
            friends.append(row[0])
        return render_template('circle_edit.html', friends=friends, friendsc=friendsc, circle=name, removed=removed,
                               added=added, exists=exists)
    except sqlite3.OperationalError:
        traceback.print_exc()
    return circles_page_db(username, db, False, False)


def circle_remove(username, name, db):
    heldID = -1
    try:
        c = db.cursor()
        t = (name, username,)
        c.execute('SELECT cid FROM circles WHERE cname=? AND creator=?', t)
        for row in c:
            heldID = row[0]
        if heldID == -1:
            return circles_page_db(username, db, False, False)

        c.execute('DELETE FROM circles WHERE cname=? AND creator=?', t)
        t = (heldID,)
        c.execute('DELETE FROM circle_members WHERE cid=?', t)
        db.commit()
        return circles_page_db(username, db, True, False)
    except sqlite3.OperationalError:
        traceback.print_exc()
    return circles_page_db(username, db, False, False)


def circle_add_f(username, name, circle, db):
    heldID = -1
    test = -1
    try:
        c = db.cursor()
        t = (circle, username,)
        c.execute('SELECT cid FROM circles WHERE cname=? AND creator=?', t)
        for row in c:
            heldID = row[0]
        if heldID == -1:
            # print("FAIL")
            return circles_page_db(username, db, False, False)
        t = (heldID, name,)
        c.execute('SELECT * FROM circle_members WHERE cid=? AND user=?', t)
        for row in c:
            test = 1
        if test == 1:
            return circle_edit(username, circle, db, False, False, True)
        c.execute('INSERT INTO circle_members VALUES (?, ?)', t)
        db.commit()
        return circle_edit(username, circle, db, False, True, False)
    except sqlite3.OperationalError:
        traceback.print_exc()
    return circle_edit(username, circle, db, False, False, False)  # or F, F, T


def circle_remove_f(username, name, circle, db):
    heldID = -1
    test = -1
    try:
        c = db.cursor()
        t = (circle, username,)
        c.execute('SELECT cid FROM circles WHERE cname=? AND creator=?', t)
        for row in c.fetchall():
            heldID = row[0]
        if heldID == -1:
            return circles_page_db(username, db, False, False)
        t = (heldID, name)
        c.execute('SELECT * FROM circle_members WHERE cid=? AND user=?', t)
        for row in c.fetchall():
            test = 1
        if test == -1:
            return circle_edit(username, circle, db, False, False, False)
        c.execute('DELETE FROM circle_members WHERE  cid=? AND user=?', t)
        db.commit()
        return circle_edit(username, circle, db, True, False, False)
    except sqlite3.OperationalError:
        traceback.print_exc()
    return circle_edit(username, circle, db, False, False, False)  # or F, F, T


def your_posts_home(username, db):
    posts = []

    try:
        c = db.cursor()
        d = db.cursor()
        t = (username,)
        c.execute('SELECT postTitle, user, postText, postid FROM Posts WHERE user=?', t)
        for row in c.fetchall():
            pictures = []
            # search for pictures based on postid
            t = (row[3],)
            d.execute('SELECT owner, path From pictures pic INNER JOIN postpictures post on pic.picid=post.picid \
            WHERE post.postid=?', t)
            for stuff in d.fetchall():
                pic = "/images/" + stuff[0] + "/" + stuff[1]
                pictures.append(pic)
            post = (row[0], row[1], row[2], row[3], pictures)
            posts.append(post)
        posts.reverse()
        return render_template('your_posts_home.html', posts=posts)
    except sqlite3.OperationalError:
        traceback.print_exc()
    return render_template('your_posts_home.html', posts=posts)


def friends_posts_home(username, db):
    posts = []
    try:
        c = db.cursor()
        d = db.cursor()
        t = (username,)
        c.execute('SELECT DISTINCT postTitle, user, postText, p.postid  \
                    FROM Posts p \
                    INNER JOIN postTarget pt on p.postid = pt.postid \
                    WHERE cid IN(SELECT cid From circle_members WHERE user=?)', t)
        for row in c.fetchall():
            pictures = []
            # search for pictures based on postid
            t = (row[3],)
            d.execute('SELECT owner, path From pictures pic INNER JOIN postpictures post on pic.picid=post.picid \
            WHERE post.postid=?', t)
            for stuff in d.fetchall():
                pic = "/images/" + stuff[0] + "/" + stuff[1]
                pictures.append(pic)
            post = (row[0], row[1], row[2], pictures)
            posts.append(post)
        posts.reverse()
        return render_template('friends_posts_home.html', posts=posts)
    except sqlite3.OperationalError:
        traceback.print_exc()
    return render_template('friends_posts_home.html', posts=posts)


def create_post_page_db(username, db):
    album = pictures.get_first_user_album()
    pics = pictures.get_pictures(session['username'], album)
    return render_template('post_create_page.html', pictures=pics)


def create_post_db(username, postTitle, postText, db):
    try:
        c = db.cursor()
        t = (username, postTitle, postText,)
        c.execute('INSERT into posts (user, postTitle, postText) VALUES (?,?,?)', t)
        db.commit()
        return your_posts_home(username, db)
    except sqlite3.OperationalError:
        traceback.print_exc()
    return render_template('post_create_page.html')


def remove_post_db(username, postid, db):
    try:
        c = db.cursor()
        t = (postid,)
        c.execute('Delete From postTarget WHERE postid=?', t)
        c.execute('Delete From posts WHERE postid=?', t)
        db.commit()

        return your_posts_home(username, db)
    except sqlite3.OperationalError:
        traceback.print_exc()
    return your_posts_home(username, db)


def edit_post_circles_db(username, postid, db, bool1, bool2):
    circlesAll = []
    circlesActive = []
    try:
        c = db.cursor()
        t = (postid,)
        c.execute('SELECT c.cid, cname From postTarget p INNER JOIN circles c on p.cid = c.cid WHERE postid=?', t)
        for row in c.fetchall():
            circle = (row[0], row[1],)
            circlesActive.append(circle)

        t = (username,)
        c.execute('SELECT cid, cname From circles WHERE creator=?', t)
        for row in c.fetchall():
            circle = (row[0], row[1],)
            circlesAll.append(circle)

        return render_template('post_circles_page.html', circlesAll=circlesAll, circlesActive=circlesActive,
                               postid=postid, removed=bool1, exists=bool2)
    except sqlite3.OperationalError:
        traceback.print_exc()
    return your_posts_home(username, db)


def r_post_circles_db(username, cid, postid, db):
    try:
        c = db.cursor()
        t = (postid, cid,)
        c.execute('DELETE FROM postTarget WHERE postid=? AND cid=?', t)
        db.commit()
        return edit_post_circles_db(username, postid, db, True, False)
    except sqlite3.OperationalError:
        traceback.print_exc()
    return your_posts_home(username, db)


def a_post_circles_db(username, cid, postid, db):
    try:
        c = db.cursor()
        t = (postid, cid,)
        # c.execute('DELETE FROM postTarget WHERE postid=? AND cid=?', t)
        c.execute('Select cid FROM postTarget WHERE postid=? AND cid=?', t)
        for row in c.fetchall():
            return edit_post_circles_db(username, postid, db, False, True)
        c.execute('INSERT INTO postTarget (postid, cid) VALUES (?,?)', t)
        db.commit()
        return edit_post_circles_db(username, postid, db, False, False)
    except sqlite3.OperationalError:
        traceback.print_exc()
    return your_posts_home(username, db)

def change_info_get(username, db):
    info=()
    try:
        c = db.cursor()
        t = (username,)
        c.execute('SELECT age, date, relationship, occupation, education, home, phone, desc FROM users WHERE email=?', t)
        for row in c.fetchall():
            info = info + row
        return render_template('change_user_info_page.html', info=info)
    except sqlite3.OperationalError:
        traceback.print_exc()
    return render_template('change_user_info_page.html', info=info)