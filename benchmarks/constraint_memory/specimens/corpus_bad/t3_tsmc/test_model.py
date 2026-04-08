# test_model.py
import math

class TestModel:
    def __init__(self):
        # LOAD-BEARING VARIABLES (from previous context, updated)
        self.TSMC_ADV_WSPM = 250000  # Wafers/Mo (N3 + N4/N5)
        self.FAB_CYCLE_TIME_DAYS = 90  # Days (~3 Months) for Sub-5nm wafer process
        self.WAFER_PRICE_USD = 20000  # USD per Sub-5nm wafer
        self.CHEM_BUFFER_DAYS = 30  # Days (Conservative, lower end of 30-45 day range)
        self.QUARANTINE_DAYS = 60  # Days (Stress-test parameter)
        self.RESTART_DAYS = 45  # Days (Conservative, higher end of minimum 30-day range)
        self.OEM_INVENTORY_DAYS = 20  # Days (Plausible finished goods inventory buffer for critical products)

        # OEM Revenue (Annual, Billion USD)
        self.REV_AAPL_HW_ANNUAL = 350.0  # Billion USD
        self.REV_NVDA_DC_ANNUAL = 115.0  # Billion USD
        self.REV_AMD_ANNUAL = 22.0  # Billion USD

        # OEM Dependency Rates on TSMC Sub-5nm (Percentage)
        self.AAPL_HW_DEP_PCT = 0.90 # 90% of Apple HW revenue dependent on advanced TSMC nodes
        self.NVDA_DC_DEP_PCT = 0.95 # 95% of NVIDIA DC revenue dependent on advanced TSMC nodes
        self.AMD_DEP_PCT = 0.85 # 85% of AMD revenue dependent on advanced TSMC nodes

        # GDP Multiplier
        self.BROADER_ECONOMIC_ACTIVITY_MULTIPLIER = 2.0 # Multiplier from direct OEM revenue loss to broader global GDP contraction

        # World GDP (for context)
        self.WORLD_GDP_ANNUAL = 105.0 # Trillion USD

        # Constants for time conversion
        self.DAYS_PER_MONTH = 365.25 / 12

    def calculate_metrics(self):
        # 1. Calculate Gross Supply Void Duration (GSVD) at TSMC output
        #    This is the time from quarantine start until the first new chips are ready for shipment from TSMC.
        #    a. Time until chemical buffer depletes: CHEM_BUFFER_DAYS
        #    b. Remaining quarantine time during which fab is halted (after buffer depletion): QUARANTINE_DAYS - CHEM_BUFFER_DAYS
        #    c. Time for fab restart and re-qualification (assumes quarantine lifts after QUARANTINE_DAYS, then restart begins): RESTART_DAYS
        #    d. Time for new wafers to complete a full cycle: FAB_CYCLE_TIME_DAYS

        # Time until fab production stops due to chemical depletion
        time_until_fab_halt = self.CHEM_BUFFER_DAYS # 30 days

        # Duration the fab is non-operational due to ongoing quarantine after buffer depletion
        time_fab_halted_during_quarantine = max(0, self.QUARANTINE_DAYS - time_until_fab_halt) # 60 - 30 = 30 days

        # Total time from quarantine start until the first *new* chips are available for shipment from TSMC
        gross_supply_void_duration_days = time_until_fab_halt + time_fab_halted_during_quarantine + self.RESTART_DAYS + self.FAB_CYCLE_TIME_DAYS
        
        # 2. Calculate Effective Supply Void Duration (ESVD) felt by the market
        #    OEMs can absorb part of the initial void with their inventory buffer.
        effective_supply_void_duration_days = gross_supply_void_duration_days - self.OEM_INVENTORY_DAYS
        effective_supply_void_duration_months = effective_supply_void_duration_days / self.DAYS_PER_MONTH

        # 3. Calculate Dependent Monthly OEM Revenue (Adjusted)
        rev_aapl_hw_monthly_adj = (self.REV_AAPL_HW_ANNUAL / 12) * self.AAPL_HW_DEP_PCT
        rev_nvda_dc_monthly_adj = (self.REV_NVDA_DC_ANNUAL / 12) * self.NVDA_DC_DEP_PCT
        rev_amd_monthly_adj = (self.REV_AMD_ANNUAL / 12) * self.AMD_DEP_PCT
        dependent_monthly_oem_revenue = (rev_aapl_hw_monthly_adj + rev_nvda_dc_monthly_adj + rev_amd_monthly_adj)

        # 4. Calculate Total OEM Revenue Loss (Z_REV)
        total_oem_revenue_loss = dependent_monthly_oem_revenue * effective_supply_void_duration_months

        # 5. Calculate Immediate WIP Value Destroyed (using previous prompt's specific figure)
        total_wip_destroyed_wafers = 750000 
        wip_value_destroyed = total_wip_destroyed_wafers * self.WAFER_PRICE_USD

        # 6. Calculate Estimated Global GDP Contraction (Z_GDP)
        estimated_global_gdp_contraction = total_oem_revenue_loss * self.BROADER_ECONOMIC_ACTIVITY_MULTIPLIER
        
        return {
            "gross_supply_void_duration_days": gross_supply_void_duration_days,
            "effective_supply_void_duration_days": effective_supply_void_duration_days,
            "effective_supply_void_duration_months": effective_supply_void_duration_months,
            "dependent_monthly_oem_revenue_billions": dependent_monthly_oem_revenue, # already in billions
            "total_oem_revenue_loss_billions": total_oem_revenue_loss, # already in billions
            "wip_value_destroyed_billions": wip_value_destroyed / 1_000_000_000,
            "estimated_global_gdp_contraction_billions": estimated_global_gdp_contraction # already in billions
        }

    def run_tests(self):
        metrics = self.calculate_metrics()

        # Assertion for Effective Supply Void Duration (X)
        expected_x_months = 5.75 
        assert abs(metrics["effective_supply_void_duration_months"] - expected_x_months) < 0.01, \
            f"Effective supply void duration (X) mismatch. Expected: {expected_x_months:.2f}, Got: {metrics['effective_supply_void_duration_months']:.2f}"

        # Assertion for Dependent Monthly OEM Revenue (Y)
        expected_y_billions = 36.9125 
        assert abs(metrics["dependent_monthly_oem_revenue_billions"] - expected_y_billions) < 0.01, \
            f"Dependent monthly OEM revenue (Y) mismatch. Expected: {expected_y_billions:.2f}, Got: {metrics['dependent_monthly_oem_revenue_billions']:.2f}"

        # Assertion for Total OEM Revenue Loss (Z_REV)
        expected_z_rev_billions = 212.25 
        assert abs(metrics["total_oem_revenue_loss_billions"] - expected_z_rev_billions) < 0.01, \
            f"Total OEM revenue loss (Z_REV) mismatch. Expected: {expected_z_rev_billions:.2f}, Got: {metrics['total_oem_revenue_loss_billions']:.2f}"

        # Assertion for WIP Value Destroyed
        expected_wip_value_billions = 15.0
        assert abs(metrics["wip_value_destroyed_billions"] - expected_wip_value_billions) < 0.01, \
            f"WIP value destroyed mismatch. Expected: {expected_wip_value_billions:.2f}, Got: {metrics['wip_value_destroyed_billions']:.2f}"

        # Assertion for Estimated Global GDP Contraction (Z_GDP)
        expected_gdp_contraction_billions = 424.49 
        assert abs(metrics["estimated_global_gdp_contraction_billions"] - expected_gdp_contraction_billions) < 0.01, \
            f"Estimated global GDP contraction mismatch. Expected: {expected_gdp_contraction_billions:.2f}, Got: {metrics['estimated_global_gdp_contraction_billions']:.2f}"

        print("All assertions passed!")
        print(f"Gross Supply Void Duration: {metrics['gross_supply_void_duration_days']:.2f} days")
        print(f"Effective Supply Void Duration: {metrics['effective_supply_void_duration_months']:.2f} months")
        print(f"Dependent Monthly OEM Revenue: ${metrics['dependent_monthly_oem_revenue_billions']:.2f} Billion")
        print(f"Total OEM Revenue Loss (Z_REV): ${metrics['total_oem_revenue_loss_billions']:.2f} Billion")
        print(f"Immediate WIP Value Destroyed: ${metrics['wip_value_destroyed_billions']:.2f} Billion")
        print(f"Estimated Global GDP Contraction (Z_GDP): ${metrics['estimated_global_gdp_contraction_billions']:.2f} Billion")

if __name__ == "__main__":
    model = TestModel()
    model.run_tests()
