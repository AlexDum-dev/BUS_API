from pathlib import Path
from fastapi import FastAPI
from fastapi.encoders import jsonable_encoder
import mysql.connector
import os
from dotenv import load_dotenv

dotenv_path=Path('./venv/.env')
load_dotenv(dotenv_path=dotenv_path)

dbBlablabus = mysql.connector.connect(
    host="localhost",
    user=os.getenv('userDB'),
    password=os.getenv('passwordDB'),
    database="Blablabus"
)
dbBlablabusCursor = dbBlablabus.cursor()
app = FastAPI()


#Format d'appel : http://127.0.0.1:8000/blablabus/?fromDest=XXX&toDest=XXX&dateTrip=AAAA-MM-JJ
#Example d'appel : http://127.0.0.1:8000/blablabus/?fromDest=XPB&toDest=QJZ&dateTrip=2022-04-01

@app.get("/blablabus/")
def say_hello(fromDest: str, toDest: str, dateTrip: str):
    dbBlablabusCursor.execute("SELECT st1.trip_id "
                              "FROM  StopsTime st1 "
                              "INNER JOIN StopsTime st2 ON st1.trip_id = st2.trip_id "
                              "WHERE st1.stop_id=(%s) AND st2.stop_id=(%s) AND st1.arrival_time < st2.arrival_time",
                              (fromDest, toDest))

    possiblesTrips = dbBlablabusCursor.fetchall()
    res = list()
    for trip in possiblesTrips:
        dbBlablabusCursor.execute(
            "SELECT StopsTime.trip_id, Trip.service_id, Route.route_id, Route.route_long_name from Trip JOIN   StopsTime ON StopsTime.trip_id = Trip.trip_id JOIN Service ON Trip.service_id = Service.service_id JOIN Route ON Trip.route_id = Route.route_id WHERE Service.startDate <= (%s) AND StopsTime.trip_id=(%s)",
            (dateTrip, trip[0]))

        desc = dbBlablabusCursor.description
        column_names = [col[0] for col in desc]
        data = [dict(zip(column_names, row))
                for row in dbBlablabusCursor.fetchall()]
        res.append(data)

    return jsonable_encoder(res)
