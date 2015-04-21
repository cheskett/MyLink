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
