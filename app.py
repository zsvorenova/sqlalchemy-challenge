# import required libraries
import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

# import Flask and create an app
from flask import Flask, jsonify
app = Flask(__name__)

#Database Setup
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
Base = automap_base()
Base.prepare(engine, reflect=True)
Measurement = Base.classes.measurement
Station = Base.classes.station

# Define what to do when a user hits routes
# index/home route - list all routes available
@app.route("/")
def home():
    print("Server received request for 'Home' page...")
    return (
        f"Welcome to Hawai Climate API!<br/>"
        f"Available Routes<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/2015-10-28<br/>"
        f"/api/v1.0/2015-12-28/2016-01-10"
    )

# precipitation route - query results to dictionary date as key and prcp as values, return json
@app.route("/api/v1.0/precipitation")
def precipitation():
    # create session(link) from Python to the DB
    session = Session(engine)
    # query last 12 months of data
    results = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= '2016-08-23').\
        order_by(Measurement.date).all()
    session.close()
    # create a dictionary from row data and append to a list of percipitation_data
    prcp_data = []
    for date, prcp in results:
        prcp_data.append({date:prcp})

    return jsonify(prcp_data)

# stations route - return json list of stations from the dataset
@app.route("/api/v1.0/stations")
def stations():
    # create session(link) from Python to the DB
    session = Session(engine)
    # list all stations from the database
    sel = [Station.station, Station.name, Station.latitude, Station.longitude, Station.elevation]
    results = session.query(*sel).all()
    session.close()
    # create a dictionary from row data and append to a list
    stations_data = []
    for station, name, latitude, longitude, elevation in results:
        stations_data.append({"station_id": station,
                                "name": name,
                                "latitude": latitude,
                                "longitude": longitude,
                                "elevation": elevation})
    
    return jsonify(stations_data)

# tobs route - query dates and tobs for the most active station for last 12M, return JSON list of tobs
@app.route("/api/v1.0/tobs")
def tobs():
    # create session(link) from Python to the DB
    session = Session(engine)
    # list all stations from the database
    sel = [Measurement.date, Measurement.tobs]
    results = session.query(*sel).\
        filter(Measurement.station=='USC00519281').\
        filter(Measurement.date >= '2016-08-23').all()
    session.close()
    # create a dictionary from row data and append to a list
    temperature =[]
    for date, tobs in results:
        temperature.append({date : tobs})
    
    return jsonify([{"station":"USC00519281", "tobs": temperature}])

# <start> <start>/<end> route - return TMIN, TMAX, and TAVG for the specified period
@app.route("/api/v1.0/<start>")
def query_start(start):
    session = Session(engine)
    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]
    results = session.query(*sel).\
            filter(Measurement.date >= start).all()
    first_date = str(session.query(Measurement.date).order_by(Measurement.date).first())[2:-3]
    last_date = str(session.query(Measurement.date).order_by(Measurement.date.desc()).first())[2:-3]
    session.close()

    for min,avg,max in results:
        min=min
        avg=avg
        max=max

    if (start >= first_date and start <=last_date):
        return jsonify(min_temp=min, avg_temp=avg, max_temp=max)
    
    return (
            f"Start date is not included in the database. Try again!<br/>"
            f"Hint: use the date between {first_date} and {last_date}."
       ), 404
            
@app.route("/api/v1.0/<start>/<end>")
def query_start_end(start, end):
    session = Session(engine)
    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]
    results = session.query(*sel).\
            filter(Measurement.date >= start).filter(Measurement.date <= end).all()
    first_date = str(session.query(Measurement.date).order_by(Measurement.date).first())[2:-3]
    last_date = str(session.query(Measurement.date).order_by(Measurement.date.desc()).first())[2:-3]
    session.close()

    for min,avg,max in results:
        min=min
        avg=avg
        max=max

    if (start >= first_date and start <=last_date) and (end >= first_date and end <=last_date):
        return jsonify(min_temp=min, avg_temp=avg, max_temp=max)
    
    return (
            f"Start or/and end date are not included in the database. Try again!<br/>"
            f"Hint: use the date between {first_date} and {last_date}."
        ), 404


if __name__ == "__main__":
    app.run(debug=True)
