import pandas as pd
from mesa import Model
from mesa.time import RandomActivation
from src.forest_area_model import ForestArea
from shapely.geometry import Point, Polygon
from multiprocessing import Pool


class ForestModel(Model):

    def __init__(self, areas, wind_conditions, humidity_conditions, trees_per_agent=500):

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
        # # Use Pool to parallelize the stesps of agents
        # with Pool(processes=4) as pool:
        #     agents = list(self.schedule.agents)
        #     pool.map(self._agent_step_wrapper, agents)

        # After parallel step, perform any model-wide updates
        self.schedule.step()

    @staticmethod
    def _agent_step_wrapper(self, agent):
        agent.step()


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
    scaled_square = Polygon([(-1.8602886340206184, 43.03057672253384), (-1.963381417525773, 43.03057672253384), (-2.008484510309278, 43.08113852028664), (-2.1695669845360825, 43.119059868601255), (-2.356422654639175, 43.119059868601255), (-2.3821958505154637, 43.08113852028664), (-2.150237087628866, 42.72720593601698), (-1.956938118556701, 42.701925037140576), (-1.7636391494845358, 42.71456548657878), (-1.5961133762886601, 42.803048632646195), (-1.5252370876288657, 42.87257110455631), (-1.8602886340206184, 43.03057672253384)])
    forest_areas = [{"name": "Area1",
                     "area": scaled_square,
                     "vegetation": [{"tree": "pine", "tree_density_m": 0.1}]}]

    scaling_factor = (0.1 / initial_square.area) ** 0.5
    scaled_square = Polygon([(-2.285546365979381, 43.04321717197204), (-2.0986906958762885, 42.86625087983721), (-2.0729175, 42.92313290230912), (-2.0729175, 43.04321717197204), (-2.285546365979381, 43.04321717197204), (-2.285546365979381, 42.980014924781024), (-2.285546365979381, 43.04321717197204)])

    fire_area = [{"name": "Fire_Area1", "area": scaled_square}]
    forest_model = ForestModel(areas=forest_areas,
                               wind_conditions={"speed": 100, "direction": 45},
                               humidity_conditions={"rain": False, "wet": False, "humidity": 60})

    forest_model.initialise_fire(fire_areas=fire_area)
    results = forest_model.run_simulation(simulation_time=10)

