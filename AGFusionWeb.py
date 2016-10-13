import sqlite3
import os
import uuid
import pickle

import agfusion
import jsonpickle
import matplotlib.pyplot as plt, mpld3
from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash, send_file
import pyensembl

app = Flask(__name__)
app.config.from_object(__name__)

db = agfusion.AGFusionDB(
    '/Users/charlesmurphy/Desktop/Research/AGFusion/AGFusion/agfusion/data/agfusion.db'
)

app.config.update(dict(
    DATABASE=None,
    SECRET_KEY='development key',
    USERNAME='admin',
    PASSWORD='default'
))
app.config.from_envvar('FLASKR_SETTINGS', silent=True)

def check_params(params):

    #check parameters

    if params['dpi']=='':
        params['dpi']='100'
    try:
        params['dpi']=int(params['dpi'])
    except ValueError:
        params['inputerrormsg']="Enter an integer for DPI."
        params['inputerror']='visible'

        return None,render_template('index.html',params=params)

    #check image width

    if params['imagewidth']=='':
        params['imagewidth']='8'

    try:
        params['imagewidth']=int(params['imagewidth'])
    except ValueError:
        params['inputerrormsg']="Enter an integer for image width."
        params['inputerror']='visible'

        return None,render_template('index.html',params=params)

    #check image height

    if params['imageheight']=='':
        params['imageheight']='2'

    try:
        params['imageheight']=int(params['imageheight'])
    except ValueError:
        params['inputerrormsg']="Enter an integer for image height."
        params['inputerror']='visible'

        return None,render_template('index.html',params=params)

    #check scale

    try:
        params['scale']=int(params['scale'])
    except ValueError:
        params['inputerrormsg']="Enter an integer for scale."
        params['inputerror']='visible'

        return None,render_template('index.html',params=params)

    #check font size

    if params['fontsize']=='':
        params['fontsize']='12'

    try:
        params['fontsize']=int(params['fontsize'])
    except ValueError:
        params['inputerrormsg']="Enter an integer for font size."
        params['inputerror']='visible'

        return None,render_template('index.html',params=params)

    return params,None

def check_fusion_input(params):
    #check fusion input

    if params['genome']=='none':

        params['inputerrormsg']="Select a reference genome."
        params['inputerror']='visible'

        return None,render_template('index.html',params=params)

    if request.form['loc5prime']=='':

        params['inputerrormsg']="Enter a 5' junction."
        params['inputerror']='visible'

        return None,render_template('index.html',params=params)

    if request.form['loc3prime']=='':

        params['inputerrormsg']="Enter a 3' junction."
        params['inputerror']='visible'

        return None,render_template('index.html',params=params)

    return params,None

def set_genome(params):

    if params['genome']=="GRCh38":
        pyensembl_data = pyensembl.EnsemblRelease(84,'human')
        params['grch38_color'] = "lightgrey"
    elif params['genome']=="GRCh37":
        pyensembl_data = pyensembl.EnsemblRelease(75,'human')
        params['grch37_color'] = "lightgrey"
    else:
        pyensembl_data = pyensembl.EnsemblRelease(84,'mouse')
        params['gene5prime'] = params['gene5prime'].capitalize()
        params['gene3prime'] = params['gene3prime'].capitalize()
        params['grcm38_color'] = "lightgrey"

    return params, pyensembl_data

@app.route('/',methods=['GET','POST'])
def index():
    #if 'gallery_count' not in session:
    #    session['gallery_count']=0

    params={}
    params['gene5prime'] = ""
    params['gene3prime'] = ""
    params['loc5prime'] = ""
    params['loc3prime'] = ""

    params['grcm38_color'] = "white"
    params['grch37_color'] = "white"
    params['grch38_color'] = "white"


    params['fontsize'] = "12"
    params['dpi'] = "100"
    params['imagewidth'] = "8"
    params['imageheight'] = "2"
    params['scale'] = "0"
    params['genome'] = ""
    params['plotdisplay']='none'
    params['inputerror']='hidden'
    params['optionalparameterdisplay']='none'

    if 'id' not in session:
        session['id'] = str(uuid.uuid4())

        session['userdata'] = os.path.join(os.path.abspath(os.curdir),'userdata',session['id'])

        if not os.path.exists(session['userdata']):
            os.mkdir(session['userdata'])

    if 'submitfusion' in request.form:

        params['gene5prime'] = str(request.form['gene5prime'])
        params['gene3prime'] = str(request.form['gene3prime'])
        params['loc5prime'] = str(request.form['loc5prime'])
        params['loc3prime'] = str(request.form['loc3prime'])

        params['fontsize'] = str(request.form['fontsize'])
        params['dpi'] = str(request.form['dpi'])
        params['imagewidth'] = str(request.form['imagewidth'])
        params['imageheight'] = str(request.form['imageheight'])
        params['scale'] = str(request.form['scale'])
        params['genome'] = str(request.form['genome'])
        params['inputerror']='hidden'

        params, pyensembl_data = set_genome(params)

        params,error = check_fusion_input(params=params)

        if error is not None:
            return error

        params,error = check_params(params=params)
        if error is not None:
            return error

        #try to construct the fusion

        try:
            fusion = agfusion.Fusion(
                gene5prime=params['gene5prime'],
                gene5primejunction=int(params['loc5prime']),
                gene3prime=params['gene3prime'],
                gene3primejunction=int(params['loc3prime']),
                db=db,
                pyensembl_data=pyensembl_data
            )
        except agfusion.exceptions.GeneIDException5prime as e:

            params['inputerrormsg'] = e
            params['inputerror']='visible'
            return render_template('index.html',params=params)

        except agfusion.exceptions.GeneIDException3prime as e:

            params['inputerrormsg'] = e
            params['inputerror'] = 'visible'
            return render_template('index.html',params=params)

        except agfusion.exceptions.JunctionException5prime as e:

            params['inputerrormsg'] = e
            params['inputerror'] = 'visible'
            return render_template('index.html',params=params)

        except agfusion.exceptions.JunctionException3prime as e:

            params['inputerrormsg'] = e
            params['inputerror'] = 'visible'
            return render_template('index.html',params=params)

        except agfusion.exceptions.TooManyGenesException as e:

            params['inputerrormsg'] = e
            params['inputerror'] = 'visible'
            return render_template('index.html',params=params)

        #save the fusion output and visualize

        middlestar=False

        fusion.save_transcript_cdna(out_dir=session['userdata'],middlestar=middlestar)
        fusion.save_transcript_cds(out_dir=session['userdata'],middlestar=middlestar)
        fusion.save_proteins(out_dir=session['userdata'],middlestar=middlestar)
        pickle.dump(fusion,open(session['userdata'] + '/fusion.pk','wb'))

        session['name'] = fusion.name

        dict_of_plots, plot_key = fusion.output_to_html(
            fontsize=params['fontsize'],
            dpi=params['dpi'],
            width=params['imagewidth'],
            height=params['imageheight'],
            scale=params['scale'],
            mpld3=mpld3
        )

        effects = {}
        for name, transcript in fusion.transcripts.items():
            effects[name] = {
                'effect':transcript.effect,
                '5prime_effect':transcript.effect_5prime,
                '3prime_effect':transcript.effect_3prime
            }

        session['plot_key'] = plot_key

        params['plotdisplay'] = 'visible'
        params['name'] = fusion.name

        params['gene5prime'] = params['gene5prime'].upper()
        params['gene3prime'] = params['gene3prime'].upper()

        return render_template(
            'index.html',
            dict_of_plots=dict_of_plots,
            effects=effects,
            params=params
        )

    elif 'downloadseq' in request.form:

        #download sequence data

        if request.form['downloadseq']=='cdna':
            return send_file(session['userdata'] + '/' + session['name'] + '_cdna.fa',as_attachment=True)
        elif request.form['downloadseq']=='cds':
            return send_file(session['userdata'] + '/' + session['name'] + '_cds.fa',as_attachment=True)
        else:
            return send_file(session['userdata'] + '/' + session['name'] + '_protein.fa',as_attachment=True)

    elif 'downloadimage' in request.form:

        params['fontsize'] = str(request.form['fontsize'])
        params['dpi'] = str(request.form['dpi'])
        params['imagewidth'] = str(request.form['imagewidth'])
        params['imageheight'] = str(request.form['imageheight'])
        params['scale'] = str(request.form['scale'])
        params['inputerror']='hidden'
        params['plotdisplay'] = 'visible'

        params,error = check_params(params=params)
        if error is not None:
            return error

        #download image data

        fusion = pickle.load(open(session['userdata'] + '/fusion.pk','rb'))

        fusion_name = str(request.form['image_key'])

        image_file = fusion.save_image(
            transcript=fusion_name,
            out_dir=session['userdata'],
            file_type=str(request.form['downloadimage']),
            fontsize=params['fontsize'],
            dpi=params['dpi'],
            width=params['imagewidth'],
            height=params['imageheight'],
            scale=params['scale']
        )

        return send_file(image_file, as_attachment=True)
    else:

        # default index load

        return render_template('index.html',params=params)

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
