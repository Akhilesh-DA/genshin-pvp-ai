# ============================================================
# GENSHIN IMPACT PVP AI
# AI Training Module
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
# TRAINING CONFIGURATION
# ============================================================

NUM_EPISODES = 500

TEAM_SIZE = 3

OUTPUT_DIR = "../outputs"

MODEL_FILE = os.path.join(
    OUTPUT_DIR,
    "training_results.json"
)


# ============================================================
# TRAINING STATISTICS
# ============================================================

class TrainingStatistics:

    def __init__(self):

        self.games = 0

        self.player_a_wins = 0

        self.player_b_wins = 0

        self.draws = 0

        self.total_turns = 0

        self.rewards = []

        self.action_counts = {

            "basic": 0,

            "special": 0,

            "switch": 0

        }


    # --------------------------------------------------------
    # RECORD RESULT
    # --------------------------------------------------------

    def record_game(
        self,
        result,
        agent
    ):

        self.games += 1

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


        # ----------------------------------------------------
        # Record AI actions
        # ----------------------------------------------------

        for decision in agent.decision_history:

            action = decision.get(
                "action"
            )

            if action in self.action_counts:

                self.action_counts[action] += 1


    # --------------------------------------------------------
    # AVERAGE TURNS
    # --------------------------------------------------------

    def average_turns(self):

        if self.games == 0:

            return 0

        return (
            self.total_turns
            /
            self.games
        )


    # --------------------------------------------------------
    # WIN RATE
    # --------------------------------------------------------

    def player_a_win_rate(self):

        if self.games == 0:

            return 0

        return (
            self.player_a_wins
            /
            self.games
        )


    # --------------------------------------------------------
    # DISPLAY
    # --------------------------------------------------------

    def display(self):

        print(
            "\n========================================"
        )

        print(
            "       TRAINING STATISTICS"
        )

        print(
            "========================================"
        )

        print(
            f"Games played      : {self.games}"
        )

        print(
            f"Player A wins     : {self.player_a_wins}"
        )

        print(
            f"Player B wins     : {self.player_b_wins}"
        )

        print(
            f"Draws             : {self.draws}"
        )

        print(
            f"Player A win rate : "
            f"{self.player_a_win_rate():.3f}"
        )

        print(
            f"Average turns     : "
            f"{self.average_turns():.2f}"
        )

        print(
            "\nAction usage:"
        )

        for action, count in (
            self.action_counts.items()
        ):

            print(
                f"{action:<15}: {count}"
            )


# ============================================================
# REWARD FUNCTION
# ============================================================

def calculate_reward(
    result,
    player
):
    """
    Calculate a reward for the AI.

    Positive reward:
        - Winning
        - Remaining characters
        - Objective progress

    Negative reward:
        - Losing
        - Long inefficient battles
    """

    winner = result["winner"]


    # --------------------------------------------------------
    # Winner reward
    # --------------------------------------------------------

    if winner == player:

        reward = 100.0

    elif winner == "Draw":

        reward = 10.0

    else:

        reward = -100.0


    # --------------------------------------------------------
    # Remaining characters
    # --------------------------------------------------------

    if player == "Player A":

        remaining = (
            result["player_a_remaining"]
        )

        objective = (
            result["player_a_objective"]
        )

    else:

        remaining = (
            result["player_b_remaining"]
        )

        objective = (
            result["player_b_objective"]
        )


    reward += (
        remaining
        *
        10
    )


    # --------------------------------------------------------
    # Objective reward
    # --------------------------------------------------------

    reward += (
        objective
        *
        20
    )


    # --------------------------------------------------------
    # Efficiency penalty
    # --------------------------------------------------------

    reward -= (
        result["turns"]
        *
        0.05
    )


    return reward


# ============================================================
# CREATE TEAMS
# ============================================================

def create_teams(
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
# RUN ONE EPISODE
# ============================================================

def run_episode(
    character_model
):

    # --------------------------------------------------------
    # New arena for every game
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
    # Generate teams
    # --------------------------------------------------------

    team_a, team_b = create_teams(

        builder,

        TEAM_SIZE

    )


    if team_a is None:

        return None, None


    # --------------------------------------------------------
    # Combat engine
    # --------------------------------------------------------

    engine = PvPCombatEngine(

        team_a,

        team_b,

        arena

    )


    # --------------------------------------------------------
    # AI agents
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
    # Battle
    # --------------------------------------------------------

    result = engine.run_battle()


    # --------------------------------------------------------
    # Rewards
    # --------------------------------------------------------

    reward_a = calculate_reward(

        result,

        "Player A"

    )


    reward_b = calculate_reward(

        result,

        "Player B"

    )


    agent_a_reward = {

        "reward": reward_a,

        "winner": result["winner"],

        "turns": result["turns"]

    }


    agent_b_reward = {

        "reward": reward_b,

        "winner": result["winner"],

        "turns": result["turns"]

    }


    return (

        result,

        {

            "agent_a": agent_a,

            "agent_b": agent_b,

            "agent_a_reward":
                agent_a_reward,

            "agent_b_reward":
                agent_b_reward

        }

    )


# ============================================================
# SAVE TRAINING RESULTS
# ============================================================

def save_training_results(
    statistics,
    episode_rewards
):

    os.makedirs(
        OUTPUT_DIR,
        exist_ok=True
    )


    data = {

        "episodes":
            statistics.games,

        "player_a_wins":
            statistics.player_a_wins,

        "player_b_wins":
            statistics.player_b_wins,

        "draws":
            statistics.draws,

        "player_a_win_rate":
            statistics.player_a_win_rate(),

        "average_turns":
            statistics.average_turns(),

        "action_counts":
            statistics.action_counts,

        "episode_rewards":
            episode_rewards

    }


    with open(
        MODEL_FILE,
        "w"
    ) as file:

        json.dump(
            data,
            file,
            indent=4
        )


    print(
        f"\nTraining results saved to:"
    )

    print(
        MODEL_FILE
    )


# ============================================================
# TRAINING LOOP
# ============================================================

def train():

    print(
        "\n========================================"
    )

    print(
        "      GENSHIN PVP AI TRAINING"
    )

    print(
        "========================================"
    )


    print(
        f"\nEpisodes: {NUM_EPISODES}"

    )

    print(
        f"Team size: {TEAM_SIZE}"
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
        f"Dataset loaded: "
        f"{len(df)} characters"
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
    # Statistics
    # --------------------------------------------------------

    statistics = (
        TrainingStatistics()
    )


    episode_rewards = []


    # ========================================================
    # EPISODE LOOP
    # ========================================================

    for episode in range(
        1,
        NUM_EPISODES + 1
    ):

        try:

            result, agents = (
                run_episode(
                    character_model
                )
            )


            if result is None:

                print(
                    f"Episode {episode} "
                    f"could not be completed."
                )

                continue


            # ------------------------------------------------
            # Record statistics
            # ------------------------------------------------

            statistics.record_game(

                result,

                agents["agent_a"]

            )


            reward_a = (
                agents[
                    "agent_a_reward"
                ]["reward"]
            )


            reward_b = (
                agents[
                    "agent_b_reward"
                ]["reward"]
            )


            episode_rewards.append({

                "episode":
                    episode,

                "reward_a":
                    reward_a,

                "reward_b":
                    reward_b

            })


            # ------------------------------------------------
            # Progress display
            # ------------------------------------------------

            if (
                episode % 10 == 0
                or
                episode == 1
            ):

                print(
                    f"\nEpisode "
                    f"{episode}/{NUM_EPISODES}"
                )

                print(
                    f"Winner: "
                    f"{result['winner']}"
                )

                print(
                    f"Turns: "
                    f"{result['turns']}"
                )

                print(
                    f"Reward A: "
                    f"{reward_a:.2f}"
                )

                print(
                    f"Reward B: "
                    f"{reward_b:.2f}"
                )


        except Exception as error:

            print(
                f"\nEpisode {episode} "
                f"failed:"
            )

            print(
                error
            )


    # ========================================================
    # FINAL RESULTS
    # ========================================================

    statistics.display()


    save_training_results(

        statistics,

        episode_rewards

    )


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    train()