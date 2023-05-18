from mesa import Agent
from mesa.model import Model
import numpy as np


class State:
    SUSCEPTIBLE = 0
    INFECTED = 1
    DECEASED = 2
    RECOVERED = 3


class InfectableAgent(Agent):
    """An agent that can get infected."""

    def __init__(self, unique_id: int, model: Model) -> None:
        super().__init__(unique_id, model)
        self.state = State.SUSCEPTIBLE
        self.age = self.random.normalvariate(0, 100)
        self.infection_time = 0
        self.wear_mask = np.random.choice(
            [False, True],
            p=[1 - self.model.wear_mask_chance, self.model.wear_mask_chance],
        )
        self.set_recovery_time()

    def step(self) -> None:
        self.check_status()
        self.move()
        self.contact()

    def check_status(self) -> None:
        """Check infection status"""
        if self.state != State.INFECTED:
            return
        death_rate = self.model.death_rate
        alive = np.random.choice([0, 1], p=[death_rate, 1 - death_rate])
        if alive == 0:
            self.state = State.DECEASED
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
