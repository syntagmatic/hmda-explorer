import json
from flask import Flask, g, render_template, request
from sqlalchemy import create_engine, MetaData, Table

import sys
sys.path.append('lib/')
import jsonh

DATABASE = 'sqlite:///data/hmda2009.db'

app = Flask(__name__)
app.config['DATABASE'] = DATABASE

##########
# DATABASE
##########

engine = create_engine(DATABASE, convert_unicode=True)
metadata = MetaData(bind=engine)

hmda_table = Table('hmda2009', metadata, autoload=True)

@app.before_request
def before_request():
    g.db = engine.connect()

@app.teardown_request
def teardown_request(exception):
    if hasattr(g, 'db'):
        g.db.close()

def query_db(query_string):
    result = []
    for row in g.db.execute(query_string):
        result.append(dict(row.items()))
    return result

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

def dumps(result):
    compact = request.args.get('jsonh', False)
    if compact:
        return jsonh.dumps(result)
    else:
        return json.dumps(result)

# queries
@app.route('/query/')
def query_reg():
    result = query_db('select * from hmda2009 limit 10')
    return dumps(result)

@app.route('/query/tables/')
def query_tables():
    query_string = "SELECT * FROM sqlite_master WHERE type='table'"
    result = query_db(query_string)
    return dumps(result)

@app.route('/query/schema/<table>')
def query_schema(table):
    query_string = 'pragma table_info(%s)' % table
    result = query_db(query_string)
    return dumps(result)

@app.route('/query/uniq/<field>')
def query_uniqs(field):
    query_string = 'select %(field)s, count(*) from hmda2009 group by %(field)s' % {'field': field}
    result = query_db(query_string)
    return dumps(result)

@app.route('/query/histogram/<x>/<bin>')
def query_histogram(x, bin):
    query_string = query.histogram(x, bin)
    result = query_db(query_string)
    return dumps(result)

@app.route('/query/matrix/<x>/<xbin>/<y>/<ybin>')
def query_matrix(x, xbin, y, ybin):
    query_string = query.matrix(x, xbin, y, ybin)
    result = query_db(query_string)
    return dumps(result)

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
    app.run(host='0.0.0.0')
