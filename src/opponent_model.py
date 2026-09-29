# ============================================================
# GENSHIN IMPACT PVP AI
# Opponent Modeling Module
# ============================================================

import numpy as np


class OpponentModel:
    """
    Models the behavior of an opposing PvP player.

    The model keeps track of observed actions and gradually
    estimates the opponent's strategy.
    """

    def __init__(self):

        # ----------------------------------------------------
        # Action statistics
        # ----------------------------------------------------

        self.basic_attacks = 0
        self.special_attacks = 0

        self.total_actions = 0

        # ----------------------------------------------------
        # Target statistics
        # ----------------------------------------------------

        self.target_history = {}

        # ----------------------------------------------------
        # Combat statistics
        # ----------------------------------------------------

        self.damage_dealt = 0.0
        self.damage_received = 0.0

        # ----------------------------------------------------
        # Switching
        # ----------------------------------------------------

        self.switches = 0

        # ----------------------------------------------------
        # Objective behavior
        # ----------------------------------------------------

        self.objective_actions = 0

        # ----------------------------------------------------
        # Risk estimate
        # ----------------------------------------------------

        self.risk_score = 0.50


    # ========================================================
    # RECORD ACTION
    # ========================================================

    def record_action(
        self,
        action,
        attacker=None,
        target=None,
        damage=0.0
    ):
        """
        Record an observed opponent action.
        """

        self.total_actions += 1

        # ----------------------------------------------------
        # Action type
        # ----------------------------------------------------

        if action == "basic":

            self.basic_attacks += 1

        elif action == "special":

            self.special_attacks += 1


        # ----------------------------------------------------
        # Target
        # ----------------------------------------------------

        if target is not None:

            target_name = getattr(
                target,
                "name",
                str(target)
            )

            self.target_history[target_name] = (

                self.target_history.get(
                    target_name,
                    0
                )

                + 1

            )


        # ----------------------------------------------------
        # Damage
        # ----------------------------------------------------

        self.damage_dealt += damage


        # ----------------------------------------------------
        # Update risk
        # ----------------------------------------------------

        self._update_risk()


    # ========================================================
    # RECORD SWITCH
    # ========================================================

    def record_switch(self):

        self.switches += 1

        self._update_risk()


    # ========================================================
    # RECORD OBJECTIVE ACTION
    # ========================================================

    def record_objective_action(self):

        self.objective_actions += 1

        self._update_risk()


    # ========================================================
    # UPDATE RISK
    # ========================================================

    def _update_risk(self):
        """
        Estimate whether the opponent is playing
        aggressively or conservatively.
        """

        if self.total_actions == 0:

            self.risk_score = 0.50

            return


        special_ratio = (
            self.special_attacks
            /
            self.total_actions
        )


        switch_ratio = (
            self.switches
            /
            max(
                self.total_actions,
                1
            )
        )


        objective_ratio = (
            self.objective_actions
            /
            max(
                self.total_actions,
                1
            )
        )


        # More special attacks generally indicate
        # greater willingness to commit resources.

        risk = 0.40

        risk += (
            0.35
            *
            special_ratio
        )

        risk += (
            0.15
            *
            switch_ratio
        )

        risk += (
            0.10
            *
            objective_ratio
        )


        self.risk_score = float(
            np.clip(
                risk,
                0,
                1
            )
        )


    # ========================================================
    # AGGRESSION
    # ========================================================

    def aggression_score(self):
        """
        Estimate opponent aggression.
        """

        if self.total_actions == 0:

            return 0.50


        special_ratio = (
            self.special_attacks
            /
            self.total_actions
        )


        return float(
            np.clip(
                0.30
                +
                0.70
                *
                special_ratio,
                0,
                1
            )
        )


    # ========================================================
    # DEFENSIVE SCORE
    # ========================================================

    def defensive_score(self):
        """
        Estimate how defensive the opponent is.

        High switching frequency relative to attacks
        can indicate a more conservative strategy.
        """

        if self.total_actions == 0:

            return 0.50


        switch_ratio = (
            self.switches
            /
            self.total_actions
        )


        return float(
            np.clip(
                0.50
                +
                switch_ratio,
                0,
                1
            )
        )


    # ========================================================
    # PREFERRED TARGET
    # ========================================================

    def preferred_target(self):
        """
        Return the most frequently targeted character.
        """

        if not self.target_history:

            return None


        return max(
            self.target_history,
            key=self.target_history.get
        )


    # ========================================================
    # TARGET PROBABILITIES
    # ========================================================

    def target_probabilities(self):
        """
        Convert target history into probabilities.
        """

        if not self.target_history:

            return {}


        total = sum(
            self.target_history.values()
        )


        return {

            target:
                count / total

            for target, count
            in self.target_history.items()

        }


    # ========================================================
    # SPECIAL ATTACK PROBABILITY
    # ========================================================

    def special_attack_probability(
        self
    ):
        """
        Estimate probability of using a special attack
        when the opponent has sufficient energy.
        """

        if self.total_actions == 0:

            return 0.30


        return float(
            self.special_attacks
            /
            self.total_actions
        )


    # ========================================================
    # PREDICT NEXT ACTION
    # ========================================================

    def predict_next_action(
        self,
        energy=0
    ):
        """
        Predict the opponent's next action.
        """

        if energy < 30:

            return "basic"


        probability = (
            self.special_attack_probability()
        )


        if probability >= 0.50:

            return "special"


        return "basic"


    # ========================================================
    # PREDICT TARGET
    # ========================================================

    def predict_target(
        self,
        available_targets
    ):
        """
        Predict which target the opponent is likely
        to attack next.
        """

        if not available_targets:

            return None


        probabilities = (
            self.target_probabilities()
        )


        # ----------------------------------------------------
        # Known target
        # ----------------------------------------------------

        best_target = None
        best_probability = -1


        for target in available_targets:

            name = getattr(
                target,
                "name",
                str(target)
            )


            probability = probabilities.get(
                name,
                0
            )


            if probability > best_probability:

                best_probability = probability

                best_target = target


        if best_target is not None:

            return best_target


        # ----------------------------------------------------
        # Unknown target
        # ----------------------------------------------------

        # If no history exists, choose the target
        # with the lowest HP.

        return min(

            available_targets,

            key=lambda x:
                getattr(
                    x,
                    "hp",
                    float("inf")
                )

        )


    # ========================================================
    # STRATEGY CLASSIFICATION
    # ========================================================

    def classify_strategy(self):
        """
        Give a descriptive strategy classification.

        This is not a permanent label. The model can change
        as new actions are observed.
        """

        aggression = (
            self.aggression_score()
        )

        defense = (
            self.defensive_score()
        )


        if aggression >= 0.70:

            return "Aggressive"


        if defense >= 0.70:

            return "Defensive"


        if (
            aggression >= 0.55
            and defense >= 0.55
        ):

            return "Adaptive"


        return "Balanced"


    # ========================================================
    # ADAPTATION SIGNAL
    # ========================================================

    def adaptation_signal(self):
        """
        Indicates how much evidence we have collected
        about the opponent.
        """

        if self.total_actions == 0:

            return 0.0


        # Saturating function.

        confidence = (

            1
            -
            np.exp(
                -self.total_actions / 10
            )

        )


        return float(
            np.clip(
                confidence,
                0,
                1
            )
        )


    # ========================================================
    # COMPLETE PROFILE
    # ========================================================

    def get_profile(self):
        """
        Return the current opponent model.
        """

        return {

            "total_actions":
                self.total_actions,

            "basic_attacks":
                self.basic_attacks,

            "special_attacks":
                self.special_attacks,

            "switches":
                self.switches,

            "objective_actions":
                self.objective_actions,

            "aggression":
                self.aggression_score(),

            "defensive_score":
                self.defensive_score(),

            "risk_score":
                self.risk_score,

            "preferred_target":
                self.preferred_target(),

            "special_probability":
                self.special_attack_probability(),

            "strategy":
                self.classify_strategy(),

            "adaptation_confidence":
                self.adaptation_signal()

        }


    # ========================================================
    # DISPLAY
    # ========================================================

    def display(self):

        print(
            "\n========================================"
        )

        print(
            "          OPPONENT MODEL"
        )

        print(
            "========================================"
        )


        profile = self.get_profile()


        for key, value in profile.items():

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

    print(
        "\n========================================"
    )

    print(
        " OPPONENT MODEL TEST"
    )

    print(
        "========================================"
    )


    model = OpponentModel()


    # --------------------------------------------------------
    # Simulate observed opponent behavior
    # --------------------------------------------------------

    for _ in range(5):

        model.record_action(
            "basic"
        )


    for _ in range(4):

        model.record_action(
            "special"
        )


    model.record_switch()

    model.record_switch()


    model.record_objective_action()


    # --------------------------------------------------------
    # Display model
    # --------------------------------------------------------

    model.display()


    # --------------------------------------------------------
    # Predictions
    # --------------------------------------------------------

    print(
        "\nPredicted next action:"
    )

    print(
        model.predict_next_action(
            energy=80
        )
    )


    print(
        "\n========================================"
    )

    print(
        " OPPONENT MODEL TEST COMPLETED"
    )

    print(
        "========================================"
    )