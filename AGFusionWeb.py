import sqlite3
import os

from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash


def connect_db():
    """Connects to the specific database."""
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv

app = Flask(__name__)
app.config.from_object(__name__)


app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'vgfusion.db'),
    SECRET_KEY='development key',
    USERNAME='admin',
    PASSWORD='default'
))
app.config.from_envvar('FLASKR_SETTINGS', silent=True)

rv = connect_db()

@app.route('/')
def index():
    session['gallery_count']=0
    return render_template('index.html')

@app.route('/gallery')
def gallery():
    return render_template('gallery.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/help')
def help():
    return render_template('help.html')

@app.route('/feedback')
def feedback():
    return render_template('feedback.html')


@app.route('/thanks')
def thanks():
    return render_template('thanks.html')
