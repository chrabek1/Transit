import requests, json, pymysql, googlemaps
from flask import Flask, request
from datetime import datetime, date

app = Flask(__name__)

con = pymysql.connect('192.168.1.87', 'root','pass','transit')

gmaps = googlemaps.Client(key='AIzaSyDLpDu6ap9FvcBvshtA2I9vF61T1L8ap-0')
api_key='AIzaSyDLpDu6ap9FvcBvshtA2I9vF61T1L8ap-0'

@app.route('/')
def hello_world():
    return 'kierowca ciężarówki'

@app.route('/transits',methods=['POST'])
def transits():
    data = request.json
    source = data['source_address']
    dest = data['destination_address']
    my_dist = gmaps.distance_matrix(str(source),str(dest))['rows'][0]['elements'][0] 
    data['distance']=my_dist['distance']['value']

    sql="INSERT INTO `routes` "
    a=['`'+field+'`' for field in data]
    b=['\''+str(field)+'\'' for field in data.values()]
    sql+='(' + ", ".join(a)+') VALUES (' +", ".join(b) +')'

    with con:
        cur = con.cursor()
        cur.execute(str(sql))
    
    return "chyba sie udalo"

@app.route('/reports/range')
def reports():
    data = request.json
    start_date = data['start_date']
    end_date = data['end_date']
    sql = "SELECT SUM(distance), SUM(price) FROM routes WHERE date>=\"" + str(start_date) + "\" AND date<=\"" + str(end_date) + "\""
    #sql = "SELECT * FROM routes WHERE date>=\"" + str(start_date) + "\" AND date<=\"" + str(end_date) + "\""
    with con:
        cur = con.cursor()
        cur.execute(sql)

        rows = cur.fetchall()
    response={
        "total_distance": str(rows[0][0]),
        "total_price": str(rows[0][1])
    }
    return json.dumps(response)

@app.route('/reports/monthly')
def monthly_reports():
    today = date.today()
    month = date.today().month
    first_day=today.strftime("%Y-%m-0")
    #return str(first_day)
    for d in range(0,today.day):
        day=today.strftime("%Y-%m-d")
        
        sql = "SELECT date, SUM(distance), AVG(distance), AVG(price) FROM routes WHERE date>=\"" + str(first_day) + "\" GROUP BY date"
    with con:
       cur = con.cursor()
       cur.execute(sql)

       rows = cur.fetchall()
    response=[]
    for row in rows:
        d={
            'date': row[0].strftime("%B, %d"),
            'total_distance': str(row[1]),
            'avg_distance': str(row[2]),
            'avg_price': str(row[3])
        }
        response.append(d)
    #return str(rows[0][0])
    return json.dumps(response)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')