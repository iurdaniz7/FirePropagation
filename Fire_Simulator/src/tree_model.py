from mesa import Agent
import math
import random
from geopy.distance import geodesic
from shapely.geometry import Point
from pyproj import Transformer


class Tree(Agent):

    def __init__(self, unique_id, location, trees_properties, model):

        super().__init__(unique_id, model)

        # Set tree properties
        self.location = location
        self.on_fire = False
        self.is_burned = False
        self.time_lasting_on_fire = 5
        self.time_left_on_fire = 0
        self.current_time_to_fire = 0
        self.current_time_on_fire = 0
        self.step_count = model.step_count
        self.color = "green"
        self.burning_value = 0.01

    @staticmethod
    def calculate_heat_intensity(source, target, wind_strength, wind_direction):

        s = (source.y, source.x)
        t = (target.y, target.x)

        # Calculate the geodesic distance between the two points
        distance = geodesic(s, t).meters

        # Calculate direction from source to target
        dx = target.x - source.x
        dy = target.y - source.y
        angle_to_target = math.degrees(math.atan2(dy, dx))

        # Calculate the angular difference between wind direction and direction to target
        angle_diff = (wind_direction - angle_to_target + 360) % 360
        angle_diff = min(angle_diff, 360 - angle_diff)

        # Constants
        base_intensity = 10000  # Base intensity in W/m^2 (arbitrary unit for initial fire strength)
        humidity_factor = 1 - (50 / 100)  # Fire intensity decreases with higher humidity
        temperature_factor = 1 + (20 - 20) / 100  # Adjust intensity based on temperature (20°C as baseline)
        wind_factor = 1 + (wind_strength / 10)  # Wind increases the spread and intensity of fire
        distance_factor = math.exp(-distance/50)  # Heat intensity decreases exponentially with distance

        # Angular influence (higher intensity in wind direction)
        angular_influence = max(0, math.cos(math.radians(angle_diff)))

        # Area size influence (larger areas on fire will have a more significant impact)
        # area_factor = math.sqrt(area_size / 1000)

        # Calculate the final heat intensity
        heat_intensity = (base_intensity * humidity_factor * temperature_factor * wind_factor *
                          distance_factor * angular_influence)

        return heat_intensity

    def step(self):

        self.step_count = self.model.step_count

        if self.is_burned:
            self.burning_value = 1
            return

        if self.on_fire:

            self.current_time_on_fire += 1
            self.burning_value = 0.1

            if self.current_time_on_fire < 2:
                self.color = "orange"
            elif self.current_time_on_fire < 4:
                self.color = "red"
            else:
                self.color = "red"

            print(f"{self.unique_id} burning at time {self.model.step_count}")

            if self.current_time_on_fire >= self.time_lasting_on_fire:
                self.on_fire = False
                self.is_burned = True
                self.color = "black"
                print(f"{self.unique_id} burned {self.model.step_count}")

        else:
            # get a list of all the trees on fire within a range 0.5
            intensity = [self.calculate_heat_intensity(source=self.location,
                                                       target=this_tree.location,
                                                       wind_strength=self.model.wind_conditions["speed"],
                                                       wind_direction=self.model.wind_conditions["direction"])
                         for this_tree in self.model.schedule.agents if (this_tree.on_fire and
                                                                         this_tree.current_time_on_fire > 0)]

            if sum(intensity) < 30:
                probability = 0
            elif sum(intensity) < 12000:
                probability = 0.8 * sum(intensity)/12000
            else:
                probability = 0.9

            self.on_fire = (random.random() < probability)

            if self.on_fire:
                print(f"{self.unique_id} set on fire at time {self.model.step_count}")


