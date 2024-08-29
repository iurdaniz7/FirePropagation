from src.forest_model import ForestModel
from shapely.geometry import Point, Polygon
from shapely.affinity import scale
from app.fire_simulation_app import FireSimulationApp
import matplotlib.pyplot as plt

if __name__ == "__main__":

    # create an initial Shapely area
    center_point = Point(-1.64323, 42.81852)

    # Define an initial square polygon around the center point
    initial_square = Polygon([
        (center_point.x - 0.01, center_point.y - 0.01),
        (center_point.x + 0.01, center_point.y - 0.01),
        (center_point.x + 0.01, center_point.y + 0.01),
        (center_point.x - 0.01, center_point.y + 0.01)
    ])

    # Scale the square polygon to cover approximately 2 square kilometers
    scaling_factor = (1 / initial_square.area) ** 0.5  # Scale to get 2 km^2
    scaled_square = scale(initial_square, xfact=scaling_factor, yfact=scaling_factor)
    forest_areas = [{"name": "Area1",
                     "area": scaled_square,
                     "vegetation": [{"tree": "pine", "tree_density_m": 0.1},
                                    {"tree": "oak", "tree_density_m": 0.1}]}]

    scaling_factor = (0.1 / initial_square.area) ** 0.5
    scaled_square = scale(initial_square, xfact=scaling_factor, yfact=scaling_factor)

    fire_area = [{"name": "Fire_Area1", "area": scaled_square}]
    forest_model = ForestModel(areas=forest_areas,
                               wind_conditions={"speed": 100, "direction": 45},
                               humidity_conditions={"rain": False, "wet": False, "humidity": 60})

    forest_model.initialise_fire(fire_areas=fire_area)
    results = forest_model.run_simulation(simulation_time=100)

    # Optional: plot using matplotlib to visualize the result

    x, y = forest_model.areas[0].area.exterior.xy
    plt.plot(x, y, color="blue")

    # Plot the centroids
    for centroid in results.location:
        plt.plot(centroid.x, centroid.y, "ro")

    plt.gca().set_aspect('equal', adjustable='box')
    plt.savefig("square_centroids.png")

    app = FireSimulationApp(data=results, area=scaled_square)