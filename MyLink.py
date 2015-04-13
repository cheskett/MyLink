from flask import Flask
from login import main, login_post
from flask import g, render_template, redirect, url_for, request, session, send_from_directory
import sqlite3
import os, cgi

# config

PROJECT_ROOT = os.path.dirname(os.path.realpath(__file__))
DATABASE = os.path.join(PROJECT_ROOT, 'picture_share.db')
# IMAGEPATH = os.path.join(PROJECT_ROOT, 'images')
IMAGEPATH = 'images/'
DEBUG = True
SECRET_KEY = 'development key'
USERNAME = 'admin'
PASSWORD = 'default'

app = Flask(__name__)
app.config.from_object(__name__)
app.config['UPLOAD_FOLDER'] = BASE_DIR = os.path.dirname(os.path.abspath(__file__)) + '/images'
app.config['ALLOWED_EXTENSIONS'] = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS']


def connect_db():
    return sqlite3.connect(app.config['DATABASE'])


@app.before_request
def before_request():
    g.db = connect_db()


@app.teardown_request
def teardown_request(exception):
    if hasattr(g, 'db'):
        g.db.close()

# @app.route('/')
# def index():
#     return render_template('index.html')

@app.route('/')
def app_login():
    # return main()
    return render_template('login.html')


@app.route('/trylogin', methods=['POST'])
def hello():
    name = request.form['username']
    password = request.form['password']
    return login_post(name, password, g.db)


@app.route('/newalbum')
def new_album():
    return


@app.route('/upload', methods=['POST', 'GET'])
def upload():
    if request.method == "GET":
        return render_template("upload.html")
    else:
        file = request.files['file']
        # Get user
        user = session['username']

        # Check if the file was uploaded
        if file and allowed_file(file.filename):
            # Make the filename safe, remove unsupported chars
            filename = file.filename.replace(" ", "_")
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return render_template("upload_success.html",
                                   filename=filename,
                                   )

        else:
            return 'No file was uploaded'



@app.route('/images/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename)


if __name__ == '__main__':
    app.debug = "True"
    host = "0.0.0.0",
    port = int("80"),
    app.run()
