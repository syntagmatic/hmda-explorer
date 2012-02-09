import os
from flask import Flask, session, escape, flash, request, render_template, redirect, url_for, send_from_directory
from flaskext.sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy import desc
from werkzeug import secure_filename

UPLOAD_FOLDER = '/var/uploads'
ALLOWED_EXTENSIONS = set(['db','csv','txt','pdf','png','jpg','jpeg','gif'])

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////var/db/datasets.db'
app.secret_key = 'this is supposed to be secret but its obviously not'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 256 * 1024 * 1024

db = SQLAlchemy(app)

########
# MODELS
########

class Dataset(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(300), unique=False)
    filename = db.Column(db.String(300), unique=True)
    last_modified = db.Column(db.DateTime)

    def __init__(self, filename):
        self.name = filename
        self.filename = filename
        self.last_modified = datetime.utcnow()

    def __repr__(self):
        return '<Dataset %r>' % self.name

#########
# UTILITY
#########

def row2dict(row):
    d = {}
    for col in row.__table__.columns.keys():
        d[col] = getattr(row, col)
    return d

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

@app.route('/uploads/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            dataset = Dataset(filename)
            db.session.add(dataset)
            db.session.commit()
            flash('uploaded: ' + url_for('uploaded_file', filename=filename))
        return redirect(url_for('datasets'))
          
    return render_template('upload.html')
    return '''
    '''

@app.route('/datasets')
def datasets():
    datasets = map(row2dict, Dataset.query.order_by(desc('last_modified')).all())
    print datasets
    return render_template('datasets.html', datasets=datasets)

############
# INITIALIZE
############

if __name__ == '__main__':
    app.debug = True
    app.run()
