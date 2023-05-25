from mesa import Agent
from mesa.model import Model
from mesa.space import Position
from mesa.datacollection import DataCollector
import numpy as np


class State:
    SUSCEPTIBLE = 0
    INFECTED = 1
    ISOLATED = 2
    DECEASED = 3
    RECOVERED = 4


class InfectableAgent(Agent):
    """An agent that can get infected."""

    def __init__(self, unique_id: int, model: Model) -> None:
        super().__init__(unique_id, model)
        self.state = State.SUSCEPTIBLE
        self.age = self.random.uniform(0, 99)
        self.infection_time = 0
        self.wear_mask = np.random.choice(
            [False, True],
            p=[1 - self.model.wear_mask_chance, self.model.wear_mask_chance],
        )
        self.isolation_time = 0
        self.set_recovery_time()

    def step(self) -> None:
        self.check_status()
        if self.state == State.ISOLATED:
            self.isolation_time += 1
            if(self.isolation_time == self.model.isolation_duration):
                self.state = State.INFECTED
        elif self.model.social_distance > 0:
            self.move_with_distance()
        else:
            self.move()
        self.contact()

    def check_status(self) -> None:
        """Check infection status"""
        if (self.state != State.INFECTED | self.state != State.ISOLATED):
            return
        if(self.state != State.ISOLATED):
            isolation_rate = self.model.isolation_chance
            isolated = np.random.choice([0,1], p=[isolation_rate, 1-isolation_rate])
            if(isolated == 0):
                self.isolation_time = 0
                self.state = State.ISOLATED
        death_rate = self.model.death_rate
        alive = np.random.choice([0, 1], p=[death_rate, 1 - death_rate])
        if alive == 0:
            self.state = State.DECEASED
            self.model.register_death(self)
        else:
            t = self.model.schedule.time - self.infection_time
            if t >= self.recovery_time:
                self.state = State.RECOVERED

    def move(self) -> None:
        """Move the agent"""
        possible_steps = self.model.grid.get_neighborhood(
            self.pos, moore=True, include_center=False
        )
        new_position = self.random.choice(possible_steps)
        self.model.grid.move_agent(self, new_position)

    def move_with_distance(self) -> None:
        """Move the agent with concern to social distance. Tries to maximize distance if model.social_distance is not possible."""
        if self.random.random() > self.model.social_distance_chance:
            self.move()
            return

        possible_steps = self.model.grid.get_neighborhood(
            self.pos, moore=True, include_center=False
        )
        self.random.shuffle(possible_steps)

        new_pos = None
        cur_distance = self.model.social_distance

        while new_pos is None:
            if cur_distance <= 0:
                self.move()
                return

            for step in possible_steps:
                if self.check_social_distance(step, cur_distance):
                    new_pos = step
                    break

            # if no position was found, try staying in the same position
            if self.check_social_distance(self.pos, cur_distance):
                new_pos = self.pos

            # otherwise, try with a smaller distance
            cur_distance -= 1

        self.model.grid.move_agent(self, new_pos)

    def check_social_distance(self, pos: Position, distance: int) -> bool:
        cells_in_distance = self.model.grid.get_neighborhood(
            pos,
            moore=True,
            include_center=True,
            radius=distance - 1,  # -1 because the center is included
        )
        agents_in_distance = [
            cell
            for cell in cells_in_distance
            if not self.model.grid.is_cell_empty(cell)
        ]
        return len(agents_in_distance) == 1  # only the agent itself

    def contact(self) -> None:
        """Find close agents and infect them"""
        cellmates = self.model.grid.get_cell_list_contents([self.pos])
        if len(cellmates) == 0:
            return
        for agent in cellmates:
            if self.random.random() > self.get_infection_rate():
                continue
            if self.state is State.INFECTED and agent.state is State.SUSCEPTIBLE:
                agent.state = State.INFECTED
                agent.infection_time = self.model.schedule.time


    def cure_adjacent(self) -> None:
        cellmates = self.model.grid.get_cell_list_contents([self.pos])
        if len(cellmates) == 0:
            return
        for agent in cellmates:
            if self.random.random() > self.model.curing_chance:
                continue
            if self.state is State.INFECTED and agent.state is not State.DECEASED:
                agent.state = State.RECOVERED



    def get_infection_rate(self) -> float:
        """Get infection rate, considering factors like wearing a mask"""
        if self.wear_mask:
            return self.model.infection_rate * (1 - self.model.mask_effectiveness)
        else:
            return self.model.infection_rate

    def set_recovery_time(self) -> None:
        """Set recovery time"""
        if self.age <= 12:
            self.recovery_time = self.random.randint(2, 7)
        elif self.age <= 19:
            self.recovery_time = self.random.randint(4, 11)
        elif self.age <= 29:
            self.recovery_time = self.random.randint(5, 14)
        elif self.age <= 39:
            self.recovery_time = self.random.randint(7, 14)
        elif self.age <= 59:
            self.recovery_time = self.random.randint(8, 21)
        elif self.age <= 79:
            self.recovery_time = self.random.randint(14, 21)
        else:
            self.recovery_time = self.random.randint(14, 28)

        self.recovery_time = int(
            self.recovery_time * self.model.recovery_time_multiplier
        )
