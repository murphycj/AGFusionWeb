import sqlite3
import os
import uuid
import pickle

import agfusion
import jsonpickle
import mpld3
from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash, send_file
import pyensembl

app = Flask(__name__)
app.config.from_object(__name__)

db = agfusion.AGFusionDB(
    '/Users/charlesmurphy/Desktop/Research/AGFusion/AGFusion/data/agfusion.db'
)

app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'vgfusion.db'),
    SECRET_KEY='development key',
    USERNAME='admin',
    PASSWORD='default'
))
app.config.from_envvar('FLASKR_SETTINGS', silent=True)


@app.route('/',methods=['GET','POST'])
def index():
    #if 'gallery_count' not in session:
    #    session['gallery_count']=0

    if 'id' not in session:
        session['id'] = str(uuid.uuid4())

        session['userdata'] = os.path.join(os.path.abspath(os.curdir),'userdata',session['id'])

        if not os.path.exists(session['userdata']):
            os.mkdir(session['userdata'])

    if 'submitfusion' in request.form:

        gene5prime_input = str(request.form['gene5prime'])
        gene3prime_input = str(request.form['gene3prime'])
        loc5prime = str(request.form['loc5prime'])
        loc3prime = str(request.form['loc3prime'])

        genome = str(request.form['genome'])

        if genome=="GRCh38":
            pyensembl_data = pyensembl.EnsemblRelease(84,'human')
        elif genome=="GRCh37":
            pyensembl_data = pyensembl.EnsemblRelease(75,'human')
        else:
            pyensembl_data = pyensembl.EnsemblRelease(84,'mouse')
            gene5prime_input = gene5prime_input.capitalize()
            gene3prime_input = gene3prime_input.capitalize()

        if genome=='none':
            return render_template(
                'index.html',
                inputerror='visible',
                plotdisplay='none',
                inputerrormsg="Select a reference genome",
                gene5prime=gene5prime_input,
                loc5prime=loc5prime,
                gene3prime=gene3prime_input,
                loc3prime=loc3prime
            )

        if request.form['loc5prime']=='':
            return render_template(
                'index.html',
                inputerror='visible',
                plotdisplay='none',
                inputerrormsg="Enter a 5' junction.",
                gene5prime=gene5prime_input,
                loc5prime=loc5prime,
                gene3prime=gene3prime_input,
                loc3prime=loc3prime
            )
        if request.form['loc3prime']=='':
            return render_template(
                'index.html',
                inputerror='visible',
                plotdisplay='none',
                inputerrormsg="Enter a 3' junction.",
                gene5prime=gene5prime_input,
                loc5prime=loc5prime,
                gene3prime=gene3prime_input,
                loc3prime=loc3prime
            )

        try:
            gene5prime = agfusion.Gene(
                gene=gene5prime_input,
                junction=int(loc5prime),
                db=db,
                pyensembl_data=pyensembl_data
            )
        except agfusion.exceptions.GeneIDException:
            return render_template(
                'index.html',
                inputerror='visible',
                plotdisplay='none',
                inputerrormsg="your 5' gene is not valid. Or the reference genome is incorrect.",
                gene5prime=gene5prime_input,
                loc5prime=loc5prime,
                gene3prime=gene3prime_input,
                loc3prime=loc3prime
            )
        except agfusion.exceptions.JunctionException:
            return render_template(
                'index.html',
                inputerror='visible',
                plotdisplay='none',
                inputerrormsg="your 5' gene junction is outside the gene boundaries. Or the reference genome is incorrect.",
                gene5prime=gene5prime_input,
                loc5prime=loc5prime,
                gene3prime=gene3prime_input,
                loc3prime=loc3prime
            )


        try:
            gene3prime = agfusion.Gene(
                gene=gene3prime_input,
                junction=int(loc3prime),
                db=db,
                pyensembl_data=pyensembl_data
            )
        except agfusion.exceptions.GeneIDException:
            return render_template(
                'index.html',
                inputerror='visible',
                plotdisplay='none',
                inputerrormsg="your 3' gene is not valid. Or the reference genome is incorrect.",
                gene5prime=gene5prime_input,
                loc5prime=loc5prime,
                gene3prime=gene3prime_input,
                loc3prime=loc3prime
            )
        except agfusion.exceptions.JunctionException:
            return render_template(
                'index.html',
                inputerror='visible',
                plotdisplay='none',
                inputerrormsg="your 3' gene junction is outside the gene boundaries. Or the reference genome is incorrect.",
                gene5prime=gene5prime_input,
                loc5prime=loc5prime,
                gene3prime=gene3prime_input,
                loc3prime=loc3prime
            )

        fusion = agfusion.Fusion(
            gene5prime=gene5prime,
            gene3prime=gene3prime,
            db=db,
            genome=genome,
            middlestar=True
        )

        fusion.save_transcript_cdna(session['userdata'])
        fusion.save_transcript_cds(session['userdata'])
        fusion.save_proteins(session['userdata'])
        pickle.dump(fusion,open(session['userdata'] + '/fusion.pk','wb'))

        session['name'] = fusion.name

        dict_of_plots, plot_key = fusion.output_to_html()

        session['plot_key'] = plot_key

        return render_template(
            'index.html',
            dict_of_plots=dict_of_plots,
            name=fusion.name,
            inputerror='hidden',
            plotdisplay='visible',
            gene5prime=gene5prime_input,
            loc5prime=loc5prime,
            gene3prime=gene3prime_input,
            loc3prime=loc3prime
        )
    elif 'downloadseq' in request.form:
        if request.form['downloadseq']=='cdna':
            return send_file(session['userdata'] + '/' + session['name'] + '_cdna.fa',as_attachment=True)
        elif request.form['downloadseq']=='cds':
            return send_file(session['userdata'] + '/' + session['name'] + '_cds.fa',as_attachment=True)
        else:
            return send_file(session['userdata'] + '/' + session['name'] + '_protein.fa',as_attachment=True)
    elif 'downloadimage' in request.form:
        fusion = pickle.load(open(session['userdata'] + '/fusion.pk','rb'))

        fusion_key = str(request.form['downloadimage'].split('_')[0])
        image_type = str(request.form['downloadimage'].split('_')[1])

        fusion_name = session['plot_key'][fusion_key]

        image_file = fusion.save_image(
            transcript=fusion_name,
            out_dir=session['userdata'],
            file_type=image_type
        )

        return send_file(image_file, as_attachment=True)
    else:
        return render_template(
            'index.html',
            inputerror='hidden',
            plotdisplay='none',
            gene5prime="",
            gene5loc="",
            gene3prime="",
            gene3loc=""
        )

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

if __name__ == '__main__':
      app.run(host='0.0.0.0', port=80)
