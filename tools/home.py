__author__ = 'Shade390'
import traceback

from flask import Flask, redirect, render_template, session, g, current_app as app, url_for

import sqlite3
from tools.pictures import get_user_profile_pic, get_profile_pic_path

def home_page(username, db):
    posts = []
    try:
        c = db.cursor()
        d= db.cursor()
        t = (username, username, username,)
        c.execute('SELECT DISTINCT postTitle, user, postText, p.postid  \
                    FROM Posts p \
                    LEFT JOIN postTarget pt on p.postid = pt.postid \
                    OR p.user = ? \
                    WHERE (cid IN(SELECT cid From circle_members WHERE user=?) OR p.user = ?)', t)
        for row in c.fetchall():
            pictures = []
            #search for pictures based on postid
            t= (row[3],)
            d.execute('SELECT owner, path From pictures pic INNER JOIN postpictures post on pic.picid=post.picid \
            WHERE post.postid=?',t)
            for stuff in d.fetchall():
                pic= "/images/" + stuff[0] +"/"+ stuff[1]
                pictures.append(pic)
            profileId = get_user_profile_pic(row[1])
            profile_path = get_profile_pic_path(profileId)
            post = (row[0], row[1], row[2], pictures, profile_path)
            posts.append(post)
        posts.reverse()
        return render_template('posts_home.html', posts=posts)
    except sqlite3.OperationalError:
        traceback.print_exc()
    return render_template('posts_home.html', posts=posts)


