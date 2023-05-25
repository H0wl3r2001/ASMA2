from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.UserParam import Slider

from model import InfectionModel
from agent import InfectableAgent, State
from mesa.visualization.modules import (
    CanvasGrid,
    ChartModule,
    BarChartModule,
    PieChartModule,
)
from TitleElement import TitleElement

NUM_CELLS = 50
CANVAS_SIZE_X = 800
CANVAS_SIZE_Y = 800

sim_params = {
    "num_agents": Slider(
        "Number of regular agents",
        value=100,
        min_value=10,
        max_value=1000,
        step=1,
    ),
    "num_traveling_agents": Slider(
        "Number of traveling agents",
        value=0,
        min_value=0,
        max_value=100,
        step=1,
    ),
    "num_medic_agents": Slider(
        "Number of medic agents",
        value=0,
        min_value=0,
        max_value=100,
        step=1,
    ),
    "infection_rate": Slider(
        "Infection rate",
        value=0.7,
        min_value=0.1,
        max_value=1.0,
        step=0.1,
    ),
    "death_rate": Slider(
        "Death rate",
        value=0.02,
        min_value=0.01,
        max_value=0.5,
        step=0.01,
    ),
    "start_infection_rate": Slider(
        "Start infection rate",
        value=0.08,
        min_value=0.01,
        max_value=0.2,
        step=0.01,
    ),
    "wear_mask_chance": Slider(
        "Chance for agents to wear mask",
        value=0.5,
        min_value=0.0,
        max_value=1.0,
        step=0.1,
    ),
    "mask_effectiveness": Slider(
        "Mask effectiveness",
        value=0.4,
        min_value=0.0,
        max_value=1.0,
        step=0.1,
    ),
    "recovery_time_multiplier": Slider(
        "Recovery time multiplier",
        value=1.0,
        min_value=0.1,
        max_value=5.0,
        step=0.1,
    ),
    "social_distance": Slider(
        "Social distance (cells)",
        value=0,
        min_value=0,
        max_value=5,
        step=1,
    ),
    "social_distance_chance": Slider(
        "Chance for agents to social distance",
        value=0.5,
        min_value=0.0,
        max_value=1.0,
        step=0.1,
    ),
    "isolation_duration": Slider(
        "Isolation duration",
        value=10,
        min_value=0,
        max_value=30,
        step=1,
    ),
    "isolation_chance": Slider(
        "Chance for infected agents to enter isolation",
        value=0.1,
        min_value=0,
        max_value=1,
        step=0.1,
    ),
    "curing_chance": Slider(
        "Chance for doctor to cure infected agent",
        value=0.5,
        min_value=0,
        max_value=1,
        step=0.1,
    ),
    "vaccine_ready_time": Slider(
        "Duration before the vaccine is ready",
        value=15,
        min_value=0,
        max_value=40,
        step=1,
    ),
    "vaccine_batch_size": Slider(
        "Size of vaccine batches",
        value=10,
        min_value=0,
        max_value=100,
        step=1,
    ),
    "vaccine_effectiveness": Slider(
        "Vaccine effectiveness",
        value=0.5,
        min_value=0,
        max_value=1,
        step=0.1,
    ),
    "width": NUM_CELLS,
    "height": NUM_CELLS,
}


def agent_display(agent: InfectableAgent) -> dict:
    """Display agent with infection state"""
    display = {"Shape": "circle", "Filled": "true", "Layer": 0}
    if agent.isMedic == True:
        display["Color"] = "Grey"
        display["r"] = 0.6
    elif agent.state is State.SUSCEPTIBLE:
        display["Color"] = "Blue"
        display["r"] = 0.5
    elif agent.state is State.INFECTED:
        display["Color"] = "Red"
        display["Layer"] = 3
        display["r"] = 0.2
    elif agent.state is State.ISOLATED:
        display["Color"] = "Yellow"
        display["Layer"] = 4
        display["r"] = 0.3
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

stateChart = ChartModule(
    [
        {"Label": "Susceptible", "Color": "Blue"},
        {"Label": "Infected", "Color": "Red"},
        {"Label": "Isolated", "Color": "Yellow"},
        {"Label": "Recovered", "Color": "Green"},
        {"Label": "Deceased", "Color": "Black"},
    ],
    canvas_height=300,
    data_collector_name="stateDataCollector",
)

timeToDieBarChart = BarChartModule(
    [{"Label": f"{i}-{i+2}", "Color": "#ff726f"} for i in range(1, 30, 3)],
    canvas_width=1000,
    data_collector_name="deathDataCollector",
)

ageBarChart = BarChartModule(
    [{"Label": f"{i}-{i+9}", "Color": "LightBlue"} for i in range(0, 100, 10)],
    canvas_width=1000,
    data_collector_name="ageDataCollector",
)

maskPieChart = PieChartModule(
    [
        {"Label": "Wearing Mask", "Color": "Green"},
        {"Label": "Not Wearing Mask", "Color": "Red"},
    ],
    canvas_height=300,
    data_collector_name="protectionDataCollector",
)

vaccinationChart = PieChartModule(
    [
        {"Label": "Vaccinated", "Color": "Green"},
        {"Label": "Not Vaccinated", "Color": "Red"},
    ],
    canvas_height=300,
    data_collector_name="protectionDataCollector",
)

server = ModularServer(
    InfectionModel,
    [
        TitleElement("The World", False, 150),
        grid,
        TitleElement("Agent States"),
        stateChart,
        TitleElement("Death Time after Infection (steps)"),
        timeToDieBarChart,
        TitleElement("Age Distribution (years)"),
        ageBarChart,
        TitleElement("Mask Wearing Distribution", False, 50),
        maskPieChart,
        TitleElement("Vaccination Distribution", False, 50),
        vaccinationChart,
    ],
    "Infection Model",
    sim_params,
)
server.port = 8521
server.launch()
