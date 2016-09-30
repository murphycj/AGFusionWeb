import sqlite3
import os

import agfusion
import mpld3
from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash

app = Flask(__name__)
app.config.from_object(__name__)

db = agfusion.AGFusionDB(
    '/Users/charlesmurphy/Desktop/Research/AGFusion/AGFusion/data/agfusion.db',
    84,
    'mouse'
)

app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'vgfusion.db'),
    SECRET_KEY='development key',
    USERNAME='admin',
    PASSWORD='default'
))
app.config.from_envvar('FLASKR_SETTINGS', silent=True)

@app.route('/')
def index():
    session['gallery_count']=0
    return render_template('index.html')

@app.route('/plot',methods=["GET","POST"])
def plot():

    #gene5prime = agfusion.Gene(
    #    gene=str(request.form['5primegene']),
    #    junction=int(request.form['5primeloc']),
    #    db=db
    #)

    #gene3prime = agfusion.Gene(
    #    gene=str(request.form['3primegene']),
    #    junction=int(request.form['3primeloc']),
    #    db=db
    #)
    gene5prime = agfusion.Gene(
        gene='ENSMUSG00000022770',
        junction=31684294,
        db=db
    )

    gene3prime = agfusion.Gene(
        gene='ENSMUSG00000002413',
        junction=39648486,
        db=db
    )

    fusion = agfusion.Fusion(
        gene5prime=gene5prime,
        gene3prime=gene3prime,
        db=db
    )

    dict_of_plots=fusion.output_to_html()


    return render_template('plot.html', dict_of_plots=dict_of_plots)

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
