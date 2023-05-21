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
        num_traveling_agents: int = 0,
        width: int = 10,
        height: int = 10,
        infection_rate: float = 0.4,
        death_rate: float = 0.02,
        start_infection_rate: float = 0.02,
        wear_mask_chance: float = 0.5,
        mask_effectiveness: float = 0.5,
        recovery_time_multiplier: float = 1.0,
        social_distance: int = 0
    ) -> None:
        self.num_agents = num_agents
        self.num_traveling_agents = num_traveling_agents
        self.infection_rate = infection_rate
        self.death_rate = death_rate
        self.start_infection_rate = start_infection_rate
        self.wear_mask_chance = wear_mask_chance
        self.mask_effectiveness = mask_effectiveness
        self.recovery_time_multiplier = recovery_time_multiplier
        self.social_distance = social_distance
        self.grid = MultiGrid(width, height, True)
        self.schedule = RandomActivation(self)
        self.running = True

        self.datacollector = DataCollector(
            {
                "Susceptible": lambda m: self.count_state(m, State.SUSCEPTIBLE),
                "Infected": lambda m: self.count_state(m, State.INFECTED),
                "Recovered": lambda m: self.count_state(m, State.RECOVERED),
                "Deceased": lambda m: self.count_state(m, State.DECEASED),
            }
        )

        for i in range(self.num_agents):
            a = InfectableAgent(i, self)
            self.add_agent(a)

        self.travelling_agents = []
        for i in range(self.num_traveling_agents):
            a = InfectableAgent(i + self.num_agents, self)
            self.add_agent(a)
            self.travelling_agents.append(a)

    def step(self) -> None:
        """Advance the model by one step."""
        self.datacollector.collect(self)

        # travel before step to guarantee checks like social distancing
        if len(self.travelling_agents) > 0:
            self.travel()
        self.schedule.step()
        if self.check_end():
            self.running = False

    def travel(self) -> None:
        """Move traveling agents to random locations"""
        for agent in self.travelling_agents:
            self.place_agent(agent)

    def count_state(self, model: Model, state: State) -> int:
        """Count agents with a given state in the given model"""
        return len([a for a in model.schedule.agents if a.state is state])

    def add_agent(self, agent: InfectableAgent) -> None:
        self.schedule.add(agent)
        self.place_agent(agent)
        self.try_to_infect_agent(agent)
        return agent

    def place_agent(self, agent: InfectableAgent) -> None:
        x = self.random.randrange(self.grid.width)
        y = self.random.randrange(self.grid.height)
        self.grid.place_agent(agent, (x, y))

    def try_to_infect_agent(self, agent: InfectableAgent) -> None:
        infected = np.random.choice(
            [0, 1], p=[1 - self.start_infection_rate, self.start_infection_rate]
        )
        if infected == 1:
            agent.state = State.INFECTED
            agent.infection_time = self.schedule.time

    def check_end(self) -> bool:
        return not any([a.state is State.INFECTED for a in self.schedule.agents])
