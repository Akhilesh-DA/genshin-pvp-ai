# ============================================================
# GENSHIN IMPACT PVP AI
# Team Builder Module
# ============================================================

import random
import itertools
import numpy as np

from data_loader import load_and_prepare_data
from character_model import CharacterModel
from arena import PvPArena


# ------------------------------------------------------------
# TEAM BUILDER
# ------------------------------------------------------------

class TeamBuilder:
    """
    Builds PvP teams using strategic factors instead of
    simply selecting the strongest characters.

    Supported team sizes:

        1v1
        2v2
        3v3
        4v4

    The architecture can later be extended to NvN.
    """

    def __init__(
        self,
        character_model,
        arena
    ):

        self.character_model = character_model

        self.arena = arena

        self.characters = (
            character_model.get_all_characters()
        )


    # --------------------------------------------------------
    # TEAM SIZE VALIDATION
    # --------------------------------------------------------

    def validate_team_size(
        self,
        team_size
    ):
        """
        Validate requested team size.
        """

        if team_size < 1:

            raise ValueError(
                "Team size must be at least 1."
            )

        if team_size > len(
            self.characters
        ):

            raise ValueError(
                "Team size is larger than "
                "the number of available characters."
            )

        return True


    # --------------------------------------------------------
    # ROLE BALANCE
    # --------------------------------------------------------

    def calculate_role_balance(
        self,
        team
    ):
        """
        Evaluate role diversity.

        A team containing only one type of character
        can become predictable.

        The builder therefore rewards complementary roles.
        """

        if not team:

            return 0.0


        roles = [

            str(
                character.get(
                    "role",
                    "Unknown"
                )
            ).lower()

            for character in team

        ]


        score = 0.0


        # ----------------------------------------------------
        # Count role categories
        # ----------------------------------------------------

        has_dps = any(
            "dps" in role
            or "offensive" in role
            for role in roles
        )

        has_support = any(
            "support" in role
            for role in roles
        )

        has_survivability = any(
            "surviv" in role
            for role in roles
        )


        # ----------------------------------------------------
        # Reward complementary roles
        # ----------------------------------------------------

        if has_dps:

            score += 0.30


        if has_support:

            score += 0.30


        if has_survivability:

            score += 0.30


        # Small reward for multiple roles

        unique_roles = len(
            set(roles)
        )

        score += min(
            unique_roles * 0.05,
            0.10
        )


        return float(
            np.clip(
                score,
                0,
                1
            )
        )


    # --------------------------------------------------------
    # ELEMENT DIVERSITY
    # --------------------------------------------------------

    def calculate_element_diversity(
        self,
        team
    ):
        """
        Measure elemental diversity.

        Diversity can make a team less vulnerable
        to a single environmental condition.
        """

        if not team:

            return 0.0


        elements = [

            str(
                character.get(
                    "element",
                    "Unknown"
                )
            ).lower()

            for character in team

        ]


        known_elements = [

            element

            for element in elements

            if element != "unknown"

        ]


        if not known_elements:

            return 0.5


        unique_elements = len(
            set(
                known_elements
            )
        )


        diversity = (
            unique_elements
            /
            len(team)
        )


        return float(
            np.clip(
                diversity,
                0,
                1
            )
        )


    # --------------------------------------------------------
    # ELEMENTAL SYNERGY
    # --------------------------------------------------------

    def calculate_elemental_synergy(
        self,
        team
    ):
        """
        Estimate elemental synergy.

        This is intentionally simplified at this stage.

        More detailed elemental interaction logic will be
        introduced later in the combat simulator.
        """

        if len(team) <= 1:

            return 0.50


        elements = [

            str(
                character.get(
                    "element",
                    "Unknown"
                )
            ).lower()

            for character in team

        ]


        score = 0.50


        # ----------------------------------------------------
        # Repeated elements can provide consistency
        # ----------------------------------------------------

        counts = {}

        for element in elements:

            counts[element] = (
                counts.get(
                    element,
                    0
                )
                + 1
            )


        largest_group = max(
            counts.values()
        )


        # Moderate repetition is rewarded.
        # Excessive repetition is penalized.

        if largest_group == 2:

            score += 0.15

        elif largest_group >= 3:

            score -= 0.05


        # ----------------------------------------------------
        # Elemental diversity
        # ----------------------------------------------------

        if len(
            set(elements)
        ) >= 3:

            score += 0.15


        return float(
            np.clip(
                score,
                0,
                1
            )
        )


    # --------------------------------------------------------
    # FLEXIBILITY
    # --------------------------------------------------------

    def calculate_team_flexibility(
        self,
        team
    ):
        """
        Measure how adaptable the team is.
        """

        if not team:

            return 0.0


        flexibility_scores = [

            float(
                character.get(
                    "flexibility_score",
                    0.5
                )
            )

            for character in team

        ]


        return float(
            np.mean(
                flexibility_scores
            )
        )


    # --------------------------------------------------------
    # TEAM RISK
    # --------------------------------------------------------

    def calculate_team_risk(
        self,
        team
    ):
        """
        Calculate team-level strategic risk.

        A team composed entirely of high-risk characters
        receives a higher risk value.
        """

        if not team:

            return 1.0


        risk_scores = [

            float(
                character.get(
                    "risk_score",
                    0.5
                )
            )

            for character in team

        ]


        average_risk = np.mean(
            risk_scores
        )


        # Concentration risk

        offensive_count = sum(

            (
                "dps"
                in
                str(
                    character.get(
                        "role",
                        ""
                    )
                ).lower()
            )

            for character in team

        )


        if offensive_count == len(
            team
        ):

            average_risk += 0.15


        return float(
            np.clip(
                average_risk,
                0,
                1
            )
        )


    # --------------------------------------------------------
    # RAW TEAM POWER
    # --------------------------------------------------------

    def calculate_raw_team_power(
        self,
        team
    ):
        """
        Calculate average individual PvP value.

        This is deliberately only one component
        of the final team score.
        """

        if not team:

            return 0.0


        values = [

            float(
                character.get(
                    "pvp_value",
                    0.5
                )
            )

            for character in team

        ]


        return float(
            np.mean(values)
        )


    # --------------------------------------------------------
    # ENVIRONMENT FIT
    # --------------------------------------------------------

    def calculate_environment_fit(
        self,
        team
    ):
        """
        Measure how well the team fits the current arena.
        """

        return (
            self.arena
            .calculate_team_environment_score(
                team
            )
        )


    # --------------------------------------------------------
    # OBJECTIVE FIT
    # --------------------------------------------------------

    def calculate_objective_fit(
        self,
        team
    ):
        """
        Measure how well the team fits the current
        arena objective.
        """

        return (
            self.arena
            .get_objective_value(
                team
            )
        )


    # --------------------------------------------------------
    # TEAM SCORE
    # --------------------------------------------------------

    def calculate_team_score(
        self,
        team
    ):
        """
        Calculate strategic team score.

        IMPORTANT:

        Raw character strength is NOT dominant.

        The final score considers:

            Raw power
            Role balance
            Element diversity
            Elemental synergy
            Flexibility
            Environment
            Objective
            Risk
        """

        if not team:

            return 0.0


        raw_power = (
            self.calculate_raw_team_power(
                team
            )
        )


        role_balance = (
            self.calculate_role_balance(
                team
            )
        )


        element_diversity = (
            self.calculate_element_diversity(
                team
            )
        )


        elemental_synergy = (
            self.calculate_elemental_synergy(
                team
            )
        )


        flexibility = (
            self.calculate_team_flexibility(
                team
            )
        )


        environment_fit = (
            self.calculate_environment_fit(
                team
            )
        )


        objective_fit = (
            self.calculate_objective_fit(
                team
            )
        )


        risk = (
            self.calculate_team_risk(
                team
            )
        )


        # ----------------------------------------------------
        # FINAL STRATEGIC SCORE
        # ----------------------------------------------------

        score = (

            # Individual power
            0.20 * raw_power

            # Team composition
            +
            0.15 * role_balance

            # Elemental coverage
            +
            0.10 * element_diversity

            # Elemental synergy
            +
            0.10 * elemental_synergy

            # Adaptability
            +
            0.10 * flexibility

            # Arena adaptation
            +
            0.20 * environment_fit

            # Objective understanding
            +
            0.10 * objective_fit

            # Risk management
            -
            0.05 * risk

        )


        return float(
            np.clip(
                score,
                0,
                1
            )
        )


    # --------------------------------------------------------
    # TEAM SIGNATURE
    # --------------------------------------------------------

    def team_signature(
        self,
        team
    ):
        """
        Generate a unique identifier for a team.
        """

        ids = [

            str(
                character.get(
                    "character_id"
                )
            )

            for character in team

        ]

        return tuple(
            sorted(ids)
        )


    # --------------------------------------------------------
    # BUILD RANDOM TEAM
    # --------------------------------------------------------

    def build_random_team(
        self,
        team_size
    ):
        """
        Create a random team.
        """

        self.validate_team_size(
            team_size
        )


        return random.sample(
            self.characters,
            team_size
        )


    # --------------------------------------------------------
    # GENERATE TEAM CANDIDATES
    # --------------------------------------------------------

    def generate_team_candidates(
        self,
        team_size,
        max_candidates=100
    ):
        """
        Generate candidate teams.

        For small team sizes, combinations are sampled
        or enumerated depending on the size of the
        character pool.
        """

        self.validate_team_size(
            team_size
        )


        number_of_characters = (
            len(self.characters)
        )


        total_combinations = 1


        # Calculate nCr

        from math import comb

        total_combinations = comb(

            number_of_characters,

            team_size

        )


        # ----------------------------------------------------
        # Small search space
        # ----------------------------------------------------

        if total_combinations <= max_candidates:

            candidates = list(

                itertools.combinations(

                    self.characters,

                    team_size

                )

            )

            return [

                list(team)

                for team in candidates

            ]


        # ----------------------------------------------------
        # Large search space
        # ----------------------------------------------------

        candidates = []

        signatures = set()


        attempts = 0


        while (

            len(candidates)
            <
            max_candidates

            and

            attempts
            <
            max_candidates * 10

        ):

            attempts += 1


            team = self.build_random_team(
                team_size
            )


            signature = self.team_signature(
                team
            )


            if signature not in signatures:

                signatures.add(
                    signature
                )

                candidates.append(
                    team
                )


        return candidates


    # --------------------------------------------------------
    # FIND BEST TEAM
    # --------------------------------------------------------

    def find_best_team(
        self,
        team_size,
        max_candidates=100
    ):
        """
        Search candidate teams and return the
        highest-scoring strategic team.
        """

        candidates = (
            self.generate_team_candidates(
                team_size,
                max_candidates
            )
        )


        if not candidates:

            return None


        scored_teams = []


        for team in candidates:

            score = (
                self.calculate_team_score(
                    team
                )
            )


            scored_teams.append(

                (
                    score,
                    team
                )

            )


        scored_teams.sort(

            key=lambda x:
                x[0],

            reverse=True

        )


        best_score, best_team = (
            scored_teams[0]
        )


        return {

            "team": best_team,

            "score": best_score,

            "candidates_evaluated":
                len(scored_teams)

        }


    # --------------------------------------------------------
    # GET TEAM EXPLANATION
    # --------------------------------------------------------

    def explain_team(
        self,
        team
    ):
        """
        Explain why a team received its score.
        """

        return {

            "raw_power":
                self.calculate_raw_team_power(
                    team
                ),

            "role_balance":
                self.calculate_role_balance(
                    team
                ),

            "element_diversity":
                self.calculate_element_diversity(
                    team
                ),

            "elemental_synergy":
                self.calculate_elemental_synergy(
                    team
                ),

            "flexibility":
                self.calculate_team_flexibility(
                    team
                ),

            "environment_fit":
                self.calculate_environment_fit(
                    team
                ),

            "objective_fit":
                self.calculate_objective_fit(
                    team
                ),

            "risk":
                self.calculate_team_risk(
                    team
                ),

            "final_score":
                self.calculate_team_score(
                    team
                )

        }


    # --------------------------------------------------------
    # DISPLAY TEAM
    # --------------------------------------------------------

    def display_team(
        self,
        team
    ):
        """
        Display team information.
        """

        print(
            "\n========================================"
        )

        print(
            "             SELECTED TEAM"
        )

        print(
            "========================================"
        )


        for index, character in enumerate(

            team,

            start=1

        ):

            print(

                f"{index}. "
                f"{character.get('name', 'Unknown')} "
                f"| "
                f"{character.get('element', 'Unknown')} "
                f"| "
                f"{character.get('role', 'Unknown')}"

            )


        print(
            "\nTeam explanation:"
        )


        explanation = (
            self.explain_team(
                team
            )
        )


        for key, value in (
            explanation.items()
        ):

            print(

                f"  {key:<22}: "
                f"{value:.3f}"

            )


# ------------------------------------------------------------
# STANDALONE TEST
# ------------------------------------------------------------

if __name__ == "__main__":

    print(
        "\n========================================"
    )

    print(
        " TEAM BUILDER TEST"
    )

    print(
        "========================================"
    )


    # --------------------------------------------------------
    # Load character dataset
    # --------------------------------------------------------

    df, mapping = (
        load_and_prepare_data()
    )


    # --------------------------------------------------------
    # Create character model
    # --------------------------------------------------------

    character_model = (
        CharacterModel(
            df
        )
    )


    # --------------------------------------------------------
    # Create random arena
    # --------------------------------------------------------

    arena = PvPArena()


    arena.display()


    # --------------------------------------------------------
    # Create team builder
    # --------------------------------------------------------

    builder = TeamBuilder(

        character_model,

        arena

    )


    # --------------------------------------------------------
    # Test 1v1
    # --------------------------------------------------------

    print(
        "\n\n========== 1v1 TEST =========="
    )


    result_1v1 = (
        builder.find_best_team(
            team_size=1,
            max_candidates=50
        )
    )


    if result_1v1:

        builder.display_team(
            result_1v1["team"]
        )


    # --------------------------------------------------------
    # Test 2v2
    # --------------------------------------------------------

    print(
        "\n\n========== 2v2 TEST =========="
    )


    result_2v2 = (
        builder.find_best_team(
            team_size=2,
            max_candidates=100
        )
    )


    if result_2v2:

        builder.display_team(
            result_2v2["team"]
        )


    # --------------------------------------------------------
    # Test 3v3
    # --------------------------------------------------------

    print(
        "\n\n========== 3v3 TEST =========="
    )


    result_3v3 = (
        builder.find_best_team(
            team_size=3,
            max_candidates=100
        )
    )


    if result_3v3:

        builder.display_team(
            result_3v3["team"]
        )


    # --------------------------------------------------------
    # Test 4v4
    # --------------------------------------------------------

    print(
        "\n\n========== 4v4 TEST =========="
    )


    result_4v4 = (
        builder.find_best_team(
            team_size=4,
            max_candidates=100
        )
    )


    if result_4v4:

        builder.display_team(
            result_4v4["team"]
        )


    print(
        "\n========================================"
    )

    print(
        " TEAM BUILDER TEST COMPLETED"
    )

    print(
        "========================================"
    )