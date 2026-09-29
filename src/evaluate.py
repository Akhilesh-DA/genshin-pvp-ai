# ============================================================
# GENSHIN IMPACT PVP AI
# Evaluation Module
# ============================================================

import os
import json
import random
import numpy as np

from data_loader import load_and_prepare_data
from character_model import CharacterModel
from arena import PvPArena
from team_builder import TeamBuilder
from combat_engine import PvPCombatEngine
from ai_agent import PvPAgent


# ============================================================
# CONFIGURATION
# ============================================================

MATCHES_PER_FORMAT = 50

TEAM_SIZES = [
    1,
    2,
    3,
    4
]

OUTPUT_DIR = "../outputs"

RESULT_FILE = os.path.join(
    OUTPUT_DIR,
    "evaluation_results.json"
)


# ============================================================
# EVALUATION STATISTICS
# ============================================================

class EvaluationStatistics:

    def __init__(
        self,
        team_size
    ):

        self.team_size = team_size

        self.matches = 0

        self.player_a_wins = 0

        self.player_b_wins = 0

        self.draws = 0

        self.total_turns = 0

        self.total_remaining_a = 0

        self.total_remaining_b = 0

        self.total_objective_a = 0

        self.total_objective_b = 0


    # --------------------------------------------------------
    # RECORD MATCH
    # --------------------------------------------------------

    def record(
        self,
        result
    ):

        self.matches += 1

        winner = result["winner"]


        if winner == "Player A":

            self.player_a_wins += 1

        elif winner == "Player B":

            self.player_b_wins += 1

        else:

            self.draws += 1


        self.total_turns += (
            result["turns"]
        )


        self.total_remaining_a += (
            result["player_a_remaining"]
        )


        self.total_remaining_b += (
            result["player_b_remaining"]
        )


        self.total_objective_a += (
            result["player_a_objective"]
        )


        self.total_objective_b += (
            result["player_b_objective"]
        )


    # --------------------------------------------------------
    # WIN RATE
    # --------------------------------------------------------

    def win_rate(self):

        if self.matches == 0:

            return 0

        return (
            self.player_a_wins
            /
            self.matches
        )


    # --------------------------------------------------------
    # AVERAGE TURNS
    # --------------------------------------------------------

    def average_turns(self):

        if self.matches == 0:

            return 0

        return (
            self.total_turns
            /
            self.matches
        )


    # --------------------------------------------------------
    # AVERAGE REMAINING
    # --------------------------------------------------------

    def average_remaining_a(self):

        if self.matches == 0:

            return 0

        return (
            self.total_remaining_a
            /
            self.matches
        )


    def average_remaining_b(self):

        if self.matches == 0:

            return 0

        return (
            self.total_remaining_b
            /
            self.matches
        )


    # --------------------------------------------------------
    # AVERAGE OBJECTIVE
    # --------------------------------------------------------

    def average_objective_a(self):

        if self.matches == 0:

            return 0

        return (
            self.total_objective_a
            /
            self.matches
        )


    def average_objective_b(self):

        if self.matches == 0:

            return 0

        return (
            self.total_objective_b
            /
            self.matches
        )


    # --------------------------------------------------------
    # CONVERT TO DICTIONARY
    # --------------------------------------------------------

    def to_dict(self):

        return {

            "team_size":
                self.team_size,

            "format":
                f"{self.team_size}v{self.team_size}",

            "matches":
                self.matches,

            "player_a_wins":
                self.player_a_wins,

            "player_b_wins":
                self.player_b_wins,

            "draws":
                self.draws,

            "player_a_win_rate":
                self.win_rate(),

            "average_turns":
                self.average_turns(),

            "average_remaining_a":
                self.average_remaining_a(),

            "average_remaining_b":
                self.average_remaining_b(),

            "average_objective_a":
                self.average_objective_a(),

            "average_objective_b":
                self.average_objective_b()

        }


# ============================================================
# BUILD TEAMS
# ============================================================

def build_teams(
    builder,
    team_size
):

    result_a = (
        builder.find_best_team(
            team_size=team_size,
            max_candidates=100
        )
    )


    result_b = (
        builder.find_best_team(
            team_size=team_size,
            max_candidates=100
        )
    )


    if result_a is None:

        return None, None


    if result_b is None:

        return None, None


    return (
        result_a["team"],
        result_b["team"]
    )


# ============================================================
# RUN MATCH
# ============================================================

def run_match(
    character_model,
    team_size
):

    # --------------------------------------------------------
    # Create a new dynamic arena
    # --------------------------------------------------------

    arena = PvPArena()


    # --------------------------------------------------------
    # Team builder
    # --------------------------------------------------------

    builder = TeamBuilder(

        character_model,

        arena

    )


    # --------------------------------------------------------
    # Create teams
    # --------------------------------------------------------

    team_a, team_b = build_teams(

        builder,

        team_size

    )


    if team_a is None:

        return None


    # --------------------------------------------------------
    # Combat engine
    # --------------------------------------------------------

    engine = PvPCombatEngine(

        team_a,

        team_b,

        arena

    )


    # --------------------------------------------------------
    # Create AI agents
    # --------------------------------------------------------

    agent_a = PvPAgent(

        name="Player A AI",

        team=engine.player_a.characters,

        arena=arena

    )


    agent_b = PvPAgent(

        name="Player B AI",

        team=engine.player_b.characters,

        arena=arena

    )


    # --------------------------------------------------------
    # Run battle
    # --------------------------------------------------------

    result = engine.run_battle()


    # --------------------------------------------------------
    # Store additional information
    # --------------------------------------------------------

    result["arena"] = {

        "weather":
            arena.weather,

        "terrain":
            arena.terrain,

        "objective":
            arena.objective,

        "event":
            arena.event

    }


    result["agent_a"] = {

        "strategy":
            agent_a.opponent_model
            .classify_strategy(),

        "decisions":
            len(
                agent_a.decision_history
            )

    }


    result["agent_b"] = {

        "strategy":
            agent_b.opponent_model
            .classify_strategy(),

        "decisions":
            len(
                agent_b.decision_history
            )

    }


    return result


# ============================================================
# EVALUATE ONE FORMAT
# ============================================================

def evaluate_format(
    character_model,
    team_size,
    number_of_matches
):

    statistics = (
        EvaluationStatistics(
            team_size
        )
    )


    print(
        "\n========================================"
    )

    print(
        f"Evaluating "
        f"{team_size}v{team_size}"
    )

    print(
        "========================================"
    )


    for match in range(
        1,
        number_of_matches + 1
    ):

        try:

            result = run_match(

                character_model,

                team_size

            )


            if result is None:

                print(
                    f"Match {match} failed."
                )

                continue


            statistics.record(
                result
            )


            # ------------------------------------------------
            # Progress
            # ------------------------------------------------

            if (
                match % 10 == 0
                or
                match == 1
            ):

                print(

                    f"Match "
                    f"{match}/"
                    f"{number_of_matches} "
                    f"| Winner: "
                    f"{result['winner']} "
                    f"| Turns: "
                    f"{result['turns']}"

                )


        except Exception as error:

            print(
                f"Match {match} error:"
            )

            print(
                error
            )


    return statistics


# ============================================================
# EVALUATE ALL FORMATS
# ============================================================

def evaluate_all():

    print(
        "\n========================================"
    )

    print(
        "      GENSHIN PVP AI EVALUATION"
    )

    print(
        "========================================"
    )


    # --------------------------------------------------------
    # Load dataset
    # --------------------------------------------------------

    print(
        "\nLoading dataset..."
    )


    df, mapping = (
        load_and_prepare_data()
    )


    print(
        f"Characters loaded: "
        f"{len(df)}"
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
    # Results
    # --------------------------------------------------------

    all_results = {}


    # --------------------------------------------------------
    # Evaluate 1v1, 2v2, 3v3, 4v4
    # --------------------------------------------------------

    for team_size in TEAM_SIZES:

        statistics = evaluate_format(

            character_model,

            team_size,

            MATCHES_PER_FORMAT

        )


        statistics_dict = (
            statistics.to_dict()
        )


        all_results[
            f"{team_size}v{team_size}"
        ] = statistics_dict


        print(
            "\nCompleted "
            f"{team_size}v{team_size}"
        )

        print(
            f"Matches: "
            f"{statistics.matches}"
        )

        print(
            f"Player A wins: "
            f"{statistics.player_a_wins}"
        )

        print(
            f"Player B wins: "
            f"{statistics.player_b_wins}"
        )

        print(
            f"Draws: "
            f"{statistics.draws}"
        )

        print(
            f"Player A win rate: "
            f"{statistics.win_rate():.3f}"
        )


    # --------------------------------------------------------
    # Save results
    # --------------------------------------------------------

    os.makedirs(
        OUTPUT_DIR,
        exist_ok=True
    )


    with open(
        RESULT_FILE,
        "w"
    ) as file:

        json.dump(
            all_results,
            file,
            indent=4
        )


    print(
        "\n========================================"
    )

    print(
        "       EVALUATION COMPLETED"
    )

    print(
        "========================================"
    )


    print(
        f"\nResults saved to:"
    )

    print(
        RESULT_FILE
    )


    # --------------------------------------------------------
    # Final summary
    # --------------------------------------------------------

    print(
        "\nFORMAT SUMMARY"
    )

    print(
        "----------------------------------------"
    )


    for format_name, data in (
        all_results.items()
    ):

        print(

            f"{format_name:<8} "
            f"| Win Rate: "
            f"{data['player_a_win_rate']:.3f} "
            f"| Avg Turns: "
            f"{data['average_turns']:.2f}"

        )


    return all_results


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    evaluate_all()