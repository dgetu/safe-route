import scipy
import numpy as np


class CrimeDensityParser:
    radius = 0.004

    def buildCrimeDensity(self, crimeCoords):
        kdTree = scipy.spatial.cKDTree(crimeCoords)

        def crimeDensity(coordinates):
            return kdTree.query_ball_point(
                coordinates, self.radius, workers=-1, return_length=True
            )

        return crimeDensity


class PathGenerator:
    lengthWeight = 0
    crimeWeight = 2
    flatCost = 0
    bins = 15
    max_waypoints = 20  # doesnt actually do anything right now

    def __init__(self, src, dest, crimeDensity):
        self.src = src
        self.dest = dest
        self.crimeDensity = crimeDensity
        self.lats = np.linspace(src[0], dest[0], self.bins)
        self.longs = np.linspace(src[1], dest[1], self.bins)
        self.avgCrime = np.average(
            [crimeDensity((lat, lon)) for lat in self.lats for lon in self.longs]
        )
        self.minDistance = self.distance(src, dest)
        self.directCost = 1
        self.directCost = self.directPathCost(self.src, self.dest)

    def distance(self, src, dest):
        return (src[0] - dest[0]) ** 2 + (src[1] - dest[1]) ** 2

    def normalizeCost(self, distance, crime):
        return (
            distance * (self.lengthWeight + self.crimeWeight * crime)
        ) + self.flatCost

    def directPathCost(self, src, dest):
        samples = 20
        crime = np.max(
            [self.crimeDensity(coordinate) for coordinate in zip(self.lats, self.longs)]
        )

        distance = self.distance(src, dest)
        return self.normalizeCost(distance, crime)

    def generatePath(self):
        costMatrix = self.generateCostMatrix()
        predecessors = scipy.sparse.csgraph.shortest_path(
            costMatrix, indices=0, return_predecessors=True
        )[1]
        indices = [224]
        while indices[-1] != 0:
            indices.append(predecessors[indices[-1]])
        waypointIndices = [
            self.costMatrixIndexToIndices(index)[1] for index in reversed(indices)
        ]
        waypoints = [(self.lats[x], self.longs[y]) for x, y in waypointIndices]
        return waypoints

    def costMatrixIndexToIndices(self, index):
        srcLat = (index // self.bins ** 3) % self.bins
        srcLong = (index // self.bins ** 2) % self.bins
        destLat = (index // self.bins) % self.bins
        destLong = index % self.bins
        return ((srcLat, srcLong), (destLat, destLong))

    def generateCostMatrix(self):
        output = np.zeros(self.bins ** 4)
        for i in range(len(output)):
            src, dest = self.costMatrixIndexToIndices(i)
            if src != dest:
                output[i] = self.directPathCost(
                    (self.lats[src[0]], self.longs[src[1]]),
                    (self.lats[dest[0]], self.longs[dest[1]]),
                )
        output = np.reshape(output, (self.bins ** 2, self.bins ** 2))
        return output


if __name__ == "__main__":
    import matplotlib.pyplot as plt
    import seaborn as sns
    import pandas as pd
    import json

    with open("testCoords.json") as file:
        data = json.load(file)
        coordinates = np.array(
            [(float(coord["latitude"]), float(coord["longitude"])) for coord in data]
        )
    crimeDensity = CrimeDensityParser().buildCrimeDensity(coordinates)
    whiteHouse = (38.897957, -77.036560)
    usCapitol = (38.887163118, -77.005333312)
    pathGenerator = PathGenerator(whiteHouse, usCapitol, crimeDensity)
    path = np.array(pathGenerator.generatePath())
    lats = np.linspace(whiteHouse[0], usCapitol[0], 100)
    longs = np.linspace(whiteHouse[1], usCapitol[1], 100)
    testData = np.array([[(lat, lon) for lon in longs] for lat in lats])
    testData = np.apply_along_axis(crimeDensity, 2, testData)
    # sns.heatmap(testData)
    sns.scatterplot(path[:, 1], path[:, 0])
    plt.show()