# Import the dependencies.
from flask import Flask, jsonify
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, distinct


#################################################
# Database Setup
#################################################

# Create engine
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table
Measurement = Base.classes.measurement

# Create our session (link) from Python to the DB
Session = Session(engine)

#################################################
# Flask Setup
#################################################

app = Flask(__name__)


#################################################
# Flask Routes
#################################################

# Define the root route
@app.route("/")
def welcome():
    return (
        "Welcome to the Hawaii Weather Analysis API!<br/><br/>"
        "Available Routes:<br/>"
        "<a href='/api/v1.0/precipitation'>/api/v1.0/precipitation</a><br/>"
        "<a href='/api/v1.0/stations'>/api/v1.0/stations</a><br/>"
        "<a href='/api/v1.0/tobs'>/api/v1.0/tobs</a><br/>"
    )

# Define the precipitation route
@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session()
    last_date = session.query(func.max(Measurement.date)).scalar()
    last_date = datetime.strptime(last_date, '%Y-%m-%d')
    one_year_ago = last_date - timedelta(days=365)
    prcp_data = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= one_year_ago).all()
    session.close()
    prcp_dict = {date: prcp for date, prcp in prcp_data}
    return jsonify(prcp_dict)

# Define the stations route
@app.route("/api/v1.0/stations")
def stations():
    session = Session()
    station_data = session.query(Measurement.station).distinct().all()
    session.close()
    station_list = [station for station, in station_data]
    return jsonify(station_list)

# Define the temperature observations route
@app.route("/api/v1.0/tobs")
def tobs():
    session = Session()
    last_date = session.query(func.max(Measurement.date)).scalar()
    last_date = datetime.strptime(last_date, '%Y-%m-%d')
    one_year_ago = last_date - timedelta(days=365)
    most_active_station = session.query(Measurement.station).\
        group_by(Measurement.station).\
        order_by(func.count(Measurement.station).desc()).first()[0]
    tobs_data = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.station == most_active_station).\
        filter(Measurement.date >= one_year_ago).all()
    session.close()
    tobs_dict = {date: tobs for date, tobs in tobs_data}
    return jsonify(tobs_dict)

# Run the app
if __name__ == '__main__':
    app.run(debug=True)
