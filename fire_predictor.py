from mesa import Agent, Model
from mesa.time import RandomActivation
import random
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import math
import numpy as np


class Tree(Agent):
    """An agent with fixed initial wealth."""
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.size = 's'
        self.type = 'eucalyptus'
        self.x = 0
        self.y = 0
        self.on_fire = False
        self.is_burned = False
        self.time_on_fire = 5
        self.steps_left_on_fire = 0
        self.time_to_set_fire = 5
        self.current_time_to_fire = 0
        self.current_time_on_fire = 0

    def calculate_time_will_stay_on_fire(self):

        # type effect
        if self.type == 'oak':
            self.time_on_fire = self.time_to_set_fire + 1
        else:
            self.time_on_fire = self.time_to_set_fire - 1

            # size effect
            if self.size == 's':
                self.time_on_fire = self.time_to_set_fire - 1
            elif self.size == 'l':
                self.time_on_fire = self.time_to_set_fire + 1

        self.current_time_on_fire = self.time_to_set_fire

    def calculate_time_to_set_fire(self):

        # humidity effect
        if self.model.humidity == 'high':
            self.time_to_set_fire = self.time_to_set_fire + 1
        elif self.model.humidity == 'low':
            self.time_to_set_fire = self.time_to_set_fire - 1

        # wind effect
        if self.model.wind == 'strong':
            self.time_to_set_fire = self.time_to_set_fire - 1
        elif self.model.wind == 'weak':
            self.time_to_set_fire = self.time_to_set_fire + 1

        # type effect
        if self.type == 'oak':
            self.time_to_set_fire = self.time_to_set_fire + 2
        else:
            self.time_to_set_fire = self.time_to_set_fire - 1

        # size effect
        if self.size == 's':
            self.time_to_set_fire = self.time_to_set_fire - 1
        elif self.size == 'l':
            self.time_to_set_fire = self.time_to_set_fire + 1

        self.current_time_to_fire = self.time_to_set_fire

    def step(self):

        if self.on_fire is False:
            # the tree will set on fire depending environmental conditions:
            radius = 5

            # get a list of all the trees on fire within a range 0.5
            list_trees_fire = [this_tree for this_tree in self.model.schedule.agents if
                               (this_tree.on_fire is True) and
                               (math.sqrt((self.x - this_tree.x)**2 + (self.y - this_tree.y)**2) < radius)]

            if (self.type == 'eucalyptus' and len(list_trees_fire) > 3) or \
                    (self.type == 'oak' and len(list_trees_fire) > 6):
                self.current_time_to_fire = self.current_time_to_fire - 1

                if self.current_time_to_fire == 0:
                    self.on_fire = True
            else:
                self.current_time_to_fire = self.time_to_set_fire

        else:

            self.current_time_on_fire = self.current_time_on_fire - 1

            if self.current_time_on_fire == 0:
                self.on_fire = False
                self.is_burned = True
                print('tree %s burned' % self.unique_id)


class ForestModel(Model):
    """A model with some number of agents."""

    def __init__(self, number_trees, wind_conditions, humidity_conditions, fire_location):

        self.num_agents = number_trees
        self.schedule = RandomActivation(self)
        self.humidity = humidity_conditions
        self.wind = wind_conditions

        # Create agents
        for i in range(self.num_agents):
            this_tree = Tree(i, self)

            # set size:
            sizes = ['s', 'm', 'l']
            this_tree.size = random.choice(sizes)

            # set type
            tree_types = ['eucalyptus', 'oak']
            this_tree.type = random.choice(tree_types)

            # set position
            if this_tree.type == 'oak':

                if random.choice([1, 2]) == 1:
                    this_tree.x = np.random.normal(30, 10, 1)
                    this_tree.y = np.random.normal(60, 10, 1)
                else:
                    this_tree.x = np.random.normal(60, 10, 1)
                    this_tree.y = np.random.normal(30, 10, 1)
            else:

                if random.choice([1, 2]) == 1:
                    this_tree.x = np.random.normal(60, 10, 1)
                    this_tree.y = np.random.normal(60, 10, 1)
                else:
                    this_tree.x = np.random.normal(20, 5, 1)
                    this_tree.y = np.random.normal(20, 5, 1)

            # calculate fire time
            this_tree.calculate_time_to_set_fire()
            this_tree.calculate_time_will_stay_on_fire()

            # add tree to schedule
            self.schedule.add(this_tree)

        # set initial trees on fire:
        radius = 4
        list_trees_fire = [this_tree for this_tree in self.schedule.agents if
                           (math.sqrt((fire_location[0] - this_tree.x) ** 2 +
                                      (fire_location[1] - this_tree.y) ** 2) < radius)]

        for this_tree in list_trees_fire:
            this_tree.on_fire = True

    def step(self):
        self.schedule.step()


class ForestSimulation:

    def __init__(self, n_trees=2000, wind='strong', humidity='high', fire_location=[0, 0], number_of_steps=10):

        # set forest model
        self.forest_model = ForestModel(number_trees=n_trees, wind_conditions=wind,
                                        humidity_conditions=humidity, fire_location=fire_location)

        # Setup the figure and axes...
        self.fig, self.ax = plt.subplots()

        # Then setup FuncAnimation.
        self.ani = animation.FuncAnimation(self.fig, self.update, init_func=self.setup_plot,
                                           frames=number_of_steps - 1, interval=1, blit=True)

        self.collection_x = []
        self.collection_y = []
        self.collection_size = []
        self.collection_color = []
        self.number_of_steps = number_of_steps

    def set_fire(self):

        for i in range(self.number_of_steps):
            self.forest_model.step()

            # plot results
            tree_color = []
            marker_size = []
            x = []
            y = []
            for tree in self.forest_model.schedule.agents:

                x.append(tree.x)
                y.append(tree.y)

                # get the color:
                if tree.is_burned is True:
                    tree_color.append('black')

                elif tree.on_fire is True:
                    if tree.steps_left_on_fire <= 2:
                        tree_color.append('red')
                    else:
                        tree_color.append('yellow')
                else:
                    if tree.type == 'oak':
                        tree_color.append('green')
                    else:
                        tree_color.append('lightgreen')

                # get the size:
                if tree.size == 's':
                    marker_size.append(10)
                elif tree.size == 'm':
                    marker_size.append(25)
                else:
                    marker_size.append(40)

            # return x, y, marker_size, tree_color
            self.collection_x.append(x)
            self.collection_y.append(y)
            self.collection_size.append(marker_size)
            self.collection_color.append(tree_color)

    def update(self, i):

        # x, y, size, color = self.set_fire()

        self.scat.set_offsets(np.c_[self.collection_x[i], self.collection_y[i]])
        self.scat._sizes = np.array(self.collection_size[i])
        self.scat.set_facecolor(np.array(self.collection_color[i]))
        return self.scat,

    def setup_plot(self):
        """Initial drawing of the scatter plot."""
        # x, y, size, color = self.set_fire()
        self.scat = self.ax.scatter(self.collection_x[0], self.collection_y[0], c=self.collection_color[0],
                                    s=self.collection_size[0], animated=True)
        # self.scat = self.ax.scatter(self.collection_x[0], self.collection_y[0],
        #                             c=self.collection_color[0], s=self.collection_size[0])

        # For FuncAnimation's sake, we need to return the artist we'll be using
        # Note that it expects a sequence of artists, thus the trailing comma.
        return self.scat,

    def show(self):

        plt.show()


if __name__ == '__main__':

    # environmental parameters
    n_trees = 3000
    w = 'strong'
    hum = 'high'
    location = [60, 60]
    n_of_steps = 200

    # start simulation
    forest_simulation = ForestSimulation(n_trees=n_trees,
                                         wind=w,
                                         humidity=hum,
                                         fire_location=location,
                                         number_of_steps=n_of_steps)
    forest_simulation.set_fire()
    forest_simulation.show()





