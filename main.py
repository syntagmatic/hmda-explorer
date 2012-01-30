import sqlite3
import json
from flask import Flask, g, render_template
app = Flask(__name__)

##########
# DATABASE
##########

DATABASE = 'data/hmda2009.db'

def connect_db():
    return sqlite3.connect(DATABASE)

@app.before_request
def before_request():
    g.db = connect_db()

@app.teardown_request
def teardown_request(exception):
    if hasattr(g, 'db'):
        g.db.close()

def query_db(query, args=(), one=False):
    cur = g.db.execute(query, args)
    rv = [dict((cur.description[idx][0], value)
               for idx, value in enumerate(row)) for row in cur.fetchall()]
    return (rv[0] if rv else None) if one else rv

########
# ROUTES
########

@app.route('/')
def hello_world():
    return 'hello'

@app.route('/query')
def query():
    result = query_db('select * from hmda2009 limit 10')
    return json.dumps(result)

@app.route('/query/uniq/<field>')
def get_uniqs(field):
    query_string = 'select %(field)s, count(*) from hmda2009 group by %(field)s' % {'field': field}
    print 'query> ', query_string
    result = query_db(query_string)
    return json.dumps(result)

@app.route('/bargraph/uniq/<field>')
def get_uniqs(field):
    query_string = 'select %(field)s, count(*) as "count" from hmda2009 group by %(field)s' % {'field': field}
    print 'graph> ', query_string
    result = query_db(query_string)
    data = {
      'query': query_string,
      'field': field,
      'data': result
    }
    return render_template('bargraph.html', data=data)

############
# INITIALIZE
############

if __name__ == '__main__':
    app.debug = True
    app.run()
