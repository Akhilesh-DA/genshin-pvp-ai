# ============================================================
# GENSHIN IMPACT PVP AI
# Configuration File
# ============================================================

import random
import numpy as np


# ------------------------------------------------------------
# RANDOM SEED
# ------------------------------------------------------------

SEED = 42


def set_seed():
    """
    Set random seeds so that experiments are reproducible.
    """

    random.seed(SEED)
    np.random.seed(SEED)


# ------------------------------------------------------------
# PROJECT PATHS
# ------------------------------------------------------------

CSV_FILE = "data/genshin_impact.csv"

PROCESSED_DATA = "outputs/processed_character_data.csv"

MATCH_DATA = "outputs/synthetic_pvp_matches.csv"

ACTION_DATA = "outputs/synthetic_action_data.csv"

OPPONENT_MODEL = "models/opponent_model.pkl"

ACTION_MODEL = "models/action_model.pkl"


# ------------------------------------------------------------
# GAME SETTINGS
# ------------------------------------------------------------

# Supported team sizes:
#
# 1 -> 1v1
# 2 -> 2v2
# 3 -> 3v3
# 4 -> 4v4
#
# Future:
# N -> NvN

TEAM_SIZE = 4


# Maximum number of turns in one PvP match

MAX_TURNS = 30


# ------------------------------------------------------------
# DATASET GENERATION
# ------------------------------------------------------------

N_PVP_MATCHES = 3000

N_ACTION_SAMPLES = 10000


# ------------------------------------------------------------
# CHARACTER ROLES
# ------------------------------------------------------------

ROLE_LIST = [

    "On-Field",

    "Off-Field",

    "DPS",

    "Support",

    "Survivability"

]


# ------------------------------------------------------------
# ELEMENTS
# ------------------------------------------------------------

ELEMENTS = [

    "Pyro",

    "Hydro",

    "Cryo",

    "Electro",

    "Anemo",

    "Geo",

    "Dendro"

]


# ------------------------------------------------------------
# WEATHER CONDITIONS
# ------------------------------------------------------------

WEATHER = [

    "Clear",

    "Thunderstorm",

    "Sandstorm",

    "Blizzard",

    "Monsoon",

    "Solar Flare"

]


# ------------------------------------------------------------
# TERRAIN CONDITIONS
# ------------------------------------------------------------

TERRAIN = [

    "Open Field",

    "Floating Islands",

    "Crystalline Caverns",

    "Dense Forest",

    "Ancient Ruins"

]


# ------------------------------------------------------------
# OBJECTIVES
# ------------------------------------------------------------

OBJECTIVES = [

    "Eliminate",

    "Control Zones",

    "Protect Relic",

    "Collect Orbs",

    "Survival",

    "Escort"

]


# ------------------------------------------------------------
# DYNAMIC EVENTS
# ------------------------------------------------------------

EVENTS = [

    "None",

    "Lava Eruption",

    "Flood",

    "Corruption Zone",

    "Gravity Inversion",

    "Element Suppression",

    "Energy Blackout",

    "Shield Nullification",

    "Time Distortion"

]


# ------------------------------------------------------------
# POSSIBLE ACTIONS
# ------------------------------------------------------------

ACTIONS = [

    "Move",

    "Attack",

    "Skill",

    "Burst",

    "Swap",

    "Defend",

    "Gather Resource",

    "Capture Objective",

    "Retreat",

    "Coordinate"

]


# ------------------------------------------------------------
# OPPONENT PERSONALITIES
# ------------------------------------------------------------

OPPONENT_PERSONALITIES = [

    "Aggressive",

    "Defensive",

    "Adaptive",

    "Objective Focused",

    "Resource Focused"

]


# ------------------------------------------------------------
# COMBAT PARAMETERS
# ------------------------------------------------------------

ACTION_MULTIPLIERS = {

    "Attack": 0.80,

    "Skill": 1.20,

    "Burst": 1.80

}


# ------------------------------------------------------------
# PVP SCORING
# ------------------------------------------------------------

# The system intentionally does NOT make raw damage
# the only determinant of victory.

SCORE_WEIGHTS = {

    "survival": 0.25,

    "objective": 0.20,

    "resource": 0.10,

    "synergy": 0.15,

    "damage": 0.10,

    "adaptability": 0.10,

    "risk_management": 0.10

}


# ------------------------------------------------------------
# MODEL SETTINGS
# ------------------------------------------------------------

RANDOM_FOREST_ESTIMATORS = 250

RANDOM_FOREST_MAX_DEPTH = 15


# ------------------------------------------------------------
# DISPLAY SETTINGS
# ------------------------------------------------------------

PRINT_MATCH_DETAILS = True

PRINT_TEAM_DETAILS = True

PRINT_ARENA_DETAILS = True