# Import the dependencies.
import numpy as np
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

#################################################
# Database Setup
#################################################

engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(autoload_with=engine)
Base.classes.keys()

# Save reference to the table
measurement = Base.classes.measurement
station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################

app = Flask(__name__)

#################################################
# Flask Routes
#################################################

# Welcome page route
@app.route("/")
# List all available api routes
def welcome():
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end>"
    )

# Precipitation data route
@app.route("/api/v1.0/precipitation")
# Return precipitation data of most recent year
def precipitation():
    # Calculate the date one year from the last date in data set.
    last_year = dt.date(2017,8,23) - dt.timedelta(days = 365)

    # Perform a query to retrieve the data and precipitation scores
    precip = session.query(measurement.date, measurement.prcp).filter(measurement.date >= last_year).all()

    # Close Session
    session.close()

    # Convert the query results to a dictionary using "date" as the key and "prcp" as the value
    precip_data = []
    for date, prcp in precip:
        precip_dict = {}
        precip_dict["Date"] = date
        precip_dict["Precipitation"] = prcp
        precip_data.append(precip_dict)

    return jsonify(precip_data)

# Stations route
@app.route("/api/v1.0/stations")
# Return a JSON list of all stations
def stations():
    # Query for a list of all stations
    stations = session.query(station.name).all()

    # Close Session
    session.close()

     # Create a dictionary from the station data and append the list
    station_data = []
    for name, station, elevation, latitude, longitude in stations:
        station_dict = {}
        station_dict["Station ID"] = station
        station_dict["Name"] = name
        station_dict["Latitude"] = latitude
        station_dict["Longitude"] = longitude
        station_dict["Elevation"] = elevation
        station_data.append(station_dict)

    return jsonify(station_data)


# Temperature observation route
@app.route("/api/v1.0/tobs")
# Query the dates and temperature observations of the most-active station for the previous year of data
def tobs():
    # Calculate the date one year from the last date in data set.
    last_year = dt.date(2017,8,23) - dt.timedelta(days = 365)

    # Return a JSON list of temperature observations for the previous year
    tobs = session.query(measurement.tobs).filter(measurement.station == 'USC00519281').filter(measurement.date >= last_year).all()
    
    # Close Session                                                  
    session.close()
    
    # Create a dictionary from the tobs data and append the list
    tobs_data = []
    for date, temp in tobs:
        tobs_dict = {}
        tobs_dict[date] = temp
        tobs_data.append(tobs_dict)

    return jsonify(tobs_data)


# Start range route
@app.route("/api/v1.0/<start>")
# Return a JSON list of the minimum temperature, the average temperature, and the maximum temperature for a specified start or start-end range
def tobs_start(start):
    # For a specified start, calculate TMIN, TAVG, and TMAX for all the dates greater than or equal to the start date
    start_data = session.query(func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).\
                                                                                filter(measurement.date >= start).all()
    
    # Close Session                                                  
    session.close()
    
    # Create a dictionary from the start range data and append the list
    start_date = []
    for min, avg, max in start_data:
        start_dict = {}
        start_dict["Minimum Temperature"] = min
        start_dict["Average Temperature"] = avg
        start_dict["Maxium Temperature"] = max
        start_date.append(start_dict)
        
    return jsonify(start_date)


# Start/End range route
@app.route("/api/v1.0/<start>/<end>")
# Return a JSON list of the minimum temperature, the average temperature, and the maximum temperature for a specified start or start-end range
def tobs_start_end(start, end):
    # For a specified start date and end date, calculate TMIN, TAVG, and TMAX for the dates from the start date to the end date, inclusive
    start_end = session.query(func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).\
                                            filter(measurement.date >= start).filter(measurement.date <= end).all()

    # Close Session                                                  
    session.close()
    
    # Create a dictionary from the start/end range data and append the list
    start_end_date = []
    for min, avg, max in start_end:
        start_end_dict = {}
        start_end_dict["Minimum Temperature"] = min
        start_end_dict["Average Temperature"] = avg
        start_end_dict["Maxium Temperature"] = max
        start_end_date.append(start_end_dict)
        
    return jsonify(start_end_date)

if __name__ == '__main__':
    app.run(debug=True)