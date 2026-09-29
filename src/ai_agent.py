# ============================================================
# GENSHIN IMPACT PVP AI
# Adaptive AI Agent
# ============================================================

import random
import numpy as np

from opponent_model import OpponentModel


# ============================================================
# AI AGENT
# ============================================================

class PvPAgent:
    """
    Adaptive PvP decision-making agent.

    The agent evaluates:

        - Own HP
        - Own energy
        - Opponent HP
        - Arena
        - Objective
        - Team composition
        - Opponent behavior
        - Risk
        - Long-term value

    The current version uses a strategic scoring system.

    Later, this decision engine can be connected to
    reinforcement learning.
    """

    def __init__(
        self,
        name,
        team,
        arena
    ):

        self.name = name

        self.team = team

        self.arena = arena

        self.opponent_model = (
            OpponentModel()
        )

        # ----------------------------------------------------
        # Decision history
        # ----------------------------------------------------

        self.decision_history = []

        # ----------------------------------------------------
        # Learning parameters
        # ----------------------------------------------------

        self.exploration_rate = 0.15

        self.discount_factor = 0.90


    # ========================================================
    # GET ACTIVE CHARACTER
    # ========================================================

    def get_active_character(
        self
    ):

        alive_characters = [

            character

            for character in self.team

            if character.is_alive()

        ]


        if not alive_characters:

            return None


        # Prefer the first living character
        # until switching logic is implemented.

        return alive_characters[0]


    # ========================================================
    # GET OPPONENT ACTIVE CHARACTER
    # ========================================================

    def get_opponent_active_character(
        self,
        opponent_team
    ):

        alive_characters = [

            character

            for character in opponent_team

            if character.is_alive()

        ]


        if not alive_characters:

            return None


        return alive_characters[0]


    # ========================================================
    # HEALTH SCORE
    # ========================================================

    def health_score(
        self,
        character
    ):

        if character is None:

            return 0.0


        return float(
            np.clip(

                character.hp
                /
                character.max_hp,

                0,
                1

            )
        )


    # ========================================================
    # ENERGY SCORE
    # ========================================================

    def energy_score(
        self,
        character
    ):

        if character is None:

            return 0.0


        return float(
            np.clip(

                character.energy
                /
                100,

                0,
                1

            )
        )


    # ========================================================
    # FINISHING POTENTIAL
    # ========================================================

    def finishing_potential(
        self,
        attacker,
        target
    ):

        if attacker is None:

            return 0.0


        if target is None:

            return 0.0


        health_ratio = (

            target.hp
            /
            target.max_hp

        )


        offensive = (
            attacker.offensive_score
        )


        # Lower enemy HP increases finishing potential.

        potential = (

            offensive
            *
            (
                1
                -
                health_ratio
            )

        )


        return float(
            np.clip(
                potential,
                0,
                1
            )
        )


    # ========================================================
    # SURVIVAL VALUE
    # ========================================================

    def survival_value(
        self,
        character
    ):

        if character is None:

            return 0.0


        hp = self.health_score(
            character
        )


        survivability = (
            character.survivability_score
        )


        return float(

            0.60 * hp

            +

            0.40 * survivability

        )


    # ========================================================
    # SPECIAL ATTACK VALUE
    # ========================================================

    def special_value(
        self,
        attacker,
        target
    ):

        if attacker is None:

            return 0.0


        if target is None:

            return 0.0


        if attacker.energy < 30:

            return 0.0


        offensive = (
            attacker.offensive_score
        )


        finishing = (
            self.finishing_potential(
                attacker,
                target
            )
        )


        environment = (
            self.arena.get_modifier(
                "elemental_effect"
            )
        )


        value = (

            0.45
            *
            offensive

            +

            0.25
            *
            finishing

            +

            0.20
            *
            min(
                environment,
                1.5
            )
            /
            1.5

            +

            0.10

        )


        return float(
            np.clip(
                value,
                0,
                1
            )
        )


    # ========================================================
    # BASIC ATTACK VALUE
    # ========================================================

    def basic_attack_value(
        self,
        attacker,
        target
    ):

        if attacker is None:

            return 0.0


        if target is None:

            return 0.0


        offensive = (
            attacker.offensive_score
        )


        target_health = (
            self.health_score(
                target
            )
        )


        value = (

            0.60 * offensive

            +

            0.20
            *
            (
                1
                -
                target_health
            )

            +

            0.20

        )


        return float(
            np.clip(
                value,
                0,
                1
            )
        )


    # ========================================================
    # SWITCH VALUE
    # ========================================================

    def switch_value(
        self,
        current_character
    ):

        if current_character is None:

            return 0.0


        current_survival = (
            self.survival_value(
                current_character
            )
        )


        # If the current character is in serious danger,
        # switching becomes more valuable.

        danger = (

            1
            -
            current_survival

        )


        return float(
            np.clip(
                danger,
                0,
                1
            )
        )


    # ========================================================
    # OBJECTIVE VALUE
    # ========================================================

    def objective_value(
        self,
        character
    ):

        if character is None:

            return 0.0


        role = str(
            getattr(
                character,
                "role",
                ""
            )
        ).lower()


        objective = (
            self.arena.objective
        )


        score = 0.40


        if objective == "Eliminate":

            if "dps" in role:

                score += 0.35


        elif objective == "Control Zones":

            if "support" in role:

                score += 0.25

            if "surviv" in role:

                score += 0.25


        elif objective == "Protect Relic":

            if "support" in role:

                score += 0.25

            if "surviv" in role:

                score += 0.30


        elif objective == "Survival":

            if "surviv" in role:

                score += 0.35


        elif objective == "Collect Orbs":

            if "support" in role:

                score += 0.20


        elif objective == "Escort":

            if "support" in role:

                score += 0.20


        return float(
            np.clip(
                score,
                0,
                1
            )
        )


    # ========================================================
    # OPPONENT THREAT
    # ========================================================

    def opponent_threat(
        self,
        opponent
    ):

        if opponent is None:

            return 0.0


        health = (
            self.health_score(
                opponent
            )
        )


        offensive = (
            opponent.offensive_score
        )


        energy = (
            self.energy_score(
                opponent
            )
        )


        # High offensive ability + high energy
        # represents greater immediate threat.

        threat = (

            0.45 * offensive

            +

            0.30 * energy

            +

            0.25 * health

        )


        return float(
            np.clip(
                threat,
                0,
                1
            )
        )


    # ========================================================
    # RISK OF ATTACK
    # ========================================================

    def attack_risk(
        self,
        attacker,
        target
    ):

        if attacker is None:

            return 1.0


        if target is None:

            return 1.0


        own_health = (
            self.health_score(
                attacker
            )
        )


        enemy_health = (
            self.health_score(
                target
            )
        )


        # Lower own HP means attacking becomes riskier.

        risk = (

            0.50
            *
            (
                1
                -
                own_health
            )

            +

            0.20
            *
            enemy_health

        )


        return float(
            np.clip(
                risk,
                0,
                1
            )
        )


    # ========================================================
    # EVALUATE ACTION
    # ========================================================

    def evaluate_action(
        self,
        action,
        attacker,
        target
    ):
        """
        Evaluate a possible action.
        """

        if action == "basic":

            value = (
                self.basic_attack_value(
                    attacker,
                    target
                )
            )


        elif action == "special":

            value = (
                self.special_value(
                    attacker,
                    target
                )
            )


        elif action == "switch":

            value = (
                self.switch_value(
                    attacker
                )
            )


        else:

            value = 0.0


        # ----------------------------------------------------
        # Objective
        # ----------------------------------------------------

        objective_bonus = (
            self.objective_value(
                attacker
            )
        )


        # ----------------------------------------------------
        # Threat
        # ----------------------------------------------------

        threat = (
            self.opponent_threat(
                target
            )
        )


        # ----------------------------------------------------
        # Risk
        # ----------------------------------------------------

        risk = (
            self.attack_risk(
                attacker,
                target
            )
        )


        # ----------------------------------------------------
        # Opponent behavior
        # ----------------------------------------------------

        opponent_aggression = (
            self.opponent_model
            .aggression_score()
        )


        # ----------------------------------------------------
        # Strategic score
        # ----------------------------------------------------

        if action == "switch":

            score = (

                0.55 * value

                +

                0.20
                *
                threat

                +

                0.15
                *
                objective_bonus

                +

                0.10
                *
                opponent_aggression

            )

        else:

            score = (

                0.40 * value

                +

                0.20
                *
                objective_bonus

                +

                0.20
                *
                threat

                +

                0.10
                *
                opponent_aggression

                -

                0.10 * risk

            )


        return float(
            np.clip(
                score,
                0,
                1
            )
        )


    # ========================================================
    # CHOOSE ACTION
    # ========================================================

    def choose_action(
        self,
        attacker,
        target
    ):
        """
        Choose the action with the highest strategic value.

        Exploration is included so the agent does not
        permanently follow one deterministic strategy.
        """

        possible_actions = [
            "basic"
        ]


        if attacker is not None:

            if attacker.energy >= 30:

                possible_actions.append(
                    "special"
                )


        if (
            attacker is not None
            and
            self.health_score(
                attacker
            ) < 0.30
        ):

            possible_actions.append(
                "switch"
            )


        # ----------------------------------------------------
        # Exploration
        # ----------------------------------------------------

        if random.random() < self.exploration_rate:

            action = random.choice(
                possible_actions
            )

            self.decision_history.append({

                "action": action,

                "reason":
                    "exploration"

            })

            return action


        # ----------------------------------------------------
        # Evaluate actions
        # ----------------------------------------------------

        scores = {}


        for action in possible_actions:

            scores[action] = (
                self.evaluate_action(
                    action,
                    attacker,
                    target
                )
            )


        best_action = max(

            scores,

            key=scores.get

        )


        self.decision_history.append({

            "action":
                best_action,

            "scores":
                scores,

            "reason":
                "strategic_evaluation"

        })


        return best_action


    # ========================================================
    # UPDATE OPPONENT MODEL
    # ========================================================

    def observe_opponent_action(
        self,
        action,
        target=None,
        damage=0.0
    ):

        self.opponent_model.record_action(

            action,

            target=target,

            damage=damage

        )


    # ========================================================
    # UPDATE AFTER SWITCH
    # ========================================================

    def observe_opponent_switch(self):

        self.opponent_model.record_switch()


    # ========================================================
    # GET DECISION STATE
    # ========================================================

    def get_state(
        self,
        attacker,
        target
    ):

        return {

            "own_hp":
                self.health_score(
                    attacker
                ),

            "own_energy":
                self.energy_score(
                    attacker
                ),

            "opponent_hp":
                self.health_score(
                    target
                ),

            "opponent_energy":
                self.energy_score(
                    target
                ),

            "opponent_threat":
                self.opponent_threat(
                    target
                ),

            "opponent_aggression":
                self.opponent_model
                .aggression_score(),

            "objective":
                self.arena.objective,

            "weather":
                self.arena.weather,

            "terrain":
                self.arena.terrain,

            "event":
                self.arena.event

        }


    # ========================================================
    # DISPLAY AGENT STATE
    # ========================================================

    def display_state(
        self,
        attacker,
        target
    ):

        print(
            "\n========================================"
        )

        print(
            f"          {self.name}"
        )

        print(
            "========================================"
        )


        state = self.get_state(
            attacker,
            target
        )


        for key, value in state.items():

            if isinstance(
                value,
                float
            ):

                print(
                    f"{key:<25}: "
                    f"{value:.3f}"
                )

            else:

                print(
                    f"{key:<25}: "
                    f"{value}"
                )


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    from data_loader import (
        load_and_prepare_data
    )

    from character_model import (
        CharacterModel
    )

    from arena import (
        PvPArena
    )

    from team_builder import (
        TeamBuilder
    )

    from combat_engine import (
        PvPCombatEngine
    )


    print(
        "\n========================================"
    )

    print(
        " AI AGENT TEST"
    )

    print(
        "========================================"
    )


    # --------------------------------------------------------
    # Load dataset
    # --------------------------------------------------------

    df, mapping = (
        load_and_prepare_data()
    )


    # --------------------------------------------------------
    # Character model
    # --------------------------------------------------------

    character_model = (
        CharacterModel(
            df
        )
    )


    # --------------------------------------------------------
    # Arena
    # --------------------------------------------------------

    arena = PvPArena()

    arena.display()


    # --------------------------------------------------------
    # Team builder
    # --------------------------------------------------------

    builder = TeamBuilder(

        character_model,

        arena

    )


    # --------------------------------------------------------
    # Build teams
    # --------------------------------------------------------

    result_a = (
        builder.find_best_team(
            team_size=3,
            max_candidates=100
        )
    )


    result_b = (
        builder.find_best_team(
            team_size=3,
            max_candidates=100
        )
    )


    if result_a is None:

        raise RuntimeError(
            "Could not create Player A team."
        )


    if result_b is None:

        raise RuntimeError(
            "Could not create Player B team."
        )


    # --------------------------------------------------------
    # Convert to combat characters
    # --------------------------------------------------------

    engine = PvPCombatEngine(

        result_a["team"],

        result_b["team"],

        arena

    )


    attacker = (
        engine.player_a
        .active_character()
    )


    target = (
        engine.player_b
        .active_character()
    )


    # --------------------------------------------------------
    # Create AI
    # --------------------------------------------------------

    agent = PvPAgent(

        name="Player A AI",

        team=engine.player_a.characters,

        arena=arena

    )


    # --------------------------------------------------------
    # Display state
    # --------------------------------------------------------

    agent.display_state(

        attacker,

        target

    )


    # --------------------------------------------------------
    # Choose action
    # --------------------------------------------------------

    action = agent.choose_action(

        attacker,

        target

    )


    print(
        "\nAI selected action:"
    )

    print(
        action
    )


    # --------------------------------------------------------
    # Show decision history
    # --------------------------------------------------------

    print(
        "\nDecision history:"
    )

    for decision in (
        agent.decision_history
    ):

        print(
            decision
        )


    print(
        "\n========================================"
    )

    print(
        " AI AGENT TEST COMPLETED"
    )

    print(
        "========================================"
    )