import pandas as pd
from mesa import Model
from mesa.time import RandomActivation
from src.forest_area_model import ForestArea
from shapely.geometry import Point, Polygon
from shapely.affinity import scale


class ForestModel(Model):

    def __init__(self, areas, wind_conditions, humidity_conditions, trees_per_agent=1000):

        super().__init__()

        self.areas = []
        self.fires = []
        self.tree_agents = []
        self.step_count = 0
        self.wind_conditions = wind_conditions
        self.humidity_conditions = humidity_conditions
        self.schedule = RandomActivation(self)

        # Calculate number of trees
        for area in areas:
            self.areas.append(ForestArea(area=area, trees_per_agent=trees_per_agent, model=self))
            self.tree_agents += self.areas[-1].tree_agents

    def initialise_fire(self, fire_areas):

        # Find tree_agents inside the area:
        for fire in fire_areas:
            self.fires.append(fire)
            for tree_agent in self.tree_agents:
                if tree_agent.location.within(fire["area"]):
                    tree_agent.on_fire = True

        return self.tree_agents

    def run_simulation(self, simulation_time=100):

        results_list = [t_a.__dict__.copy() for t_a in self.tree_agents]
        for t in range(0, simulation_time):
            self.step_count += 1
            self.step()
            results_list = results_list + [t_a.__dict__.copy() for t_a in self.tree_agents]

        # create results dataframe
        simulation_results = pd.DataFrame(results_list)

        print(f"Number of tree_agents burned is "
              f"{len([t for t in self.tree_agents if t.is_burned])}"
              f" of {len(self.tree_agents)}")

        return simulation_results

    def step(self):
        self.schedule.step()


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
    forest_model.run_simulation(simulation_time=100)

