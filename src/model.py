from mesa import Model
from agent import InfectableAgent, State
from mesa.space import MultiGrid
from mesa.time import RandomActivation
from mesa.datacollection import DataCollector
import numpy as np


class InfectionModel(Model):
    """A model for infection spread."""

    def __init__(
        self,
        num_agents: int = 10,
        width: int = 10,
        height: int = 10,
        infection_rate: float = 0.4,
        death_rate: float = 0.02,
        start_infection_rate: float = 0.02,
    ) -> None:
        self.num_agents = num_agents
        self.infection_rate = infection_rate
        self.death_rate = death_rate
        self.start_infection_rate = start_infection_rate
        self.grid = MultiGrid(width, height, True)
        self.schedule = RandomActivation(self)
        self.running = True

        # self.datacollector = DataCollector(agent_reporters={"State": "state"})
        self.datacollector = DataCollector(
            {
                "Susceptible": lambda m: self.count_state(m, State.SUSCEPTIBLE),
                "Infected": lambda m: self.count_state(m, State.INFECTED),
                "Recovered": lambda m: self.count_state(m, State.RECOVERED),
                "Deceased": lambda m: self.count_state(m, State.DECEASED),
            }
        )

        # Create agents
        for i in range(self.num_agents):
            a = InfectableAgent(i, self)
            self.schedule.add(a)

            # Add the agent to a random grid cell
            x = self.random.randrange(self.grid.width)
            y = self.random.randrange(self.grid.height)
            self.grid.place_agent(a, (x, y))

            # Infect some agents at start
            infected = np.random.choice(
                [0, 1], p=[1 - self.start_infection_rate, self.start_infection_rate]
            )
            if infected == 1:
                a.state = State.INFECTED
                a.infection_time = self.schedule.time

    def step(self) -> None:
        """Advance the model by one step."""
        self.datacollector.collect(self)
        self.schedule.step()

    def count_state(self, model: Model, state: State) -> int:
        """Count agents with a given state in the given model"""
        return len([a for a in model.schedule.agents if a.state is state])
