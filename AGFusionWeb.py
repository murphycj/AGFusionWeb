import sqlite3
import os
import uuid

import agfusion
import jsonpickle
import mpld3
from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash, send_file

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
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'

@app.route('/')
def index():
    if 'gallery_count' not in session:
        session['gallery_count']=0

    if 'id' not in session:
        session['id'] = str(uuid.uuid4())

    session['userdata'] = os.path.join(os.path.abspath(os.curdir),'userdata',session['id'])

    if not os.path.exists(session['userdata']):
        os.mkdir(session['userdata'])

    return render_template('index.html')

@app.route('/plot',methods=["GET","POST"])
def plot():

    print session
    if request.method == 'POST':
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
            db=db,
            middlestar=True
        )

        fusion.save_transcript_cdna(session['userdata'])
        fusion.save_transcript_cds(session['userdata'])
        fusion.save_proteins(session['userdata'])

        session['name'] = fusion.name

        dict_of_plots=fusion.output_to_html()

        return render_template('plot.html', dict_of_plots=dict_of_plots, name=fusion.name)
    else:
        if request.environ['QUERY_STRING']=='cdna=':
            return send_file(session['userdata'] + '/' + session['name'] + '_cdna.fa',as_attachment=True)
        elif request.environ['QUERY_STRING']=='cds=':
            return send_file(session['userdata'] + '/' + session['name'] + '_cds.fa',as_attachment=True)
        else:
            return send_file(session['userdata'] + '/' + session['name'] + '_protein.fa',as_attachment=True)

#@app.route('/download')
#def download():
#    return send_file(session['userdata'] + '/protein.fa')

@app.route('/gallery')
def gallery():
    session['gallery_count']+=1
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
