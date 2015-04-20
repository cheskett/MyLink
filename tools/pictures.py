__author__ = 'Cameron'
import os
from flask import render_template, current_app as app, session, g


def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS']


def upload_image(file):
    if file and allowed_file(file.filename):
        # Make the filename safe, remove unsupported chars
        filename = file.filename.replace(" ", "_")
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
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