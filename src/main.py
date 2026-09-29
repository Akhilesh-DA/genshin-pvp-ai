# ============================================================
# GENSHIN IMPACT PVP AI
# MAIN PROGRAM
# ============================================================

import os
import sys


# ============================================================
# IMPORT PROJECT MODULES
# ============================================================

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
    PvPCombatEngine,
    display_result
)


# ============================================================
# DISPLAY HEADER
# ============================================================

def display_header():

    print(
        "\n"
        + "=" * 60
    )

    print(
        "        GENSHIN IMPACT PVP AI SYSTEM"
    )

    print(
        "=" * 60
    )

    print(
        "Adaptive AI for Dynamic PvP Combat"
    )

    print(
        "=" * 60
    )


# ============================================================
# LOAD SYSTEM
# ============================================================

def load_system():

    print(
        "\n[1] Loading Genshin Impact dataset..."
    )

    df, mapping = (
        load_and_prepare_data()
    )

    print(
        f"    Characters loaded: {len(df)}"
    )


    print(
        "\n[2] Creating character model..."
    )

    character_model = (
        CharacterModel(
            df
        )
    )

    print(
        "    Character model ready."
    )


    return character_model


# ============================================================
# CREATE BATTLE
# ============================================================

def create_battle(
    character_model,
    team_size
):

    print(
        "\n[3] Creating dynamic PvP arena..."
    )

    arena = PvPArena()

    arena.display()


    print(
        "\n[4] Building Player A team..."
    )

    builder = TeamBuilder(

        character_model,

        arena

    )


    result_a = (
        builder.find_best_team(

            team_size=team_size,

            max_candidates=100

        )
    )


    if result_a is None:

        raise RuntimeError(
            "Unable to create Player A team."
        )


    print(
        "\n[5] Building Player B team..."
    )


    result_b = (
        builder.find_best_team(

            team_size=team_size,

            max_candidates=100

        )
    )


    if result_b is None:

        raise RuntimeError(
            "Unable to create Player B team."
        )


    team_a = result_a["team"]

    team_b = result_b["team"]


    print(
        "\nPLAYER A TEAM"
    )

    print(
        "-" * 40
    )

    builder.display_team(
        team_a
    )


    print(
        "\nPLAYER B TEAM"
    )

    print(
        "-" * 40
    )

    builder.display_team(
        team_b
    )


    # --------------------------------------------------------
    # Create combat engine
    # --------------------------------------------------------

    print(
        "\n[6] Initializing PvP AI agents..."
    )


    engine = PvPCombatEngine(

        team_a,

        team_b,

        arena

    )


    print(
        "    Player A AI ready."
    )

    print(
        "    Player B AI ready."
    )


    return engine


# ============================================================
# RUN BATTLE
# ============================================================

def run_battle(
    engine
):

    print(
        "\n[7] Starting PvP battle..."
    )

    print(
        "=" * 60
    )


    result = (
        engine.run_battle()
    )


    display_result(
        result
    )


    return result


# ============================================================
# DISPLAY AI INFORMATION
# ============================================================

def display_ai_information(
    engine
):

    print(
        "\n"
        + "=" * 60
    )

    print(
        "              AI INFORMATION"
    )

    print(
        "=" * 60
    )


    print(
        "\nPlayer A AI:"
    )

    print(
        "Strategy model:"
    )

    print(
        engine.agent_a
        .opponent_model
        .classify_strategy()
    )


    print(
        "Opponent observations:"
    )

    print(
        engine.agent_a
        .opponent_model
        .total_actions
    )


    print(
        "\nPlayer B AI:"
    )

    print(
        "Strategy model:"
    )

    print(
        engine.agent_b
        .opponent_model
        .classify_strategy()
    )


    print(
        "Opponent observations:"
    )

    print(
        engine.agent_b
        .opponent_model
        .total_actions
    )


# ============================================================
# SAVE BATTLE RESULT
# ============================================================

def save_result(
    result
):

    output_dir = "../outputs"

    os.makedirs(
        output_dir,
        exist_ok=True
    )


    output_file = os.path.join(

        output_dir,

        "latest_battle.json"

    )


    import json


    with open(
        output_file,
        "w"
    ) as file:

        json.dump(

            result,

            file,

            indent=4,

            default=str

        )


    print(
        f"\nBattle result saved to:"
    )

    print(
        output_file
    )


# ============================================================
# MAIN
# ============================================================

def main():

    display_header()


    # --------------------------------------------------------
    # Select team size
    # --------------------------------------------------------

    print(
        "\nSelect PvP format:"
    )

    print(
        "1  →  1v1"
    )

    print(
        "2  →  2v2"
    )

    print(
        "3  →  3v3"
    )

    print(
        "4  →  4v4"
    )


    choice = input(
        "\nEnter team size [1-4]: "
    ).strip()


    if choice not in [
        "1",
        "2",
        "3",
        "4"
    ]:

        print(
            "\nInvalid choice."
        )

        print(
            "Defaulting to 3v3."
        )

        team_size = 3

    else:

        team_size = int(
            choice
        )


    # --------------------------------------------------------
    # Load system
    # --------------------------------------------------------

    character_model = (
        load_system()
    )


    # --------------------------------------------------------
    # Create battle
    # --------------------------------------------------------

    engine = create_battle(

        character_model,

        team_size

    )


    # --------------------------------------------------------
    # Run battle
    # --------------------------------------------------------

    result = run_battle(
        engine
    )


    # --------------------------------------------------------
    # AI information
    # --------------------------------------------------------

    display_ai_information(
        engine
    )


    # --------------------------------------------------------
    # Save result
    # --------------------------------------------------------

    save_result(
        result
    )


    print(
        "\n"
        + "=" * 60
    )

    print(
        "             SYSTEM COMPLETED"
    )

    print(
        "=" * 60
    )


# ============================================================
# PROGRAM ENTRY
# ============================================================

if __name__ == "__main__":

    main()