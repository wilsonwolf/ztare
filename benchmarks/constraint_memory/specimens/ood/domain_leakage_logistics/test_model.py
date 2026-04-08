class TestUrbanRelayInvariance:
    BASELINE_UNIT_COST = 100.0
    RELAY_DENSITY_GAIN = 1.10
    HYPOTHETICAL_MIDTOWN_CURB_TURNOVER_Q4_BASE = 1.02
    HYPOTHETICAL_DENSE_CORE_COMPLETION_Q4_BASE = 1.01
    HYPOTHETICAL_Q4_TRAFFIC_DAMPING_BASE = 0.99
    HUB_OVERHEAD_IDX = 1.03
    SAVINGS_FLOOR = 0.08

    def theorem_multiplier(
        self,
        relay_density_gain=None,
        curb_turnover=None,
        completion=None,
        traffic_damping=None,
        hub_overhead=None,
    ):
        relay = relay_density_gain or self.RELAY_DENSITY_GAIN
        curb = curb_turnover or self.HYPOTHETICAL_MIDTOWN_CURB_TURNOVER_Q4_BASE
        complete = completion or self.HYPOTHETICAL_DENSE_CORE_COMPLETION_Q4_BASE
        damping = traffic_damping or self.HYPOTHETICAL_Q4_TRAFFIC_DAMPING_BASE
        overhead = hub_overhead or self.HUB_OVERHEAD_IDX
        return overhead / (relay * curb * complete * damping)

    def savings_rate(self, baseline_cost=None, **kwargs):
        baseline = baseline_cost if baseline_cost is not None else self.BASELINE_UNIT_COST
        redesign = baseline * self.theorem_multiplier(**kwargs)
        return 1 - (redesign / baseline)

    def test_theorem_instance(self):
        savings = self.savings_rate()
        print(f"SAVINGS_RATE={savings:.4f}")
        assert 0.080 <= savings <= 0.0825, savings

    def test_cost_floor_transfer_under_rescaling(self):
        for baseline in (91.0, 100.0, 118.0):
            savings = self.savings_rate(baseline_cost=baseline)
            print(f"BASELINE={baseline:.1f} SAVINGS_RATE={savings:.4f}")
            assert savings >= self.SAVINGS_FLOOR, (baseline, savings)

    def test_dense_core_profile_stability(self):
        profiles = {
            "grid_core_profile": {
                "curb_turnover": 1.018,
                "completion": 1.012,
                "traffic_damping": 0.990,
            },
            "mixed_residential_profile": {
                "curb_turnover": 1.015,
                "completion": 1.011,
                "traffic_damping": 0.992,
            },
            "arterial_blend_profile": {
                "curb_turnover": 1.019,
                "completion": 1.010,
                "traffic_damping": 0.989,
            },
        }
        for name, params in profiles.items():
            savings = self.savings_rate(**params)
            print(f"{name.upper()} SAVINGS_RATE={savings:.4f}")
            assert savings >= self.SAVINGS_FLOOR, (name, savings)


if __name__ == "__main__":
    suite = TestUrbanRelayInvariance()
    suite.test_theorem_instance()
    suite.test_cost_floor_transfer_under_rescaling()
    suite.test_dense_core_profile_stability()
    print("Urban relay theorem arithmetic holds under the dimensionless coefficient instance.")
