from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.UserParam import Slider

from model import InfectionModel
from agent import InfectableAgent, State
from mesa.visualization.modules import CanvasGrid, ChartModule

NUM_CELLS = 15
CANVAS_SIZE_X = 500
CANVAS_SIZE_Y = 500

sim_params = {
    "num_agents": Slider(
        "Number of regular agents",
        value=100,  # default
        min_value=10,
        max_value=300,
        step=1,
    ),
    "num_traveling_agents": Slider(
        "Number of traveling agents",
        value=0,  # default
        min_value=0,
        max_value=100,
        step=1,
    ),
    "num_medic_agents": Slider(
        "Number of medic agents",
        value=0,  # default
        min_value=0,
        max_value=100,
        step=1,
    ),
    "infection_rate": Slider(
        "Infection rate",
        value=0.7,  # default
        min_value=0.1,
        max_value=1.0,
        step=0.1,
    ),
    "death_rate": Slider(
        "Death rate",
        value=0.02,  # default
        min_value=0.01,
        max_value=0.5,
        step=0.01,
    ),
    "start_infection_rate": Slider(
        "Start infection rate",
        value=0.05,  # default
        min_value=0.01,
        max_value=0.2,
        step=0.01,
    ),
    "wear_mask_chance": Slider(
        "Chance for agents to wear mask",
        value=0.5,  # default
        min_value=0.0,
        max_value=1.0,
        step=0.1,
    ),
    "mask_effectiveness": Slider(
        "Mask effectiveness",
        value=0.4,  # default
        min_value=0.0,
        max_value=1.0,
        step=0.1,
    ),
    "recovery_time_multiplier": Slider(
        "Recovery time multiplier",
        value=1.0,  # default
        min_value=0.1,
        max_value=5.0,
        step=0.1,
    ),
    "social_distance": Slider(
        "Social distance (cells)",
        value=0,  # default
        min_value=0,
        max_value=5,
        step=1,
    ),
    "social_distance_chance": Slider(
        "Chance for agents to social distance",
        value=0.5,  # default
        min_value=0.0,
        max_value=1.0,
        step=0.1,
    ),
    "isolation_duration": Slider(
        "Isolation duration",
        value = 10,
        min_value = 0,
        max_value= 30,
        step = 1,
    ),
    "isolation_chance": Slider(
        "Chance for infected agents to enter isolation",
        value = 0.3,
        min_value = 0,
        max_value = 1,
        step=0.1,
    ),
    "curing_chance": Slider(
        "Chance for doctor to cure infected agent",
        value = 0.9,
        min_value = 0,
        max_value = 1,
        step=0.1,
    ),
    "width": NUM_CELLS,
    "height": NUM_CELLS,
}


def agent_display(agent: InfectableAgent) -> dict:
    """Display agent with infection state"""
    display = {"Shape": "circle", "Filled": "true", "Layer": 0}
    if agent.state is State.SUSCEPTIBLE:
        display["Color"] = "Blue"
        display["r"] = 0.5
    elif agent.state is State.INFECTED:
        display["Color"] = "Red"
        display["Layer"] = 3
        display["r"] = 0.2
    elif agent.state is State.ISOLATED:
        display["Color"] ="Yellow"
        display["Layer"] = 4
        display["r"] = 0.6
    elif agent.state is State.RECOVERED:
        display["Color"] = "Green"
        display["Layer"] = 1
        display["r"] = 0.4
    elif agent.state is State.DECEASED:
        display["Color"] = "Black"
        display["Layer"] = 2
        display["r"] = 0.3
    return display


grid = CanvasGrid(agent_display, NUM_CELLS, NUM_CELLS, CANVAS_SIZE_X, CANVAS_SIZE_Y)

chart = ChartModule(
    [
        {"Label": "Susceptible", "Color": "Blue"},
        {"Label": "Infected", "Color": "Red"},
        {"Label": "Isolated", "Color" : "Yellow"},
        {"Label": "Recovered", "Color": "Green"},
        {"Label": "Deceased", "Color": "Black"},
    ],
    canvas_height=300,
    data_collector_name="datacollector",
)

server = ModularServer(InfectionModel, [grid, chart], "Infection Model", sim_params)
server.port = 8521
server.launch()
