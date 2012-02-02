import sqlite3
import json
from flask import Flask, g, render_template, request
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
    print 'query> ', query
    cur = g.db.execute(query, args)
    rv = [dict((cur.description[idx][0], value)
               for idx, value in enumerate(row)) for row in cur.fetchall()]
    return (rv[0] if rv else None) if one else rv

def query_matrix_string(x, xbin, y, ybin):
    return 'select round(%(x)s/%(xbin)s)*%(xbin)s as %(x)s, round(%(y)s/%(ybin)s)*%(ybin)s as %(y)s, count(*) as "count" from hmda2009 group by round(%(x)s/%(xbin)s)*%(xbin)s, round(%(y)s/%(ybin)s)*%(ybin)s' % {'x': x, 'xbin': xbin, 'y': y, 'ybin': ybin}

########
# ROUTES
########

@app.route('/')
def hello_world():
    return 'hello'

# queries
@app.route('/query')
def query():
    result = query_db('select * from hmda2009 limit 10')
    return json.dumps(result)

@app.route('/query/tables/')
def query_tables():
    query_string = "SELECT * FROM sqlite_master WHERE type='table'"
    result = query_db(query_string)
    return json.dumps(result)

@app.route('/query/schema/<table>')
def query_schema(table):
    query_string = 'pragma table_info(%s)' % table
    result = query_db(query_string)
    return json.dumps(result)

@app.route('/query/uniq/<field>')
def query_uniqs(field):
    query_string = 'select %(field)s, count(*) from hmda2009 group by %(field)s' % {'field': field}
    result = query_db(query_string)
    return json.dumps(result)

@app.route('/query/histogram/<field>/<bin>')
def query_histogram(field, bin):
    print bin
    query_string = query_matrix_string(x, xbin, y, ybin)
    result = query_db(query_string)
    return json.dumps(result)

@app.route('/query/matrix/<x>/<xbin>/<y>/<ybin>')
def query_matrix(x, xbin, y, ybin):
    query_string = 'select round(%(x)s/%(xbin)s)*%(xbin)s as %(x)s, round(%(y)s/%(ybin)s)*%(ybin)s as %(y)s, count(*) as "count" from hmda2009 group by round(%(x)s/%(xbin)s)*%(xbin)s, round(%(y)s/%(ybin)s)*%(ybin)s' % {'x': x, 'xbin': xbin, 'y': y, 'ybin': ybin}
    result = query_db(query_string)
    return json.dumps(result)

# graphs
@app.route('/bargraph/uniq/<field>')
def graph_uniqs(field):
    query_string = 'select %(field)s, count(*) as "count" from hmda2009 group by %(field)s' % {'field': field}
    result = query_db(query_string)
    data = {
      'query': query_string,
      'field': field,
      'data': result
    }
    return render_template('bargraph.html', data=data)

@app.route('/bargraph/freq/<field>/<limit>')
def graph_freqs(field, limit = 500):
    query_string = 'select %(field)s, count(*) as "count" from hmda2009 group by %(field)s order by count(*) desc limit %(limit)s' % {'field': field, 'limit': limit}
    result = query_db(query_string)
    data = {
      'query': query_string,
      'field': field,
      'data': result
    }
    return render_template('bargraph.html', data=data)

@app.route('/punchcard/<x>/<xbin>/<y>/<ybin>')
def punchcard(x, xbin, y, ybin):
    data = {
      'meta': {
        'x': x, 
        'xbin': xbin, 
        'y': y, 
        'ybin': ybin, 
      }
    }
    return render_template('punchcard.html', data=data)


############
# INITIALIZE
############

if __name__ == '__main__':
    app.debug = True
    app.run()
