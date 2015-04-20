__author__ = 'Cameron'
import os
from flask import render_template, current_app as app


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