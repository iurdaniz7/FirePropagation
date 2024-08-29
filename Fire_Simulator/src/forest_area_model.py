import shapely
from src.tree_model import Tree
from shapely.geometry import Polygon, LineString, Point
from shapely.ops import split
import uuid
import math


class ForestArea:

    def __init__(self, area, trees_per_agent, model):

        self.area_properties = area
        self.number_of_trees = 0
        self.trees_properties = list()
        self.area = area["area"]
        for tree_group in area["vegetation"]:
            self.number_of_trees += (area["area"].area * 1000) ** 2 * tree_group["tree_density_m"]
            self.trees_properties.append(tree_group)

        area_centroids = self.get_centroids(polygon=area["area"],
                                            n=math.ceil(math.sqrt(int(self.number_of_trees / trees_per_agent))),
                                            m=math.ceil(math.sqrt(int(self.number_of_trees / trees_per_agent))))

        self.tree_agents = list()
        for ii, centroid in enumerate(area_centroids):

            # Create Tree agent
            this_three = Tree(unique_id=int(uuid.uuid4()),
                              trees_properties=self.trees_properties,
                              location=centroid,
                              model=model)

            model.schedule.add(this_three)
            self.tree_agents.append(this_three)

    @staticmethod
    def get_centroids(polygon, n, m):
        """
        Split the given polygon into equal parts using `n` horizontal and `m` vertical lines,
        and return the centroids of the resulting polygons.

        :param polygon: The Shapely Polygon to split.
        :param n: Number of horizontal splits.
        :param m: Number of vertical splits.
        :return: List of centroids of the resulting polygons.
        """
        # Get the bounds of the polygon
        minx, miny, maxx, maxy = polygon.bounds
        x_inc = (maxx - minx) / n
        y_inc = (maxy - miny) / m

        centroids = []
        for i in range(0, n):
            for j in range(0, m):
                # Calculate the center of each sub-square
                x_coord = minx + (i + 0.5) * x_inc
                y_coord = miny + (j + 0.5) * y_inc
                point = Point(x_coord, y_coord)

                # Ensure the point is within the original polygon
                centroids.append(point)

        return centroids


