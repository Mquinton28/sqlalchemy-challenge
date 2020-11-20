# Step two - Climate App
import numpy as np
import re
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from sqlalchemy.sql import exists  

from flask import Flask, jsonify

#DB Connection
engine = create_engine("sqlite:///../sqlalchemy-challenge/Resources/hawaii.sqlite")
Base = automap_base()
Base.prepare(engine, reflect=True)

Station = Base.classes.station
Measurement = Base.classes.measurement

session = Session(engine)

# Now that you have completed your initial analysis, design a Flask API based on the queries that you have just developed.
app = Flask(__name__)

# Create connection

# Home page.
# List all routes that are available.
@app.route("/")
def home():
    print("Server received request for 'Home' page...")
    return(
        f"Available Routes:<br/>"
        f"<br/>"
        f"/api/v1.0/precipitation<br/>"  
        f"/api/v1.0/stations<br/>"
        f"<br/>"
        f"/api/v1.0/tobs<br/>"
        f"<br/>"
        f"/api/v1.0/start<br/>"
        f"<br/>"
        f"/api/v1.0/start/end<br/>"
    )

# /api/v1.0/precipitation
# Convert the query results to a dictionary using date as the key and prcp as the value.
# Return the JSON representation of your dictionary.
@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)

    results = (session.query(Measurement.date, Measurement.tobs)
    .orderby(Measurement.date))

    percp_tobs = []
    for row in results:
        weather_dict = {}
        weather_dict["date"] = row.date
        weather_dict["tobs"] = row.tobs
        percp_tobs.append(weather_dict)

    return jsonify(percp_tobs)

# /api/v1.0/stations
# Return a JSON list of stations from the dataset.
@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)

    results = session.query(Station.name).all()

    station_info = list(np.ravel(results))

    return jsonify(station_info)

# /api/v1.0/tobs
# Query the dates and temperature observations of the most active station for the last year of data.
# Return a JSON list of temperature observations (TOBS) for the previous year.
@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)

    recent_date = (session.query(Measurement.date).order_by(Measurement.date.desc()).first())

    station_list = (session.query(Measurement.station, func.count(Measurement.station)).group_by(Measurement.station).order_by(func.count(Measurement.station).desc()).all())

    hawaii_station = station_list[0][0]
    print(hawaii_station)

    results = (session.query(Measurement.station, Measurement.date, Measurement.tobs).filter(Measurement.date >= recent_date).filter(Measurement.station == hawaii_station).all())

    #Jsonify
    tobs = []
    for result in results:
        tobs_line = {}
        tobs_line['Date'] = result[1]
        tobs_line['Station'] = result[0]
        tobs_line['Tempertature'] = int(result[2])
        tobs.append(tobs_line)

    return jsonify(tobs)

# /api/v1.0/<start> and /api/v1.0/<start>/<end>
# Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.
# When given the start only, calculate TMIN, TAVG, and TMAX for all dates greater than and equal to the start date.
# When given the start and the end date, calculate the TMIN, TAVG, and TMAX for dates between the start and end date inclusive.
@app.route("/api/v1.0/<start>")
def temp(start):
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).order_by(Measurement.date.desc()).all()
    
    for tempertature in results:
        dict = {"Minimum": results[0][0], "Average":results[0][1], "Maximum":results[0][2]}
    return jsonify(dict)

@app.route("/api/v1.0/<start>/<end>")
def tempstartend(start,end):
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start, Measurement.date <= end).order_by(Measurement.date.desc()).all()

    for temperature in results:
        dict = {"Minimum":results[0][0], "Average":results[0][1], "Maximum":results[0][2]}
    return jsonify(dict)
    
if __name__ == '__main__':
    app.run(debug=True)