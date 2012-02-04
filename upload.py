import os
from flask import Flask, session, escape, flash, request, render_template, redirect, url_for, send_from_directory
from werkzeug import secure_filename

UPLOAD_FOLDER = '/var/uploads'
ALLOWED_EXTENSIONS = set(['txt','pdf','png','jpg','jpeg','gif']) 

app = Flask(__name__)
app.secret_key = 'this is supposed to be secret but its obviously not'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['parameter_storage_class'] = UPLOAD_FOLDER

########
# UPLOAD
########

def allowed_file(filename):
    return '.' in filename and \
            filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename)

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files['file']
        print file
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            flash('uploaded: ' + url_for('uploaded_file', filename=filename))
        return redirect(url_for('show_flashes'))
          
    return render_template('upload.html')
    return '''
    '''

@app.route('/flash')
def show_flashes():
    return render_template('flash.html')

############
# INITIALIZE
############

if __name__ == '__main__':
    app.debug = True
    app.run()
