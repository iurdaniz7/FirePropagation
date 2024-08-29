from mesa import Agent
import math
import random


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

    def calculate_heat_intensity(self, source, target, wind_strength, wind_direction):

        # Distance between source and target
        distance = source.distance(target)

        # Calculate direction from source to target
        dx = target.x - source.x
        dy = target.y - source.y
        angle_to_target = math.degrees(math.atan2(dy, dx))

        # Calculate the angular difference between wind direction and direction to target
        angle_diff = (wind_direction - angle_to_target + 360) % 360
        angle_diff = min(angle_diff, 360 - angle_diff)

        # Model heat intensity decay
        distance_decay = math.exp(-distance / wind_strength)

        # Model angular influence (higher intensity in wind direction)
        angular_influence = max(0, math.cos(math.radians(angle_diff)))

        # Calculate the final heat intensity
        intensity = wind_strength * distance_decay * angular_influence

        return intensity

    def step(self):

        self.step_count = self.model.step_count

        if self.is_burned:
            return

        if self.on_fire:

            self.current_time_on_fire += 1

            if self.current_time_on_fire < 2:
                self.color = "yellow"
            elif self.current_time_on_fire < 4:
                self.color = "orange"
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
                         for this_tree in self.model.schedule.agents if this_tree.on_fire]

            if sum(intensity) < 30:
                probability = 0
            elif sum(intensity) < 100:
                probability = 0.9 * sum(intensity)/100
            else:
                probability = 0.9

            self.on_fire = (random.random() < probability)

            if self.on_fire:
                print(f"{self.unique_id} set on fire at time {self.model.step_count}")


