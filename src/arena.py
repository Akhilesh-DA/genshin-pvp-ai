# ============================================================
# GENSHIN IMPACT PVP AI
# Dynamic PvP Arena Module
# ============================================================

import random
import numpy as np

import config


# ------------------------------------------------------------
# ARENA CLASS
# ------------------------------------------------------------

class PvPArena:
    """
    Represents a dynamic PvP combat environment.

    The arena contains:

        - Weather
        - Terrain
        - Objective
        - Dynamic event
        - Environmental modifiers

    These conditions influence combat and strategy.

    The purpose is to prevent the AI from relying only
    on character statistics.
    """

    def __init__(
        self,
        weather=None,
        terrain=None,
        objective=None,
        event=None
    ):

        # ----------------------------------------------------
        # Select environmental conditions
        # ----------------------------------------------------

        self.weather = (

            weather
            if weather is not None
            else random.choice(
                config.WEATHER
            )

        )

        self.terrain = (

            terrain
            if terrain is not None
            else random.choice(
                config.TERRAIN
            )

        )

        self.objective = (

            objective
            if objective is not None
            else random.choice(
                config.OBJECTIVES
            )

        )

        self.event = (

            event
            if event is not None
            else random.choice(
                config.EVENTS
            )

        )


        # ----------------------------------------------------
        # Environmental modifiers
        # ----------------------------------------------------

        self.modifiers = (
            self._create_modifiers()
        )


    # --------------------------------------------------------
    # CREATE ENVIRONMENTAL MODIFIERS
    # --------------------------------------------------------

    def _create_modifiers(self):
        """
        Create modifiers based on the current arena.

        Values are multipliers.

        Example:

            1.20 = 20% increase

            0.80 = 20% decrease

            1.00 = no modification
        """

        modifiers = {

            "damage":
                1.00,

            "survivability":
                1.00,

            "movement":
                1.00,

            "energy":
                1.00,

            "objective":
                1.00,

            "elemental_effect":
                1.00,

            "resource_gain":
                1.00

        }


        # ====================================================
        # WEATHER EFFECTS
        # ====================================================

        if self.weather == "Clear":

            modifiers["damage"] *= 1.00


        elif self.weather == "Thunderstorm":

            modifiers["elemental_effect"] *= 1.20

            modifiers["energy"] *= 0.95


        elif self.weather == "Sandstorm":

            modifiers["movement"] *= 0.85

            modifiers["objective"] *= 1.10


        elif self.weather == "Blizzard":

            modifiers["movement"] *= 0.75

            modifiers["survivability"] *= 0.90


        elif self.weather == "Monsoon":

            modifiers["movement"] *= 0.90

            modifiers["elemental_effect"] *= 1.15


        elif self.weather == "Solar Flare":

            modifiers["damage"] *= 1.15

            modifiers["survivability"] *= 0.95


        # ====================================================
        # TERRAIN EFFECTS
        # ====================================================

        if self.terrain == "Open Field":

            modifiers["movement"] *= 1.10


        elif self.terrain == "Floating Islands":

            modifiers["movement"] *= 0.85

            modifiers["objective"] *= 1.15


        elif self.terrain == "Crystalline Caverns":

            modifiers["survivability"] *= 1.10

            modifiers["movement"] *= 0.90


        elif self.terrain == "Dense Forest":

            modifiers["movement"] *= 0.95

            modifiers["survivability"] *= 1.05


        elif self.terrain == "Ancient Ruins":

            modifiers["objective"] *= 1.20


        # ====================================================
        # OBJECTIVE EFFECTS
        # ====================================================

        if self.objective == "Eliminate":

            modifiers["damage"] *= 1.10


        elif self.objective == "Control Zones":

            modifiers["objective"] *= 1.25

            modifiers["movement"] *= 1.05


        elif self.objective == "Protect Relic":

            modifiers["survivability"] *= 1.15

            modifiers["objective"] *= 1.20


        elif self.objective == "Collect Orbs":

            modifiers["resource_gain"] *= 1.30

            modifiers["movement"] *= 1.10


        elif self.objective == "Survival":

            modifiers["survivability"] *= 1.25


        elif self.objective == "Escort":

            modifiers["movement"] *= 1.15

            modifiers["survivability"] *= 1.10


        # ====================================================
        # DYNAMIC EVENTS
        # ====================================================

        if self.event == "None":

            pass


        elif self.event == "Lava Eruption":

            modifiers["movement"] *= 0.85

            modifiers["survivability"] *= 0.90


        elif self.event == "Flood":

            modifiers["movement"] *= 0.80

            modifiers["elemental_effect"] *= 1.15


        elif self.event == "Corruption Zone":

            modifiers["survivability"] *= 0.85

            modifiers["damage"] *= 1.10


        elif self.event == "Gravity Inversion":

            modifiers["movement"] *= 1.25


        elif self.event == "Element Suppression":

            modifiers["elemental_effect"] *= 0.65


        elif self.event == "Energy Blackout":

            modifiers["energy"] *= 0.50


        elif self.event == "Shield Nullification":

            modifiers["survivability"] *= 0.80


        elif self.event == "Time Distortion":

            modifiers["movement"] *= 1.15

            modifiers["energy"] *= 1.15


        return modifiers


    # --------------------------------------------------------
    # GET MODIFIER
    # --------------------------------------------------------

    def get_modifier(
        self,
        modifier_name
    ):
        """
        Return a specific environmental modifier.
        """

        return self.modifiers.get(
            modifier_name,
            1.0
        )


    # --------------------------------------------------------
    # CHARACTER ENVIRONMENT SCORE
    # --------------------------------------------------------

    def calculate_character_environment_score(
        self,
        character
    ):
        """
        Estimate how well a character fits
        the current environment.

        This is intentionally different from
        the character's raw PvP value.
        """

        score = 0.50


        # ----------------------------------------------------
        # Extract character information
        # ----------------------------------------------------

        element = str(
            character.get(
                "element",
                "Unknown"
            )
        ).lower()


        role = str(
            character.get(
                "role",
                "Unknown"
            )
        ).lower()


        # ----------------------------------------------------
        # Weather interaction
        # ----------------------------------------------------

        if self.weather == "Thunderstorm":

            if element == "electro":

                score += 0.15


        elif self.weather == "Blizzard":

            if element == "cryo":

                score += 0.15


        elif self.weather == "Monsoon":

            if element == "hydro":

                score += 0.15


        elif self.weather == "Solar Flare":

            if element == "pyro":

                score += 0.15


        # ----------------------------------------------------
        # Objective interaction
        # ----------------------------------------------------

        if self.objective == "Control Zones":

            if (
                "support" in role
                or "surviv" in role
            ):

                score += 0.12


        elif self.objective == "Protect Relic":

            if (
                "support" in role
                or "surviv" in role
            ):

                score += 0.15


        elif self.objective == "Eliminate":

            if "dps" in role:

                score += 0.12


        elif self.objective == "Collect Orbs":

            if (
                "off" in role
                or "support" in role
            ):

                score += 0.08


        elif self.objective == "Survival":

            if "surviv" in role:

                score += 0.15


        # ----------------------------------------------------
        # Event interaction
        # ----------------------------------------------------

        if self.event == "Energy Blackout":

            # Energy-dependent strategies become
            # less attractive.

            if "dps" in role:

                score -= 0.05


        elif self.event == "Shield Nullification":

            if "surviv" in role:

                score -= 0.03


        elif self.event == "Element Suppression":

            # Flexible roles suffer less.

            if (
                "support" in role
                or "off" in role
            ):

                score += 0.05


        return float(
            np.clip(
                score,
                0,
                1
            )
        )


    # --------------------------------------------------------
    # TEAM ENVIRONMENT SCORE
    # --------------------------------------------------------

    def calculate_team_environment_score(
        self,
        team
    ):
        """
        Calculate how well an entire team
        fits the current environment.
        """

        if not team:

            return 0.0


        character_scores = []


        for character in team:

            score = (
                self.calculate_character_environment_score(
                    character
                )
            )

            character_scores.append(
                score
            )


        return float(
            np.mean(
                character_scores
            )
        )


    # --------------------------------------------------------
    # OBJECTIVE VALUE
    # --------------------------------------------------------

    def get_objective_value(
        self,
        team
    ):
        """
        Calculate the team's expected value
        for the current objective.
        """

        if not team:

            return 0.0


        score = 0.50


        roles = [

            str(
                character.get(
                    "role",
                    ""
                )
            ).lower()

            for character in team

        ]


        # ----------------------------------------------------
        # Control Zones
        # ----------------------------------------------------

        if self.objective == "Control Zones":

            support_count = sum(

                "support" in role

                for role in roles

            )

            survivability_count = sum(

                "surviv" in role

                for role in roles

            )

            score += (
                0.08 * support_count
            )

            score += (
                0.08 * survivability_count
            )


        # ----------------------------------------------------
        # Protect Relic
        # ----------------------------------------------------

        elif self.objective == "Protect Relic":

            survivability_count = sum(

                "surviv" in role

                for role in roles

            )

            support_count = sum(

                "support" in role

                for role in roles

            )

            score += (
                0.10 * survivability_count
            )

            score += (
                0.06 * support_count
            )


        # ----------------------------------------------------
        # Eliminate
        # ----------------------------------------------------

        elif self.objective == "Eliminate":

            dps_count = sum(

                "dps" in role

                for role in roles

            )

            score += (
                0.10 * dps_count
            )


        # ----------------------------------------------------
        # Survival
        # ----------------------------------------------------

        elif self.objective == "Survival":

            survivability_count = sum(

                "surviv" in role

                for role in roles

            )

            score += (
                0.12 * survivability_count
            )


        # ----------------------------------------------------
        # Collect Orbs
        # ----------------------------------------------------

        elif self.objective == "Collect Orbs":

            flexible_count = sum(

                (
                    "support" in role
                    or "off" in role
                )

                for role in roles

            )

            score += (
                0.08 * flexible_count
            )


        # ----------------------------------------------------
        # Escort
        # ----------------------------------------------------

        elif self.objective == "Escort":

            score += (
                0.05
                *
                len(team)
            )


        return float(
            np.clip(
                score,
                0,
                1
            )
        )


    # --------------------------------------------------------
    # ENVIRONMENT DIFFICULTY
    # --------------------------------------------------------

    def calculate_difficulty(
        self
    ):
        """
        Estimate how disruptive the environment is.

        Higher values indicate a more unusual or
        strategically challenging environment.
        """

        difficulty = 0.20


        # Weather

        if self.weather != "Clear":

            difficulty += 0.10


        # Terrain

        if self.terrain != "Open Field":

            difficulty += 0.10


        # Dynamic event

        if self.event != "None":

            difficulty += 0.20


        # Objectives requiring planning

        if self.objective in [

            "Control Zones",

            "Protect Relic",

            "Collect Orbs",

            "Escort"

        ]:

            difficulty += 0.15


        return float(
            np.clip(
                difficulty,
                0,
                1
            )
        )


    # --------------------------------------------------------
    # ARENA STATE
    # --------------------------------------------------------

    def get_state(
        self
    ):
        """
        Return the complete arena state.
        """

        return {

            "weather":
                self.weather,

            "terrain":
                self.terrain,

            "objective":
                self.objective,

            "event":
                self.event,

            "damage_modifier":
                self.get_modifier(
                    "damage"
                ),

            "survivability_modifier":
                self.get_modifier(
                    "survivability"
                ),

            "movement_modifier":
                self.get_modifier(
                    "movement"
                ),

            "energy_modifier":
                self.get_modifier(
                    "energy"
                ),

            "objective_modifier":
                self.get_modifier(
                    "objective"
                ),

            "elemental_modifier":
                self.get_modifier(
                    "elemental_effect"
                ),

            "resource_modifier":
                self.get_modifier(
                    "resource_gain"
                ),

            "difficulty":
                self.calculate_difficulty()

        }


    # --------------------------------------------------------
    # DISPLAY ARENA
    # --------------------------------------------------------

    def display(
        self
    ):
        """
        Print arena information.
        """

        print(
            "\n========================================"
        )

        print(
            "             PVP ARENA"
        )

        print(
            "========================================"
        )

        print(
            f"Weather   : {self.weather}"
        )

        print(
            f"Terrain   : {self.terrain}"
        )

        print(
            f"Objective : {self.objective}"
        )

        print(
            f"Event     : {self.event}"
        )

        print(
            "\nModifiers:"
        )

        for name, value in (
            self.modifiers.items()
        ):

            print(
                f"  {name:<20}: "
                f"{value:.2f}"
            )

        print(
            f"\nDifficulty: "
            f"{self.calculate_difficulty():.2f}"
        )


# ------------------------------------------------------------
# RANDOM ARENA GENERATOR
# ------------------------------------------------------------

def generate_random_arena():
    """
    Generate a completely random PvP arena.
    """

    return PvPArena()


# ------------------------------------------------------------
# MULTIPLE ARENAS
# ------------------------------------------------------------

def generate_multiple_arenas(
    number=10
):
    """
    Generate multiple random arenas.
    """

    arenas = []

    for _ in range(number):

        arenas.append(
            generate_random_arena()
        )

    return arenas


# ------------------------------------------------------------
# STANDALONE TEST
# ------------------------------------------------------------

if __name__ == "__main__":

    print(
        "\n========================================"
    )

    print(
        " DYNAMIC PVP ARENA TEST"
    )

    print(
        "========================================"
    )


    # --------------------------------------------------------
    # Create random arena
    # --------------------------------------------------------

    arena = generate_random_arena()


    # --------------------------------------------------------
    # Display arena
    # --------------------------------------------------------

    arena.display()


    # --------------------------------------------------------
    # Display state
    # --------------------------------------------------------

    print(
        "\n========================================"
    )

    print(
        "ARENA STATE"
    )

    print(
        "========================================"
    )

    state = arena.get_state()


    for key, value in state.items():

        print(
            f"{key:<25}: {value}"
        )


    print(
        "\nArena module test completed successfully."
    )