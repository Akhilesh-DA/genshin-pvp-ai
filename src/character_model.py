# ============================================================
# GENSHIN IMPACT PVP AI
# Character Modeling Module
# ============================================================

import pandas as pd
import numpy as np


# ------------------------------------------------------------
# CHARACTER MODEL
# ------------------------------------------------------------

class CharacterModel:
    """
    Converts character data into PvP-oriented attributes.

    The model deliberately avoids treating raw character
    statistics as the only measure of strength.

    PvP performance will later depend on:

        - Offensive capability
        - Survivability
        - Utility
        - Flexibility
        - Synergy
        - Environment
        - Objectives
        - Opponent behavior
    """

    def __init__(self, dataframe):

        self.df = dataframe.copy()

        self.character_profiles = {}

        self._create_profiles()


    # --------------------------------------------------------
    # SAFE NUMERIC VALUE
    # --------------------------------------------------------

    @staticmethod
    def safe_numeric(
        value,
        default=0.0
    ):
        """
        Safely convert a value into a number.
        """

        try:

            value = float(value)

            if np.isnan(value):

                return default

            return value

        except:

            return default


    # --------------------------------------------------------
    # NORMALIZE VALUE
    # --------------------------------------------------------

    @staticmethod
    def normalize(
        value,
        minimum,
        maximum
    ):
        """
        Normalize a value between 0 and 1.
        """

        if maximum == minimum:

            return 0.5

        return (
            (value - minimum)
            /
            (maximum - minimum)
        )


    # --------------------------------------------------------
    # ROLE DETECTION
    # --------------------------------------------------------

    def detect_role(
        self,
        row
    ):
        """
        Determine the most likely PvP role.

        If the dataset contains a role column,
        that information is used.

        Otherwise, a role is estimated from
        available character statistics.
        """

        possible_columns = [

            "role",

            "roles",

            "character_role",

            "type",

            "class"

        ]

        for column in possible_columns:

            if column in row.index:

                value = str(
                    row[column]
                ).strip()

                if value.lower() != "unknown":

                    return value


        # ----------------------------------------------------
        # Estimate role from statistics
        # ----------------------------------------------------

        atk = self.safe_numeric(
            row.get(
                "pvp_atk",
                100
            )
        )

        hp = self.safe_numeric(
            row.get(
                "pvp_hp",
                1000
            )
        )

        defense = self.safe_numeric(
            row.get(
                "pvp_def",
                100
            )
        )


        # High attack characters
        # are initially treated as offensive.

        if atk > 150:

            return "DPS"


        # High survivability characters

        if hp > 1500 or defense > 150:

            return "Survivability"


        # Default flexible role

        return "Support"


    # --------------------------------------------------------
    # ELEMENT EXTRACTION
    # --------------------------------------------------------

    def get_element(
        self,
        row
    ):
        """
        Extract elemental information.
        """

        possible_columns = [

            "element",

            "vision",

            "element_type"

        ]

        for column in possible_columns:

            if column in row.index:

                value = str(
                    row[column]
                ).strip()

                if value.lower() != "unknown":

                    return value


        return "Unknown"


    # --------------------------------------------------------
    # WEAPON EXTRACTION
    # --------------------------------------------------------

    def get_weapon(
        self,
        row
    ):
        """
        Extract weapon information.
        """

        possible_columns = [

            "weapon",

            "weapon_type",

            "weapon_class"

        ]

        for column in possible_columns:

            if column in row.index:

                value = str(
                    row[column]
                ).strip()

                if value.lower() != "unknown":

                    return value


        return "Unknown"


    # --------------------------------------------------------
    # RARITY EXTRACTION
    # --------------------------------------------------------

    def get_rarity(
        self,
        row
    ):
        """
        Extract rarity information.
        """

        possible_columns = [

            "rarity",

            "stars",

            "star",

            "rarity_stars"

        ]

        for column in possible_columns:

            if column in row.index:

                value = self.safe_numeric(
                    row[column],
                    0
                )

                if value > 0:

                    return value


        return 5.0


    # --------------------------------------------------------
    # OFFENSIVE SCORE
    # --------------------------------------------------------

    def calculate_offensive_score(
        self,
        row
    ):
        """
        Calculate offensive capability.

        This is only one component of PvP strength.
        """

        atk = self.safe_numeric(
            row.get(
                "pvp_atk",
                100
            )
        )

        atk_normalized = self.safe_numeric(
            row.get(
                "pvp_atk_normalized",
                0.5
            ),
            0.5
        )

        rarity = self.get_rarity(
            row
        )

        rarity_score = min(
            rarity / 5.0,
            1.0
        )


        score = (

            0.60 * atk_normalized

            +

            0.25 * rarity_score

            +

            0.15 * min(
                atk / 300.0,
                1.0
            )

        )


        return float(
            np.clip(
                score,
                0,
                1
            )
        )


    # --------------------------------------------------------
    # SURVIVABILITY SCORE
    # --------------------------------------------------------

    def calculate_survivability_score(
        self,
        row
    ):
        """
        Calculate survivability.

        HP and DEF are considered.
        """

        hp_normalized = self.safe_numeric(
            row.get(
                "pvp_hp_normalized",
                0.5
            ),
            0.5
        )

        def_normalized = self.safe_numeric(
            row.get(
                "pvp_def_normalized",
                0.5
            ),
            0.5
        )


        score = (

            0.60 * hp_normalized

            +

            0.40 * def_normalized

        )


        return float(
            np.clip(
                score,
                0,
                1
            )
        )


    # --------------------------------------------------------
    # UTILITY SCORE
    # --------------------------------------------------------

    def calculate_utility_score(
        self,
        row
    ):
        """
        Estimate PvP utility.

        Support and survivability roles receive
        higher baseline utility because they can
        influence fights without directly maximizing
        damage.
        """

        role = self.detect_role(
            row
        ).lower()


        if "support" in role:

            return 0.85

        if "surviv" in role:

            return 0.75

        if "off" in role:

            return 0.70

        if "dps" in role:

            return 0.55

        return 0.60


    # --------------------------------------------------------
    # FLEXIBILITY SCORE
    # --------------------------------------------------------

    def calculate_flexibility_score(
        self,
        row
    ):
        """
        Estimate how useful a character could be
        across different environments.
        """

        role = self.detect_role(
            row
        ).lower()

        element = self.get_element(
            row
        ).lower()


        score = 0.50


        # Characters with support capability
        # are generally more adaptable.

        if "support" in role:

            score += 0.20


        # Off-field characters can adapt while
        # another character remains active.

        if "off" in role:

            score += 0.15


        # Unknown elements receive no bonus.

        if element != "unknown":

            score += 0.10


        return float(
            np.clip(
                score,
                0,
                1
            )
        )


    # --------------------------------------------------------
    # RISK SCORE
    # --------------------------------------------------------

    def calculate_risk_score(
        self,
        row
    ):
        """
        Estimate the risk associated with relying
        heavily on the character.

        High-damage / low-survivability characters
        receive higher risk.

        This is NOT a measure of whether a character
        is good or bad.
        """

        offensive = (
            self.calculate_offensive_score(
                row
            )
        )

        survivability = (
            self.calculate_survivability_score(
                row
            )
        )


        risk = (

            offensive
            *
            (1 - survivability)

        )


        return float(
            np.clip(
                risk,
                0,
                1
            )
        )


    # --------------------------------------------------------
    # PvP VALUE
    # --------------------------------------------------------

    def calculate_pvp_value(
        self,
        row
    ):
        """
        Calculate a balanced PvP value.

        Raw strength is deliberately only one part
        of the final score.
        """

        offensive = (
            self.calculate_offensive_score(
                row
            )
        )

        survivability = (
            self.calculate_survivability_score(
                row
            )
        )

        utility = (
            self.calculate_utility_score(
                row
            )
        )

        flexibility = (
            self.calculate_flexibility_score(
                row
            )
        )

        risk = (
            self.calculate_risk_score(
                row
            )
        )


        # Risk reduces the overall value slightly.

        value = (

            0.30 * offensive

            +

            0.25 * survivability

            +

            0.20 * utility

            +

            0.20 * flexibility

            -

            0.05 * risk

        )


        return float(
            np.clip(
                value,
                0,
                1
            )
        )


    # --------------------------------------------------------
    # CREATE CHARACTER PROFILE
    # --------------------------------------------------------

    def create_profile(
        self,
        row
    ):
        """
        Create a complete PvP profile for one character.
        """

        character_id = str(
            row.get(
                "character_id",
                "unknown"
            )
        )


        name = str(
            row.get(
                "name",
                character_id
            )
        )


        element = self.get_element(
            row
        )

        weapon = self.get_weapon(
            row
        )

        rarity = self.get_rarity(
            row
        )

        role = self.detect_role(
            row
        )


        offensive = (
            self.calculate_offensive_score(
                row
            )
        )

        survivability = (
            self.calculate_survivability_score(
                row
            )
        )

        utility = (
            self.calculate_utility_score(
                row
            )
        )

        flexibility = (
            self.calculate_flexibility_score(
                row
            )
        )

        risk = (
            self.calculate_risk_score(
                row
            )
        )

        pvp_value = (
            self.calculate_pvp_value(
                row
            )
        )


        return {

            "character_id":
                character_id,

            "name":
                name,

            "element":
                element,

            "weapon":
                weapon,

            "rarity":
                rarity,

            "role":
                role,

            "offensive_score":
                offensive,

            "survivability_score":
                survivability,

            "utility_score":
                utility,

            "flexibility_score":
                flexibility,

            "risk_score":
                risk,

            "pvp_value":
                pvp_value

        }


    # --------------------------------------------------------
    # CREATE ALL PROFILES
    # --------------------------------------------------------

    def _create_profiles(
        self
    ):
        """
        Create PvP profiles for every character.
        """

        for _, row in self.df.iterrows():

            profile = self.create_profile(
                row
            )

            character_id = (
                profile["character_id"]
            )

            self.character_profiles[
                character_id
            ] = profile


    # --------------------------------------------------------
    # GET CHARACTER
    # --------------------------------------------------------

    def get_character(
        self,
        character_id
    ):
        """
        Return a character profile.
        """

        return self.character_profiles.get(
            character_id
        )


    # --------------------------------------------------------
    # GET ALL CHARACTERS
    # --------------------------------------------------------

    def get_all_characters(
        self
    ):
        """
        Return all character profiles.
        """

        return list(
            self.character_profiles.values()
        )


    # --------------------------------------------------------
    # GET TOP CHARACTERS
    # --------------------------------------------------------

    def get_top_characters(
        self,
        n=10
    ):
        """
        Return characters with the highest
        calculated PvP value.

        This is only for inspection.

        The actual AI will NOT simply select
        the top characters because team synergy
        and environmental conditions matter.
        """

        characters = (
            self.get_all_characters()
        )

        characters.sort(

            key=lambda x:
                x["pvp_value"],

            reverse=True

        )

        return characters[:n]


    # --------------------------------------------------------
    # CONVERT TO DATAFRAME
    # --------------------------------------------------------

    def to_dataframe(
        self
    ):
        """
        Convert character profiles into
        a pandas DataFrame.
        """

        return pd.DataFrame(
            self.get_all_characters()
        )


# ------------------------------------------------------------
# STANDALONE TEST
# ------------------------------------------------------------

if __name__ == "__main__":

    from data_loader import (
        load_and_prepare_data
    )


    print(
        "\n========================================"
    )

    print(
        " CHARACTER MODEL TEST"
    )

    print(
        "========================================"
    )


    # --------------------------------------------------------
    # Load processed dataset
    # --------------------------------------------------------

    df, mapping = (
        load_and_prepare_data()
    )


    # --------------------------------------------------------
    # Create model
    # --------------------------------------------------------

    model = CharacterModel(
        df
    )


    # --------------------------------------------------------
    # Display number of characters
    # --------------------------------------------------------

    characters = (
        model.get_all_characters()
    )


    print(
        f"\nCharacters modeled: "
        f"{len(characters)}"
    )


    # --------------------------------------------------------
    # Display sample profiles
    # --------------------------------------------------------

    print(
        "\nSample character profiles:"
    )


    for character in characters[:5]:

        print(
            "\n----------------------------------------"
        )

        for key, value in character.items():

            print(
                f"{key:<25}: {value}"
            )


    # --------------------------------------------------------
    # Display top characters
    # --------------------------------------------------------

    print(
        "\n========================================"
    )

    print(
        " TOP PVP VALUES"
    )

    print(
        "========================================"
    )


    top_characters = (
        model.get_top_characters(
            n=10
        )
    )


    for index, character in enumerate(
        top_characters,
        start=1
    ):

        print(
            f"{index:>2}. "
            f"{character['name']:<20} "
            f"PvP Value: "
            f"{character['pvp_value']:.3f}"
        )


    print(
        "\nCharacter model test completed."
    )   