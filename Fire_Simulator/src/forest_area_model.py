import shapely
from src.tree_model import Tree
from shapely.geometry import Polygon, LineString, Point
from shapely.ops import transform
import uuid
import math
import random
import pyproj


class ForestArea:

    def __init__(self, area, trees_per_agent, model):

        self.area_properties = area
        self.number_of_trees = 0
        self.trees_properties = list()
        self.area = area["area"]
        for tree_group in area["vegetation"]:

            # Define a projection to convert lat/lon to meters (e.g., UTM zone 14N)
            project = pyproj.Transformer.from_crs("EPSG:4326", "EPSG:32614", always_xy=True).transform

            # Reproject the polygon to a coordinate system that uses meters
            projected_polygon = transform(project, area["area"])

            # Calculate the area in square meters
            area_in_square_meters = projected_polygon.area
            self.number_of_trees += area_in_square_meters * tree_group["tree_density_m"]
            self.trees_properties.append(tree_group)

        area_centroids = self.set_random_agent_location(polygon=area["area"],
                                                        n=math.ceil(self.number_of_trees / trees_per_agent))

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

    @staticmethod
    def set_random_agent_location(polygon, n):

        minx, miny, maxx, maxy = polygon.bounds

        point_list = []
        for ii in range(0, n):
            random_point = Point(random.uniform(minx, maxx), random.uniform(miny, maxy))

            if polygon.contains(random_point):
                point_list.append(random_point)

        return point_list


