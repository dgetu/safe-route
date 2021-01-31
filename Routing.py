import scipy, json
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns


class Routing:
    radius = 0.004

    def buildCrimeDensity(self, crimeCoords):
        kdTree = scipy.spatial.cKDTree(crimeCoords)

        def crimeDensity(coordinates):
            return kdTree.query_ball_point(
                coordinates, self.radius, workers=-1, return_length=True
            )

        return crimeDensity

if __name__ == "__main__":
    with open("testCoords.json") as file:
        data = json.load(file)
        coordinates = np.array(
            [(float(coord["latitude"]), float(coord["longitude"])) for coord in data]
        )
    crimeDensity = Routing().buildCrimeDensity(coordinates)
    lats = np.linspace(38.9, 39, 25)
    longs = np.linspace(-77.1, -77, 25)
    testData = np.array([[(lat, lon) for lon in longs] for lat in lats])
    testData = np.apply_along_axis(crimeDensity, 2, testData)
    sns.heatmap(testData)
    plt.show()