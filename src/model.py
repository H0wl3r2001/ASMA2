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
        social_distance: int = 0,
        social_distance_chance: float = 0.5,
        isolation_duration: int = 7,
        isolation_chance: float = 0.3,
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
        self.social_distance_chance = social_distance_chance
        self.isolation_duration = isolation_duration
        self.isolation_chance = isolation_chance
        self.grid = MultiGrid(width, height, True)
        self.schedule = RandomActivation(self)
        self.running = True
        self.death_time_freqs = {}

        self.stateDataCollector = DataCollector(
            {
                "Susceptible": lambda m: self.count_state(m, State.SUSCEPTIBLE),
                "Infected": lambda m: self.count_state(m, State.INFECTED),
                "Isolated": lambda m: self.count_state(m, State.ISOLATED),
                "Recovered": lambda m: self.count_state(m, State.RECOVERED),
                "Deceased": lambda m: self.count_state(m, State.DECEASED),
            }
        )
        self.maskDataCollector = DataCollector(
            {
                "Wearing Mask": lambda m: self.count_mask(m, True),
                "Not Wearing Mask": lambda m: self.count_mask(m, False),
            }
        )
        self.ageDataCollector = DataCollector(self.build_age_collector())
        self.deathDataCollector = DataCollector(self.build_death_collector())

        for i in range(self.num_agents):
            a = InfectableAgent(i, self)
            self.add_agent(a)

        self.travelling_agents = []
        for i in range(self.num_traveling_agents):
            a = InfectableAgent(i + self.num_agents, self)
            self.add_agent(a)
            self.travelling_agents.append(a)

        self.stateDataCollector.collect(self)
        self.maskDataCollector.collect(self)
        self.ageDataCollector.collect(self)
        self.deathDataCollector.collect(self)

    def step(self) -> None:
        """Advance the model by one step."""
        self.stateDataCollector.collect(self)
        self.maskDataCollector.collect(self)
        self.ageDataCollector.collect(self)
        self.deathDataCollector.collect(self)

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

    def count_age(self, model: Model, minAge: int, maxAge: int) -> int:
        """Count agents with a given age in the given model"""
        return len(
            [
                a
                for a in model.schedule.agents
                if a.age >= minAge and a.age <= maxAge and a.state is not State.DECEASED
            ]
        )

    def count_death(self, model: Model, minDays: int, maxDays: int) -> int:
        """Count agents who died within a given time frame in the given model"""
        freqs = [
            self.death_time_freqs[t]
            for t in range(minDays, maxDays + 1)
            if t in self.death_time_freqs
        ]
        return sum(freqs)

    def count_mask(self, model: Model, wearing: bool) -> int:
        """Count agents who are wearing/not wearing a mask in the given model"""
        return len(
            [
                a
                for a in model.schedule.agents
                if a.wear_mask == wearing and a.state is not State.DECEASED
            ]
        )

    def build_age_collector(self) -> dict:
        """Build a dict of age collectors for the data collector"""
        age_collector = {}
        for i in range(0, 100, 10):
            age_collector[
                f"{i}-{i+9}"
            ] = lambda m, minAge=i, maxAge=i + 9: self.count_age(m, minAge, maxAge)
        return age_collector

    def build_death_collector(self) -> dict:
        """Build a dict of death collectors for the data collector"""
        death_collector = {}
        for i in range(1, 30, 3):
            death_collector[
                f"{i}-{i+2}"
            ] = lambda m, minDays=i, maxDays=i + 4: self.count_death(
                m, minDays, maxDays
            )
        return death_collector

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

    def register_death(self, agent: InfectableAgent) -> None:
        """Register the death of an agent"""
        death_time = self.schedule.time - agent.infection_time
        if death_time in self.death_time_freqs:
            self.death_time_freqs[death_time] += 1
        else:
            self.death_time_freqs[death_time] = 1
