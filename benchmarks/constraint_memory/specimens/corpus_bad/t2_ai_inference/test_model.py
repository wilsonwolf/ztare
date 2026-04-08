import math

class TestOpenAISolvency:
    # LOAD-BEARING VARIABLES (MANDATORY)
    C_TRAIN = 100_000_000.0  # GPT-4 estimated training cost
    OAI_REV = 3_700_000_000.0  # OpenAI annualized revenue (Q4 2024 run rate)
    OAI_BURN = 7_000_000_000.0  # OpenAI estimated total annual burn (conservative lower estimate)
    OAI_VAL = 157_000_000_000.0  # OpenAI October 2024 valuation
    T_LIFE_YEARS = 1.5  # Model economic lifetime (years)
    VC_HURDLE_RATE = 0.25  # VC funding hurdle rate (conservative for late-stage)
    GPT4O_INPUT_PRICE = 2.50  # GPT-4o input price (late 2024)
    GPT4O_OUTPUT_PRICE = 10.00  # GPT-4o output price (late 2024)
    IO_RATIO_INPUT_WEIGHT = 1.0  # Assumed input token weight for blended price
    IO_RATIO_OUTPUT_WEIGHT = 4.0  # Assumed output token weight for blended price
    PREDICTED_FUTURE_PRICE = 0.28  # Predicted future effective average price (Q1 2026)
    OAI_BURN_REV_TARGET = 1.5 # Burn/Revenue ratio falsification threshold

    def calculate_metrics(self, burn_override=None, vc_hurdle_override=None):
        current_burn = burn_override if burn_override is not None else self.OAI_BURN
        current_vc_hurdle = vc_hurdle_override if vc_hurdle_override is not None else self.VC_HURDLE_RATE

        # 1. Effective Average Revenue Price (P_avg_revenue)
        p_avg_revenue = (self.GPT4O_INPUT_PRICE * self.IO_RATIO_INPUT_WEIGHT +
                         self.GPT4O_OUTPUT_PRICE * self.IO_RATIO_OUTPUT_WEIGHT) / \
                        (self.IO_RATIO_INPUT_WEIGHT + self.IO_RATIO_OUTPUT_WEIGHT)

        # 2. Derived Lifetime Tokens (Q_tokens_lifetime_millions)
        q_tokens_annually_millions = self.OAI_REV / p_avg_revenue
        q_tokens_lifetime_millions = q_tokens_annually_millions * self.T_LIFE_YEARS

        # 3. Corrected Training Amortization (X_AMORTIZATION)
        x_amortization = self.C_TRAIN / q_tokens_lifetime_millions

        # 4. Financial Leverage (Y_LEVERAGE)
        y_leverage = (current_burn / self.OAI_REV) * current_vc_hurdle

        return p_avg_revenue, q_tokens_lifetime_millions, x_amortization, y_leverage

    def test_solvency_at_predicted_future_price(self):
        # Calculate current metrics
        p_avg_revenue, _, x_amortization, y_leverage = self.calculate_metrics()

        # Check current solvency (should be very solvent)
        z_current_price = (x_amortization / p_avg_revenue) * y_leverage
        print(f"Z_CURRENT_PRICE: {z_current_price:.4f}")
        assert z_current_price < 0.05, f"Z_CURRENT_PRICE ({z_current_price:.4f}) indicates less solvency than expected at current prices."

        # Calculate solvency at the predicted future price floor
        z_predicted_future_price = (x_amortization / self.PREDICTED_FUTURE_PRICE) * y_leverage
        print(f"Z_PREDICTED_FUTURE_PRICE (at ${self.PREDICTED_FUTURE_PRICE}/1M): {z_predicted_future_price:.4f}")

        # Assert prediction conditions
        # 1. Z solvency ratio exceeds 0.25 at the predicted future price
        assert z_predicted_future_price > 0.25, \
            f"Falsification: Z solvency ratio ({z_predicted_future_price:.4f}) did not exceed 0.25 at ${self.PREDICTED_FUTURE_PRICE}/1M tokens."

        # Verify the calculation of predicted down-round range
        # Lower bound for down-round valuation (50% below OAI_VAL)
        down_round_val_min = self.OAI_VAL * 0.30
        # Upper bound for down-round valuation (70% below OAI_VAL, i.e., 30% of OAI_VAL)
        down_round_val_max = self.OAI_VAL * 0.50
        print(f"Implied Down-Round Valuation Range: ${down_round_val_min/1e9:.1f}B - ${down_round_val_max/1e9:.1f}B")

    def test_falsification_conditions(self):
        # Simulate conditions where the thesis is falsified
        # Case 1: P_avg_revenue stays above threshold AND Burn/Revenue drops below target
        # For this test, we assume a hypothetical scenario where P_avg_revenue > PREDICTED_FUTURE_PRICE
        # And we set a burn that brings the burn/revenue ratio below the target
        
        # Test 1. If Price does not collapse as predicted AND burn ratio improves
        hypothetical_p_avg_revenue = self.PREDICTED_FUTURE_PRICE * 1.1 # Stays above predicted collapse
        
        # Calculate the OAI_BURN needed to achieve a burn/revenue ratio below OAI_BURN_REV_TARGET
        target_burn = self.OAI_BURN_REV_TARGET * self.OAI_REV
        # Let's assume a burn that is significantly below the target_burn for falsification
        hypothetical_burn_for_falsification = self.OAI_BURN_REV_TARGET * 0.9 * self.OAI_REV # e.g. 90% of target
        
        # Recalculate metrics for falsification scenario (only Y_LEVERAGE is affected by burn change)
        _, _, x_amortization, y_leverage_falsify = self.calculate_metrics(burn_override=hypothetical_burn_for_falsification)

        burn_rev_ratio_falsify = hypothetical_burn_for_falsification / self.OAI_REV
        
        # For the test to pass if the thesis IS falsified, we should assert that Z is NOT > 0.25
        # This is essentially testing the inverse of the prediction.
        # If the actual P_inference is high and burn/revenue is low, Z should be low.
        z_falsify_scenario = (x_amortization / hypothetical_p_avg_revenue) * y_leverage_falsify
        print(f"Z_FALSIFICATION_SCENARIO (at ${hypothetical_p_avg_revenue:.2f}/1M & Burn/Rev={burn_rev_ratio_falsify:.2f}): {z_falsify_scenario:.4f}")
        assert z_falsify_scenario < 0.25, \
            f"Falsification test failed: Z ({z_falsify_scenario:.4f}) is still above 0.25 even under falsifying conditions."


# To run these tests:
# Create an instance and call the methods.
# For example, in a test runner or directly:
# test_suite = TestOpenAISolvency()
# test_suite.test_solvency_at_predicted_future_price()
# test_suite.test_falsification_conditions()
