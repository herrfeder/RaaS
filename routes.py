from flask import Flask,render_template, request, session, flash
import uuid
from werkzeug.datastructures import ImmutableMultiDict
from utility import get_env
import ThreadManager
from flask_bootstrap import Bootstrap
import os
from pandas.io.formats.style import Styler

app = Flask(__name__)
bootstrap = Bootstrap(app)

global df
global env

easystyler = Styler.from_custom_template("templates/tpl", "dataframe_button.tpl")

def get_project_list(argpath=""):

    if not argpath:
        path = "data/db/"
    else:
        path = argpath

    project_files = [x.rstrip(".db") for x in os.listdir("data/db/")]
    return project_files


@app.route('/get_data', methods=['GET', 'POST'])
def get_data():

    global df
    global env
    global df_dict

    df_dict = {}

    datatypes_client = request.form.get('datatype',"")
    load = request.form.get('load',"")

    datatypes = datatypes_client.split(",")

    #df_dict["dftypes"] = [x for x in datatypes]

    for datatype in datatypes:
        env["datatype"] = datatype
        env["dftype"] = datatype
        print(env)
        if load:
            mt = ThreadManager.threadManager.newMergeResults(env, load=True)
            df = mt.do.return_df()
            print(df)
        else:
            pass

    iframe= "/insert_data"

    return render_template( "tablepill.html",
                            leftiframe=iframe,
                            title="RaaS",
                            df_dict = {"blah":"blah"},
                            env=env)

@app.route('/insert_data/<filename>')
def insert_data(filename):
    
    global df
    #### insert data here

    return render_template( "data.html",
                            tables=[easystyler(df).render()],
                            env=env)


@app.route('/change_project')
def change_project():

    global env

    project = request.args.get('project', "")
    env["project"] = project
    print(env)

    return render_template("index.html",
                           env = env)
   


@app.route('/')
@app.route('/index', methods=['GET', 'POST'])
def index():

    global env

    env = get_env("", "")
    env['projectlist'] = get_project_list()
    return render_template('tablepill.html',
                           title='RaaS',
                           #possible_calls=possible_calls,
                           df_dict = {},
                           env=env)




@app.route('/search', methods=['POST'])
def search():
    if 'username' in session:
        username = session['username']
        #flash(username, 'info')
    else:
        return render_template('login.html')
    global result
    iframe = '/PWResults'


    dictSearchQuery = ImmutableMultiDict(request.form).to_dict(flat=True)
    dictSearchQuery = {k: v for k, v in dictSearchQuery.items() if v is not ""}
    del dictSearchQuery['search']
    if 'mode1' in request.form['mode']:
        dictSearchQuery['MODE'] = 'must'
    else:
        dictSearchQuery['MODE'] = 'should'
    del dictSearchQuery['mode']

    sessionID = uuid.uuid4()
    sessionIDHandler.sessionHandler.setSession(sessionID, finishedDownloads.handleDownloads())
    print(str(sessionIDHandler.sessionHandler.getSession(sessionID)))

    es = ThreadManager.threadManager.newThreadESInterfaceDownload(sessionIDHandler.sessionHandler.getSession(sessionID))
    result, totalHits = es.searchFor(dictSearchQuery)
    #change url?

    flash("Whaaaat! You got {} total hits. Wait for the progressbar to fill up.".format(str(totalHits)),"info")
    return render_template('index.html',
                           title='Password DB',
                           ESResult=result,
                           Params=[sessionID,totalHits],
                           iframe=iframe)


@app.route('/getall', methods=['POST'])
def getall():
    if 'username' in session:
        username = session['username']
    else:
        return render_template('login.html')
    global result
    iframe = "/PWResults"
    sessionID = uuid.uuid4()
    sessionIDHandler.sessionHandler.setSession(sessionID, finishedDownloads.handleDownloads())
    print(str(sessionIDHandler.sessionHandler.getSession(sessionID)))

    es = ThreadManager.threadManager.newThreadESInterfaceDownload(sessionIDHandler.sessionHandler.getSession(sessionID))
    result, totalHits = es.searchPasswordsAll()
    print(sessionIDHandler.sessionHandler)
    return render_template('index.html',
                           title='Password DB',
                           ESResult=result,
                           Params=[sessionID, totalHits],
                           iframe=iframe)

@app.route('/PWResults')
def pwResults():
    global result

    view_results = result
    result = ""
    return render_template('PWResults.html', title='Password DB', ESResult=view_results)

@app.route('/ServeResults', methods=['GET'])
def updateStatus():
    if 'username' in session:
        username = session['username']
    else:
        return render_template('login.html')

    servetype = request.args.get('type')

    if servetype == "download":
        sessionID = request.args.get('sessionID')
        downloadHandler = sessionIDHandler.sessionHandler.getSession(sessionID)
        downloadFile = downloadHandler.getFinishedData()
        downloadFile = downloadFile.split("/")[-1]
        return downloadFile
    elif servetype == "copy":
        # read file and return
        pass
        return ""


@app.route('/updateProgress')
def updateProgress():
    if 'username' in session:
        username = session['username']
    else:
        return render_template('login.html')

    sessionID = request.args.get("sessionID")
    progress = sessionIDHandler.sessionHandler.getSession(sessionID)
    if progress != None:
        progress = progress.getProgress()
    else:
        progress = ''
    print(progress)
    return str(progress)

@app.route('/Admin')
def admin():
    if 'username' in session:
        username = session['username']
    else:
        return render_template('login.html')
    return render_template('admin.html', title='Admin Functions')

@app.route('/uploadweb', methods=['POST'])
def uploadWeb():


    return render_template('upload.html', title='Upload Passwords')





@app.route('/uploadfilesystem', methods=['POST'])
def uploadFromFilesystem():
    if 'username' in session:
        username = session['username']
    else:
        return render_template('login.html')

    password = request.form.get('password')

    if u.genMD5Hash(hash) == admin_pwhash:

        es = ThreadManager.threadManager.newThreadPrepareData()
        result = es.processPasswordData()
        flash('Upload initiated!', 'info')
        return render_template('admin.html', title='Upload Passwords')
    else:
        flash('You have to provide the right password!', 'danger')
        return render_template('admin.html', title='Upload Passwords')




@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        session['username'] = request.form['username']
        flash("Login for {} successful. Please be kind to this database. It was created by guys without a clue what they are doing".format(request.form['username']), 'success')
        return index()
    return render_template('/login.html')




# TODO check if user is currently online than set a new user name
@app.route('/logout', methods=['GET','POST'])
def logout():
    # remove the username from teh session if it is there

    username = session.pop('username', None)

    # Need to know the current sessionID

#    del sessionDict[session.sid]
    if username == None:
        flash("You have to login with a name like 'sexy_belzebub' or 'crazy_motherfucker666'".format(username), "info")
    else:
        flash("User {} logout successful. Bye Bye.".format(username), "success")

    return render_template('login.html')


if __name__ =="__main__":
    app.run(host="0.0.0.0", port=5000)
