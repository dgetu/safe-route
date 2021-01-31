import json, polyline, requests, os
import numpy as np
from Routing import CrimeDensityParser, PathGenerator
from flask import Flask, request


app = Flask(__name__)
with open("testCoords.json") as file:
    data = json.load(file)
    coordinates = np.array(
        [(float(coord["latitude"]), float(coord["longitude"])) for coord in data]
    )
crimeDensity = CrimeDensityParser().buildCrimeDensity(coordinates)


@app.route("/route", methods=["GET"])
def route():
    if request.method == "GET":
        origin = request.args["origin"]
        destination = request.args["destination"]
        o = [float(value) for value in origin.split(",")]
        d = [float(value) for value in destination.split(",")]
        pathGenerator = PathGenerator(o, d, crimeDensity)
        path = np.array(pathGenerator.generatePath())[1:-1]
        api_key = os.getenv("API_KEY")
        args = {
            "origin": origin,
            "destination": destination,
            "mode": "walking",
            "waypoints": f"via:enc:{polyline.encode(path)}:",
            "key": os.getenv("API_KEY"),
        }
        directions = requests.get(
            "https://maps.googleapis.com/maps/api/directions/json", params=args
        )
        jsonData = directions.json()
        response = app.response_class(
            response=directions.text, status=200, mimetype="application/json"
        )
        return response
