import sqlite3
import traceback
from tools.user_data import your_posts_home
from tools.home import home_page
from tools.pictures import get_user_profile_pic, get_profile_pic_path
from flask import render_template
__author__ = 'Shade390'


#need imae daa
def get_data(username, user, db):
    info = ()
    try:
        c = db.cursor()
        t = (user,)
        c.execute('SELECT email, age, date, relationship, occupation, education, home, phone, desc FROM users WHERE email=?', t)
        picid = get_user_profile_pic(user)
        pic = get_profile_pic_path(picid)
        for row in c.fetchall():
            info=info+row
        return render_template('user_info.html', info=info, pic=pic)
    except sqlite3.OperationalError:
        traceback.print_exc()
    return home_page(username, db)




#none after ------------------------------
def e_post_images(username, postid, db, added, removed, exists):
    try:
        # get images_used
        #get_all_images
        #post_images
        return  #NO Template
    except sqlite3.OperationalError:
        traceback.print_exc()
    return your_posts_home(username, db)

def a_post_images(username, postid, picid, db):
    try:
        c = db.cursor()
        t = (postid, picid,)
        c.execute('SELECT picid FROM postpictures WHERE postid=? AND picid=?', t)
        for row in c.fetchall():
            return e_post_images(username, postid, db, False, False, True)
        c.execute('INSERT INTO postpictures (postid, picid) VALUES (?,?) ', t)
        db.commit()
        return e_post_images(username, postid, db, True, False, False)
    except sqlite3.OperationalError:
        traceback.print_exc()
    return your_posts_home(username, db)

    # if exists (username, postid, db, False, False, True)
    #if added (username, postid, db, True, False, False)
    #return e_post_images


def r_post_images(username, postid, picid, db):
    try:
        c = db.cursor()
        t = (postid, picid,)
        c.execute('DELETE FROM postpictures WHERE postid=? AND picid=?', t)
        db.commit()
        return e_post_images(username, postid, db, False, True, False)
    except sqlite3.OperationalError:
        traceback.print_exc()
    return your_posts_home(username, db)
    # if removed (username, postid, db, False, True, False)
    #return
