# ============================================================
# GENSHIN IMPACT PVP AI
# COMBAT ENGINE
#
# Steps 11A - 11D
#
# This module:
#   1. Creates Player A and Player B
#   2. Creates an AI agent for each player
#   3. Lets the AI choose every action
#   4. Supports 1v1, 2v2, 3v3 and 4v4
#   5. Supports character switching
#   6. Records opponent behaviour
#   7. Tracks objectives
#   8. Produces a complete battle result
# ============================================================

import random
import math


# ============================================================
# AI IMPORT
# ============================================================

from ai_agent import PvPAgent


# ============================================================
# BATTLE TEAM
# ============================================================

class BattleTeam:

    def __init__(
        self,
        name,
        characters
    ):

        self.name = name

        # Make a copy so the original team is not modified.
        self.characters = list(characters)

        # Current active character index.
        self.active_index = 0

        # Objective progress.
        self.objective_progress = 0.0

        # Score used by some objectives.
        self.objective_score = 0.0

    # ========================================================
    # ACTIVE CHARACTER
    # ========================================================

    def active_character(self):

        # ----------------------------------------------------
        # If current character is alive, use it.
        # ----------------------------------------------------

        if (
            0 <= self.active_index
            < len(self.characters)
        ):

            current = self.characters[
                self.active_index
            ]

            if self.is_alive(current):

                return current

        # ----------------------------------------------------
        # Current character is dead.
        # Find another living character.
        # ----------------------------------------------------

        for index, character in enumerate(
            self.characters
        ):

            if self.is_alive(character):

                self.active_index = index

                return character

        return None

    # ========================================================
    # IS CHARACTER ALIVE
    # ========================================================

    def is_alive(
        self,
        character
    ):

        if character is None:

            return False

        # Most of the project uses is_alive().
        if hasattr(
            character,
            "is_alive"
        ):

            try:

                return bool(
                    character.is_alive()
                )

            except Exception:

                pass

        # Fallback to HP.
        hp = getattr(
            character,
            "hp",
            0
        )

        return hp > 0

    # ========================================================
    # REMAINING CHARACTERS
    # ========================================================

    def remaining_characters(self):

        return sum(

            1

            for character in self.characters

            if self.is_alive(character)

        )

    # ========================================================
    # HAS LOST
    # ========================================================

    def has_lost(self):

        return (
            self.remaining_characters()
            == 0
        )

    # ========================================================
    # SWITCH CHARACTER
    # ========================================================

    def switch_character(self):

        alive_indices = [

            index

            for index, character
            in enumerate(self.characters)

            if self.is_alive(character)

        ]

        if len(alive_indices) <= 1:

            return self.active_character()

        # ----------------------------------------------------
        # Find next living character.
        # ----------------------------------------------------

        current_position = (
            alive_indices.index(
                self.active_index
            )
            if self.active_index
            in alive_indices
            else -1
        )

        next_position = (
            current_position + 1
        ) % len(alive_indices)

        self.active_index = (
            alive_indices[
                next_position
            ]
        )

        return self.active_character()


# ============================================================
# COMBAT ENGINE
# ============================================================

class PvPCombatEngine:

    def __init__(
        self,
        team_a,
        team_b,
        arena,
        max_turns=100
    ):

        # ----------------------------------------------------
        # Store arena
        # ----------------------------------------------------

        self.arena = arena

        # ----------------------------------------------------
        # Store teams
        # ----------------------------------------------------

        self.player_a = BattleTeam(

            "Player A",

            team_a

        )

        self.player_b = BattleTeam(

            "Player B",

            team_b

        )

        # ----------------------------------------------------
        # Battle settings
        # ----------------------------------------------------

        self.max_turns = max_turns

        self.turn = 0

        self.history = []

        self.finished = False

        self.winner = None

        # ----------------------------------------------------
        # Create AI agents
        # ----------------------------------------------------

        self.agent_a = PvPAgent(

            name="Player A AI",

            team=self.player_a.characters,

            arena=self.arena

        )

        self.agent_b = PvPAgent(

            name="Player B AI",

            team=self.player_b.characters,

            arena=self.arena

        )

    # ========================================================
    # SAFE VALUE
    # ========================================================

    @staticmethod
    def safe_float(
        value,
        default=0.0
    ):

        try:

            result = float(value)

            if math.isnan(result):

                return default

            if math.isinf(result):

                return default

            return result

        except (
            TypeError,
            ValueError
        ):

            return default

    # ========================================================
    # GET CHARACTER HP
    # ========================================================

    @staticmethod
    def get_hp(
        character
    ):

        return PvPCombatEngine.safe_float(

            getattr(
                character,
                "hp",
                0
            )

        )

    # ========================================================
    # GET MAX HP
    # ========================================================

    @staticmethod
    def get_max_hp(
        character
    ):

        max_hp = getattr(

            character,

            "max_hp",

            None

        )

        if max_hp is None:

            max_hp = getattr(

                character,

                "hp",

                100

            )

        return max(

            PvPCombatEngine.safe_float(

                max_hp,

                100

            ),

            1

        )

    # ========================================================
    # SET HP
    # ========================================================

    @staticmethod
    def set_hp(
        character,
        value
    ):

        max_hp = (
            PvPCombatEngine
            .get_max_hp(character)
        )

        value = max(

            0.0,

            min(
                float(value),
                max_hp
            )

        )

        character.hp = value

    # ========================================================
    # GET ENERGY
    # ========================================================

    @staticmethod
    def get_energy(
        character
    ):

        return max(

            0.0,

            PvPCombatEngine.safe_float(

                getattr(
                    character,
                    "energy",
                    0
                )

            )

        )

    # ========================================================
    # SET ENERGY
    # ========================================================

    @staticmethod
    def set_energy(
        character,
        value
    ):

        character.energy = max(

            0.0,

            min(
                100.0,
                float(value)
            )

        )

    # ========================================================
    # CHARACTER NAME
    # ========================================================

    @staticmethod
    def get_name(
        character
    ):

        return str(

            getattr(

                character,

                "name",

                "Unknown Character"

            )

        )

    # ========================================================
    # OFFENSIVE SCORE
    # ========================================================

    @staticmethod
    def get_offensive_score(
        character
    ):

        value = getattr(

            character,

            "offensive_score",

            None

        )

        if value is None:

            # Fallback to attack-related fields.
            value = getattr(

                character,

                "attack",

                None

            )

        if value is None:

            value = getattr(

                character,

                "base_attack",

                50

            )

        value = PvPCombatEngine.safe_float(

            value,

            50

        )

        # Normalize larger stats into 0-1.
        return max(

            0.05,

            min(
                1.0,
                value / 300.0
            )

        )

    # ========================================================
    # SURVIVABILITY SCORE
    # ========================================================

    @staticmethod
    def get_survivability_score(
        character
    ):

        value = getattr(

            character,

            "survivability_score",

            None

        )

        if value is not None:

            return max(

                0.05,

                min(
                    1.0,
                    PvPCombatEngine.safe_float(
                        value
                    )
                )

            )

        max_hp = (
            PvPCombatEngine
            .get_max_hp(character)
        )

        return max(

            0.05,

            min(
                1.0,
                max_hp / 20000.0
            )

        )

    # ========================================================
    # CHECK ALIVE
    # ========================================================

    @staticmethod
    def is_alive(
        character
    ):

        if character is None:

            return False

        if hasattr(

            character,

            "is_alive"

        ):

            try:

                return bool(
                    character.is_alive()
                )

            except Exception:

                pass

        return (
            PvPCombatEngine
            .get_hp(character)
            > 0
        )

    # ========================================================
    # ARENA MODIFIER
    # ========================================================

    def arena_modifier(
        self
    ):

        modifier = 1.0

        # ----------------------------------------------------
        # Weather
        # ----------------------------------------------------

        weather = str(

            getattr(

                self.arena,

                "weather",

                ""

            )

        ).lower()

        if weather:

            if (
                "storm"
                in weather
                or
                "thunder"
                in weather
            ):

                modifier *= 1.05

            elif "rain" in weather:

                modifier *= 1.02

            elif "sun" in weather:

                modifier *= 1.03

        # ----------------------------------------------------
        # Event
        # ----------------------------------------------------

        event = str(

            getattr(

                self.arena,

                "event",

                ""

            )

        ).lower()

        if event:

            if (
                "energy"
                in event
            ):

                modifier *= 0.95

            elif (
                "damage"
                in event
            ):

                modifier *= 1.05

        return modifier

    # ========================================================
    # CALCULATE BASIC DAMAGE
    # ========================================================

    def calculate_basic_damage(
        self,
        attacker,
        defender
    ):

        offensive = (
            self.get_offensive_score(
                attacker
            )
        )

        survivability = (
            self.get_survivability_score(
                defender
            )
        )

        # ----------------------------------------------------
        # Base damage
        # ----------------------------------------------------

        base_damage = (

            12.0

            +

            48.0
            *
            offensive

        )

        # ----------------------------------------------------
        # Defender mitigation
        # ----------------------------------------------------

        mitigation = (

            1.0

            -

            0.35
            *
            survivability

        )

        # ----------------------------------------------------
        # Arena
        # ----------------------------------------------------

        environment = (
            self.arena_modifier()
        )

        # ----------------------------------------------------
        # Small randomness
        # ----------------------------------------------------

        randomness = random.uniform(

            0.90,

            1.10

        )

        damage = (

            base_damage

            *

            mitigation

            *

            environment

            *

            randomness

        )

        return max(

            1.0,

            damage

        )

    # ========================================================
    # CALCULATE SPECIAL DAMAGE
    # ========================================================

    def calculate_special_damage(
        self,
        attacker,
        defender
    ):

        offensive = (
            self.get_offensive_score(
                attacker
            )
        )

        survivability = (
            self.get_survivability_score(
                defender
            )
        )

        base_damage = (

            28.0

            +

            95.0
            *
            offensive

        )

        mitigation = (

            1.0

            -

            0.25
            *
            survivability

        )

        environment = (
            self.arena_modifier()
        )

        randomness = random.uniform(

            0.90,

            1.10

        )

        damage = (

            base_damage

            *

            mitigation

            *

            environment

            *

            randomness

        )

        return max(

            1.0,

            damage

        )

    # ========================================================
    # BASIC ATTACK
    # ========================================================

    def basic_attack(
        self,
        attacker,
        defender
    ):

        damage = (
            self.calculate_basic_damage(
                attacker,
                defender
            )
        )

        old_hp = (
            self.get_hp(defender)
        )

        self.set_hp(

            defender,

            old_hp - damage

        )

        # Basic attacks generate energy.
        attacker_energy = (
            self.get_energy(attacker)
        )

        self.set_energy(

            attacker,

            attacker_energy + 12

        )

        return damage

    # ========================================================
    # SPECIAL ATTACK
    # ========================================================

    def special_attack(
        self,
        attacker,
        defender
    ):

        # ----------------------------------------------------
        # Not enough energy
        # ----------------------------------------------------

        if (
            self.get_energy(attacker)
            < 30
        ):

            return self.basic_attack(

                attacker,

                defender

            )

        damage = (
            self.calculate_special_damage(

                attacker,

                defender

            )
        )

        old_hp = (
            self.get_hp(defender)
        )

        self.set_hp(

            defender,

            old_hp - damage

        )

        # ----------------------------------------------------
        # Consume energy
        # ----------------------------------------------------

        energy = (
            self.get_energy(attacker)
        )

        self.set_energy(

            attacker,

            energy - 30

        )

        return damage

    # ========================================================
    # SELECT ACTION
    # ========================================================

    def select_action(
        self,
        agent,
        attacker,
        defender
    ):

        """
        The important integration point.

        The combat engine does NOT decide the action.

        The PvPAgent does.

        This means the AI's decision-making system is
        actually controlling the battle.
        """

        return agent.choose_action(

            attacker,

            defender

        )

    # ========================================================
    # SWITCH CHARACTER
    # ========================================================

    def switch_character(
        self,
        team,
        agent
    ):

        old_character = (
            team.active_character()
        )

        new_character = (
            team.switch_character()
        )

        if (
            new_character is not None
            and
            new_character
            is not old_character
        ):

            agent.observe_opponent_switch()

        return new_character

    # ========================================================
    # EXECUTE ACTION
    # ========================================================

    def execute_action(
        self,
        agent,
        team,
        attacker,
        defender
    ):

        # ----------------------------------------------------
        # Ask AI
        # ----------------------------------------------------

        action = self.select_action(

            agent,

            attacker,

            defender

        )

        # ----------------------------------------------------
        # BASIC
        # ----------------------------------------------------

        if action == "basic":

            damage = self.basic_attack(

                attacker,

                defender

            )

        # ----------------------------------------------------
        # SPECIAL
        # ----------------------------------------------------

        elif action == "special":

            damage = self.special_attack(

                attacker,

                defender

            )

        # ----------------------------------------------------
        # SWITCH
        # ----------------------------------------------------

        elif action == "switch":

            previous = team.active_character()

            switched = self.switch_character(

                team,

                agent

            )

            damage = 0.0

            return {

                "attacker":
                    self.get_name(
                        previous
                    ),

                "defender":
                    self.get_name(
                        defender
                    ),

                "action":
                    "switch",

                "damage":
                    0.0,

                "defender_hp":
                    self.get_hp(
                        defender
                    ),

                "switched_to":
                    self.get_name(
                        switched
                    )
                    if switched
                    else None

            }

        # ----------------------------------------------------
        # SAFETY FALLBACK
        # ----------------------------------------------------

        else:

            action = "basic"

            damage = self.basic_attack(

                attacker,

                defender

            )

        # ----------------------------------------------------
        # Return action information
        # ----------------------------------------------------

        return {

            "attacker":
                self.get_name(
                    attacker
                ),

            "defender":
                self.get_name(
                    defender
                ),

            "action":
                action,

            "damage":
                round(
                    damage,
                    2
                ),

            "defender_hp":
                round(
                    self.get_hp(
                        defender
                    ),
                    2
                )

        }

    # ========================================================
    # DETERMINE INITIATIVE
    # ========================================================

    def initiative(
        self,
        character
    ):

        # ----------------------------------------------------
        # Try speed-related fields
        # ----------------------------------------------------

        speed = getattr(

            character,

            "speed",

            None

        )

        if speed is None:

            speed = getattr(

                character,

                "initiative",

                None

            )

        if speed is None:

            speed = 50

        speed = self.safe_float(

            speed,

            50

        )

        # Add small randomness.
        return (

            speed

            +

            random.uniform(
                0,
                20
            )

        )

    # ========================================================
    # UPDATE OBJECTIVE
    # ========================================================

    def update_objective(self):

        objective = str(

            getattr(

                self.arena,

                "objective",

                "Eliminate"

            )

        ).lower()

        # ----------------------------------------------------
        # Elimination
        # ----------------------------------------------------

        if "eliminate" in objective:

            self.player_a.objective_progress = (

                1.0
                if self.player_b.has_lost()
                else 0.0

            )

            self.player_b.objective_progress = (

                1.0
                if self.player_a.has_lost()
                else 0.0

            )

            return

        # ----------------------------------------------------
        # Control zones
        # ----------------------------------------------------

        if (
            "control"
            in objective
        ):

            # Living characters provide control pressure.
            a_alive = (
                self.player_a
                .remaining_characters()
            )

            b_alive = (
                self.player_b
                .remaining_characters()
            )

            total = (
                a_alive
                +
                b_alive
            )

            if total > 0:

                self.player_a.objective_progress += (

                    a_alive
                    /
                    total
                    *
                    0.02

                )

                self.player_b.objective_progress += (

                    b_alive
                    /
                    total
                    *
                    0.02

                )

        # ----------------------------------------------------
        # Survival
        # ----------------------------------------------------

        elif (
            "survival"
            in objective
        ):

            if not self.player_a.has_lost():

                self.player_a.objective_progress += 0.01

            if not self.player_b.has_lost():

                self.player_b.objective_progress += 0.01

        # ----------------------------------------------------
        # Protect / Escort / Collect
        # ----------------------------------------------------

        else:

            if not self.player_a.has_lost():

                self.player_a.objective_progress += 0.005

            if not self.player_b.has_lost():

                self.player_b.objective_progress += 0.005

        # Keep within 0-1.
        self.player_a.objective_progress = min(

            1.0,

            self.player_a.objective_progress

        )

        self.player_b.objective_progress = min(

            1.0,

            self.player_b.objective_progress

        )

    # ========================================================
    # RUN TURN
    # ========================================================

    def run_turn(self):

        self.turn += 1

        # ----------------------------------------------------
        # Get active characters
        # ----------------------------------------------------

        attacker_a = (
            self.player_a
            .active_character()
        )

        attacker_b = (
            self.player_b
            .active_character()
        )

        # ----------------------------------------------------
        # Check whether battle is already over
        # ----------------------------------------------------

        if (
            attacker_a is None
            or
            attacker_b is None
        ):

            return

        # ----------------------------------------------------
        # Determine initiative
        # ----------------------------------------------------

        initiative_a = (
            self.initiative(
                attacker_a
            )
        )

        initiative_b = (
            self.initiative(
                attacker_b
            )
        )

        # ----------------------------------------------------
        # Determine attack order
        # ----------------------------------------------------

        if initiative_a >= initiative_b:

            first = (

                self.player_a,

                self.player_b,

                self.agent_a

            )

            second = (

                self.player_b,

                self.player_a,

                self.agent_b

            )

        else:

            first = (

                self.player_b,

                self.player_a,

                self.agent_b

            )

            second = (

                self.player_a,

                self.player_b,

                self.agent_a

            )

        actions = []

        # ====================================================
        # FIRST ACTION
        # ====================================================

        first_attacker = (
            first[0].active_character()
        )

        first_defender = (
            first[1].active_character()
        )

        if (

            first_attacker is not None

            and

            first_defender is not None

            and

            self.is_alive(
                first_attacker
            )

            and

            self.is_alive(
                first_defender
            )

        ):

            result = self.execute_action(

                first[2],

                first[0],

                first_attacker,

                first_defender

            )

            actions.append(result)

            # ------------------------------------------------
            # Inform opponent AI
            # ------------------------------------------------

            if result["action"] in [

                "basic",

                "special"

            ]:

                second[2].observe_opponent_action(

                    result["action"],

                    target=first_attacker,

                    damage=result["damage"]

                )

        # ====================================================
        # SECOND ACTION
        # ====================================================

        # If first attack killed the second player's
        # character, select the newly active character.

        second_attacker = (
            second[0].active_character()
        )

        second_defender = (
            second[1].active_character()
        )

        if (

            second_attacker is not None

            and

            second_defender is not None

            and

            self.is_alive(
                second_attacker
            )

            and

            self.is_alive(
                second_defender
            )

        ):

            result = self.execute_action(

                second[2],

                second[0],

                second_attacker,

                second_defender

            )

            actions.append(result)

            # ------------------------------------------------
            # Inform opponent AI
            # ------------------------------------------------

            if result["action"] in [

                "basic",

                "special"

            ]:

                first[2].observe_opponent_action(

                    result["action"],

                    target=second_attacker,

                    damage=result["damage"]

                )

        # ----------------------------------------------------
        # Update objective
        # ----------------------------------------------------

        self.update_objective()

        # ----------------------------------------------------
        # Store turn history
        # ----------------------------------------------------

        self.history.append({

            "turn":
                self.turn,

            "actions":
                actions,

            "player_a_alive":
                self.player_a
                .remaining_characters(),

            "player_b_alive":
                self.player_b
                .remaining_characters(),

            "player_a_objective":
                round(
                    self.player_a
                    .objective_progress,
                    4
                ),

            "player_b_objective":
                round(
                    self.player_b
                    .objective_progress,
                    4
                )

        })

    # ========================================================
    # CHECK WINNER
    # ========================================================

    def check_winner(self):

        a_lost = (
            self.player_a.has_lost()
        )

        b_lost = (
            self.player_b.has_lost()
        )

        # ----------------------------------------------------
        # Player B wins
        # ----------------------------------------------------

        if a_lost and not b_lost:

            return "Player B"

        # ----------------------------------------------------
        # Player A wins
        # ----------------------------------------------------

        if b_lost and not a_lost:

            return "Player A"

        # ----------------------------------------------------
        # Both eliminated
        # ----------------------------------------------------

        if a_lost and b_lost:

            return "Draw"

        return None

    # ========================================================
    # FORCE RESULT AT MAX TURNS
    # ========================================================

    def determine_timeout_winner(self):

        # ----------------------------------------------------
        # Remaining characters
        # ----------------------------------------------------

        remaining_a = (
            self.player_a
            .remaining_characters()
        )

        remaining_b = (
            self.player_b
            .remaining_characters()
        )

        if remaining_a > remaining_b:

            return "Player A"

        if remaining_b > remaining_a:

            return "Player B"

        # ----------------------------------------------------
        # Objective progress
        # ----------------------------------------------------

        objective_a = (
            self.player_a
            .objective_progress
        )

        objective_b = (
            self.player_b
            .objective_progress
        )

        if objective_a > objective_b:

            return "Player A"

        if objective_b > objective_a:

            return "Player B"

        # ----------------------------------------------------
        # Total HP remaining
        # ----------------------------------------------------

        hp_a = sum(

            self.get_hp(character)

            for character
            in self.player_a.characters

            if self.is_alive(character)

        )

        hp_b = sum(

            self.get_hp(character)

            for character
            in self.player_b.characters

            if self.is_alive(character)

        )

        if hp_a > hp_b:

            return "Player A"

        if hp_b > hp_a:

            return "Player B"

        return "Draw"

    # ========================================================
    # CREATE FINAL RESULT
    # ========================================================

    def create_result(self):

        return {

            "winner":
                self.winner,

            "turns":
                self.turn,

            "player_a_remaining":
                self.player_a
                .remaining_characters(),

            "player_b_remaining":
                self.player_b
                .remaining_characters(),

            "player_a_objective":
                round(

                    self.player_a
                    .objective_progress,

                    4

                ),

            "player_b_objective":
                round(

                    self.player_b
                    .objective_progress,

                    4

                ),

            "arena": {

                "weather":
                    getattr(

                        self.arena,

                        "weather",

                        None

                    ),

                "terrain":
                    getattr(

                        self.arena,

                        "terrain",

                        None

                    ),

                "objective":
                    getattr(

                        self.arena,

                        "objective",

                        None

                    ),

                "event":
                    getattr(

                        self.arena,

                        "event",

                        None

                    )

            },

            "player_a_team": [

                self.get_name(character)

                for character
                in self.player_a.characters

            ],

            "player_b_team": [

                self.get_name(character)

                for character
                in self.player_b.characters

            ],

            "battle_history":
                self.history

        }

    # ========================================================
    # RUN COMPLETE BATTLE
    # ========================================================

    def run_battle(self):

        print(
            "\n"
            + "=" * 60
        )

        print(
            "              PVP BATTLE"
        )

        print(
            "=" * 60
        )

        print(
            f"Format: "
            f"{len(self.player_a.characters)}v"
            f"{len(self.player_b.characters)}"
        )

        print(
            f"Objective: "
            f"{getattr(self.arena, 'objective', 'Unknown')}"
        )

        print(
            f"Weather: "
            f"{getattr(self.arena, 'weather', 'Unknown')}"
        )

        print(
            f"Terrain: "
            f"{getattr(self.arena, 'terrain', 'Unknown')}"
        )

        print(
            f"Event: "
            f"{getattr(self.arena, 'event', 'Unknown')}"
        )

        print(
            "=" * 60
        )

        # ----------------------------------------------------
        # Battle loop
        # ----------------------------------------------------

        while (

            self.turn
            < self.max_turns

            and

            not self.player_a.has_lost()

            and

            not self.player_b.has_lost()

        ):

            self.run_turn()

            # ------------------------------------------------
            # Display compact progress
            # ------------------------------------------------

            if (

                self.turn <= 10

                or

                self.turn % 10 == 0

            ):

                a_active = (
                    self.player_a
                    .active_character()
                )

                b_active = (
                    self.player_b
                    .active_character()
                )

                a_name = (
                    self.get_name(
                        a_active
                    )
                    if a_active
                    else "None"
                )

                b_name = (
                    self.get_name(
                        b_active
                    )
                    if b_active
                    else "None"
                )

                a_hp = (

                    round(
                        self.get_hp(
                            a_active
                        ),
                        1
                    )

                    if a_active

                    else 0

                )

                b_hp = (

                    round(
                        self.get_hp(
                            b_active
                        ),
                        1
                    )

                    if b_active

                    else 0

                )

                print(

                    f"Turn {self.turn:>3} | "

                    f"A: {a_name} "
                    f"HP={a_hp} | "

                    f"B: {b_name} "
                    f"HP={b_hp}"

                )

            # ------------------------------------------------
            # Check winner
            # ------------------------------------------------

            winner = (
                self.check_winner()
            )

            if winner is not None:

                self.winner = winner

                break

        # ----------------------------------------------------
        # Timeout
        # ----------------------------------------------------

        if self.winner is None:

            self.winner = (
                self.determine_timeout_winner()
            )

        self.finished = True

        # ----------------------------------------------------
        # Final result
        # ----------------------------------------------------

        result = (
            self.create_result()
        )

        print(
            "\n"
            + "=" * 60
        )

        print(
            "              BATTLE OVER"
        )

        print(
            "=" * 60
        )

        print(
            f"Winner: "
            f"{self.winner}"
        )

        print(
            f"Turns: "
            f"{self.turn}"
        )

        print(
            f"Player A remaining: "
            f"{result['player_a_remaining']}"
        )

        print(
            f"Player B remaining: "
            f"{result['player_b_remaining']}"
        )

        print(
            "=" * 60
        )

        return result


# ============================================================
# DISPLAY RESULT
# ============================================================

def display_result(
    result
):

    print(
        "\n"
        + "=" * 60
    )

    print(
        "             FINAL BATTLE RESULT"
    )

    print(
        "=" * 60
    )

    print(
        f"Winner              : "
        f"{result['winner']}"
    )

    print(
        f"Total turns         : "
        f"{result['turns']}"
    )

    print(
        f"Player A remaining  : "
        f"{result['player_a_remaining']}"
    )

    print(
        f"Player B remaining  : "
        f"{result['player_b_remaining']}"
    )

    print(
        f"Player A objective  : "
        f"{result['player_a_objective']}"
    )

    print(
        f"Player B objective  : "
        f"{result['player_b_objective']}"
    )

    print(
        "\nPlayer A Team:"
    )

    for character in (
        result["player_a_team"]
    ):

        print(
            f"  - {character}"
        )

    print(
        "\nPlayer B Team:"
    )

    for character in (
        result["player_b_team"]
    ):

        print(
            f"  - {character}"
        )

    print(
        "\nArena:"
    )

    for key, value in (
        result["arena"].items()
    ):

        print(
            f"  {key.capitalize():<12}: "
            f"{value}"
        )

    print(
        "=" * 60
    )


# ============================================================
# STANDALONE TEST
# ============================================================

if __name__ == "__main__":

    print(
        "\n"
        + "=" * 60
    )

    print(
        "       COMBAT ENGINE STANDALONE TEST"
    )

    print(
        "=" * 60
    )

    print(
        "\nThis test loads the dataset, builds two teams,"
    )

    print(
        "creates two AI agents and runs a complete PvP battle."
    )

    print(
        "=" * 60
    )

    try:

        # ----------------------------------------------------
        # Import project modules
        # ----------------------------------------------------

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

        # ----------------------------------------------------
        # Load data
        # ----------------------------------------------------

        print(
            "\nLoading dataset..."
        )

        df, mapping = (
            load_and_prepare_data()
        )

        print(
            f"Loaded {len(df)} characters."
        )

        # ----------------------------------------------------
        # Character model
        # ----------------------------------------------------

        character_model = (
            CharacterModel(
                df
            )
        )

        # ----------------------------------------------------
        # Arena
        # ----------------------------------------------------

        arena = PvPArena()

        # ----------------------------------------------------
        # Team builder
        # ----------------------------------------------------

        builder = TeamBuilder(

            character_model,

            arena

        )

        # ----------------------------------------------------
        # Create 3v3 teams
        # ----------------------------------------------------

        print(
            "\nBuilding Player A team..."
        )

        result_a = (
            builder.find_best_team(

                team_size=3,

                max_candidates=100

            )
        )

        print(
            "Building Player B team..."
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

        team_a = result_a["team"]

        team_b = result_b["team"]

        # ----------------------------------------------------
        # Create engine
        # ----------------------------------------------------

        engine = PvPCombatEngine(

            team_a,

            team_b,

            arena

        )

        # ----------------------------------------------------
        # Run battle
        # ----------------------------------------------------

        result = (
            engine.run_battle()
        )

        # ----------------------------------------------------
        # Display result
        # ----------------------------------------------------

        display_result(
            result
        )

        print(
            "\n"
            + "=" * 60
        )

        print(
            "      COMBAT ENGINE TEST PASSED"
        )

        print(
            "=" * 60
        )

    except Exception as error:

        print(
            "\n"
            + "=" * 60
        )

        print(
            "      COMBAT ENGINE TEST FAILED"
        )

        print(
            "=" * 60
        )

        print(
            f"\nError: {error}"
        )

        print(
            "\nCheck that the previous modules are present"
        )

        print(
            "and that their class/function names match."
        )