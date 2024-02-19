from flask import Flask, g, render_template, request
import sqlite3

import datetime
from datetime import timedelta

from pprint import pprint


DATABASE = "sales.sqlite"
LATEST_DATE = ""
MIN_YEAR = ""

ORIGIN_TOTAL = "total"
TYPE_TOTAL = "any" 

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

def exec_query(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv


def str_to_date(s):
    # day will be ignored
    year, month = tuple(map(int, s.split('-')))
    return datetime.date(year=year, month=month, day=1)

def date_to_str(d):
    return '%d-%d'%(d.year, d.month)

def create_app():
    app = Flask(__name__)
    
    with app.app_context():
        latest_date, first_date = exec_query("SELECT MAX(date), MIN(date) FROM car_sales_data;", one=True)
        # Day will be ignored
        global LATEST_DATE, MIN_YEAR
        LATEST_DATE = str_to_date(latest_date)
        MIN_YEAR = str_to_date(first_date).year
        print(LATEST_DATE)
    
    return app

app = create_app()


@app.route("/")
@app.route("/overview")
def overview():
    end_date = date_to_str(LATEST_DATE)
    start_date = date_to_str(LATEST_DATE - timedelta(days=365))

    latests = exec_query("select date, location, dollars from car_sales_data where date >= ? and date <= ? order by location, date DESC;", args=(start_date, end_date))


    regions = []
    old_loc = None
    for (date, loc, val) in latests:
        if loc != old_loc:
            regions.append({'name':loc, 'last_date':date, 'sales': []})
            old_loc = loc
        regions[-1]['sales'].append(val)

    canada_idx = 0
    for i, region in enumerate(regions):
        if region['name'] == 'CA':
            canada_idx = i
        region['month_change'] = region['sales'][0] - region['sales'][1]
        region['month_change_pct'] = region['month_change'] / region['sales'][1] * 100
        region['year_change'] = region['sales'][0] - region['sales'][-1]
        region['year_change_pct'] = region['year_change'] / region['sales'][1] * 100
        del region['sales']

    # Re-order so Canada total is first
    temp = regions[canada_idx]
    regions = [temp] + regions[:canada_idx] + regions[canada_idx+1:]

    return render_template("base.html", regions=regions, minYear=MIN_YEAR, maxYear=LATEST_DATE.year)


@app.route("/detailed_data", methods=['POST'])
def detailed_data():
    data = request.json
    start = data['start_date']
    end = data['end_date']
    region = data['region']


    sales = exec_query("select date, dollars, units, cars_dollars, trucks_dollars, na_dollars, overseas_dollars from car_sales_data WHERE location=? AND date >= ? AND date <= ? order by date", args=(region, start, end))

    dates, dollars, units, car_sales, truck_sales, na_sales, overseas_sales  = zip(*sales)


    return {
        'status': 'OK', 
        'dates':dates, 
        'dollars':dollars, 
        'units':units, 
        'trucks':truck_sales,
        'cars':car_sales,
        'na':na_sales,
        'overseas': overseas_sales,
    }





@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()




if __name__=="__main__":
    app.run()
