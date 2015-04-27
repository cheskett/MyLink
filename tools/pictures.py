__author__ = 'Cameron'
import os
from traceback import print_exc
from flask import render_template, current_app as app, session, g, flash


def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS']


def upload_image(file, album):
    if file and album and allowed_file(file.filename):
        # Make the filename safe, remove unsupported chars
        filename = file.filename.replace(" ", "_")
        savepath = os.path.join(app.config['UPLOAD_FOLDER'], session['username'])
        if not os.path.exists(savepath):
            os.makedirs(savepath)
        file.save(os.path.join(savepath, filename))
        c = g.db.cursor()
        t = (filename, album, session['username'])
        c.execute("INSERT INTO pictures (path, album, owner) VALUES (?,?,?)", t)
        g.db.commit()
        return render_template("upload_success.html",
                               filename=filename)

    else:
        return 'No file was uploaded'


def get_albums():
    user = (session['username'],)
    g.db.row_factory = dict_factory
    c = g.db.cursor()
    sql = "SELECT * FROM albums WHERE owner = ?"
    c.execute(sql, user)
    albums = c.fetchall()
    return albums


def get_pictures(user, album):
    t = (user, album)
    g.db.row_factory = dict_factory
    c = g.db.cursor()
    sql = "SELECT * FROM pictures WHERE owner = ? and album= ?"
    c.execute(sql, t)
    pictures = c.fetchall()
    return pictures


def get_first_user_album():
    t = (session['username'],)
    c = g.db.cursor()
    sql = "SELECT name FROM albums WHERE owner = ?"
    c.execute(sql, t)
    album = c.fetchone()
    album = album[0]
    return album


def create_album(form):
    privacy = form['privacy']
    title = form['title']
    t = (title, session['username'], privacy)
    c = g.db.cursor()
    sql = "INSERT INTO albums (name, owner, visibility) VALUES (?,?,?)"
    try:
        c.execute(sql, t)
        g.db.commit()
        flash("Album created successfully")
    except:
        print_exc()
        flash("Error creating album")


def get_user_profile_pic(username):
    c = g.db.cursor()
    t = (username,)
    sql = "SELECT MAX(picid) FROM pictures WHERE album='Profile Pictures' AND owner = ?"
    c.execute(sql, t)
    data = c.fetchone()
    if data is not None:
        return data[0]
    return None


def get_profile_pic_path(picid):
    c = g.db.cursor()
    t = (picid,)
    sql = "SELECT owner, path FROM pictures WHERE picid = ?"
    c.execute(sql, t)
    data = c.fetchone()
    if data is not None:
        path = os.path.join("/images", data[0], data[1])
        return path
    return None
