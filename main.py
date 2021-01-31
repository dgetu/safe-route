import json

import numpy as np
from Routing import CrimeDensityParser, PathGenerator
from flask import Flask, request
import polyline

app = Flask(__name__)
with open("testCoords.json") as file:
        data = json.load(file)
        coordinates = np.array(
            [(float(coord["latitude"]), float(coord["longitude"])) for coord in data]
        )
crimeDensity = CrimeDensityParser().buildCrimeDensity(coordinates)
@app.route('/route', methods=["GET"])
def route():
    if request.method == "GET":
        origin = request.args["origin"]
        destination = request.args["destination"]
        pathGenerator = PathGenerator(origin, destination, crimeDensity)
        path = np.array(pathGenerator.generatePath())
        print(f"via:enc:{polyline.encode(path)}:")