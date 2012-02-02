import sqlite3
import json
from flask import Flask, g, render_template, request

app = Flask(__name__)
DATABASE = 'data/hmda2009.db'

##########
# DATABASE
##########

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

class Query:
    def freq(_, field, limit):
        return 'select %(field)s, count(*) as "count" from hmda2009 group by %(field)s order by count(*) desc limit %(limit)s' % {'field': field, 'limit': limit}
    def histogram(_, x, bin):
        return 'select round(%(x)s/%(bin)s)*%(bin)s as %(x)s, count(*) as "count" from hmda2009 group by round(%(x)s/%(bin)s)*%(bin)s' % {'x': x, 'bin': bin}
    def matrix(_, x, xbin, y, ybin):
        return 'select round(%(x)s/%(xbin)s)*%(xbin)s as %(x)s, round(%(y)s/%(ybin)s)*%(ybin)s as %(y)s, count(*) as "count" from hmda2009 group by round(%(x)s/%(xbin)s)*%(xbin)s, round(%(y)s/%(ybin)s)*%(ybin)s' % {'x': x, 'xbin': xbin, 'y': y, 'ybin': ybin}

query = Query()

##############
# QUERY ROUTES
##############

@app.route('/')
def hello_world():
    return 'hello'

# queries
@app.route('/query/')
def query_reg():
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

@app.route('/query/histogram/<x>/<bin>')
def query_histogramx(x, bin):
    query_string = query.histogram(x, bin)
    result = query_db(query_string)
    return json.dumps(result)

@app.route('/query/matrix/<x>/<xbin>/<y>/<ybin>')
def query_matrix(x, xbin, y, ybin):
    query_string = query.matrix(x, xbin, y, ybin)
    result = query_db(query_string)
    return json.dumps(result)

#############
# VIEW ROUTES
#############

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
    query_string = query.freq(field, limit)
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
