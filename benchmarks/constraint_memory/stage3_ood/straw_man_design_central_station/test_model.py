import math

# Load-Bearing Variables from the prompt and new derivations
# Digital Tier Variables (for context and overall funding, not directly for H-HOB unit economics validation)
annual_membership_fee_full = 120
quarterly_credit_full = 15
net_membership_revenue_full = annual_membership_fee_full - (quarterly_credit_full * 4)
annual_digital_upsell_full = 180
membership_gross_margin = 1.00 # 100%
digital_content_gross_margin = 0.70 # 70%
annual_digital_access_fee_digital_only = 120
cac_digital_only = 30
annual_churn_rate_digital_only = 0.25
digital_platform_fixed_cost_annual = 250000
city_fixed_cost_boston_monthly = 8500
steady_state_full_members_boston = 800
target_digital_only_members = 5000
target_nyc_launch_cost = 25000
nyc_launch_funding_period_months = 3

# NEW Load-Bearing Variables for Host-Ambassador Model (H-HOB)
avg_program_fee_per_member = 60
cs_revenue_share_from_program_fees = 0.40 # 40%
host_program_direct_cost_per_participant = 10
standard_cohort_size_intimacy = 8
target_programs_per_host_per_month = 2
host_recruitment_cost_per_active_host_annualized = 200
host_management_cost_per_active_host_per_month = 50
localized_marketing_overhead_per_micro_geography_per_month = 300
target_active_hosts_per_micro_geography = 5
avg_program_participation_per_active_full_member_per_month = 0.33 # 4 programs/year / 12 months

# --- Calculations for H-HOB Unit Economics ---

# 1. Host-Ambassador Program Unit Economics (per 8-person cohort)
total_program_revenue_cohort = avg_program_fee_per_member * standard_cohort_size_intimacy
cs_gp_per_program_cohort = total_program_revenue_cohort * cs_revenue_share_from_program_fees
host_revenue_per_program_cohort = total_program_revenue_cohort * (1 - cs_revenue_share_from_program_fees)
host_direct_costs_per_program_cohort = host_program_direct_cost_per_participant * standard_cohort_size_intimacy
host_net_profit_per_program_cohort = host_revenue_per_program_cohort - host_direct_costs_per_program_cohort

# 2. Breakeven Micro-Geography Unit Economics (Monthly)
host_recruitment_amortized_monthly = (host_recruitment_cost_per_active_host_annualized * target_active_hosts_per_micro_geography) / 12
host_mgmt_total_monthly = host_management_cost_per_active_host_per_month * target_active_hosts_per_micro_geography
micro_geo_fixed_costs_monthly = host_recruitment_amortized_monthly + host_mgmt_total_monthly + localized_marketing_overhead_per_micro_geography_per_month

programs_for_breakeven_monthly = micro_geo_fixed_costs_monthly / cs_gp_per_program_cohort
participants_for_breakeven_monthly = programs_for_breakeven_monthly * standard_cohort_size_intimacy
active_full_members_for_breakeven_monthly = participants_for_breakeven_monthly / avg_program_participation_per_active_full_member_per_month

# Operational Cost Per Active Host per Month
total_centralized_host_ops_cost_per_micro_geo_monthly = host_recruitment_amortized_monthly + host_mgmt_total_monthly
operational_cost_per_active_host_per_month = total_centralized_host_ops_cost_per_micro_geo_monthly / target_active_hosts_per_micro_geography

# --- Falsification Conditions ---
# Prediction:
# 1. CS Gross Profit per Host-Ambassador Program exceeding $190 per 8-person cohort.
# 2. Breakeven point of 85 or fewer active full members within their first 18 months.
# 3. Total operational cost per active host-ambassador not exceeding $70 per month.

# Falsification check values:
falsification_cs_gp_per_program_threshold = 190
falsification_breakeven_members_threshold = 85
falsification_ops_cost_per_host_threshold = 70

# --- Assertions for Falsification ---
def test_model():
    # 1. CS Gross Profit per Host-Ambassador Program (8-person cohort)
    assert cs_gp_per_program_cohort > falsification_cs_gp_per_program_threshold, \
        f"Falsification: CS Gross Profit per Host-Ambassador Program ({cs_gp_per_program_cohort:.2f}) is below ${falsification_cs_gp_per_program_threshold}"

    # 2. Breakeven Active Full Members per Micro-Geography
    # Round up as members are discrete units
    assert math.ceil(active_full_members_for_breakeven_monthly) <= falsification_breakeven_members_threshold, \
        f"Falsification: Active Full Members for Breakeven ({math.ceil(active_full_members_for_breakeven_monthly)}) exceeds {falsification_breakeven_members_threshold}"

    # 3. Operational Cost Per Active Host per Month
    assert operational_cost_per_active_host_per_month <= falsification_ops_cost_per_host_threshold, \
        f"Falsification: Operational Cost Per Active Host per Month ({operational_cost_per_active_host_per_month:.2f}) exceeds ${falsification_ops_cost_per_host_threshold}"

    print("All H-HOB unit economic assertions passed. The model supports the prediction.")
    print(f"CS Gross Profit per Program: ${cs_gp_per_program_cohort:.2f}")
    print(f"Host Net Profit per Program: ${host_net_profit_per_program_cohort:.2f}")
    print(f"Breakeven Programs/Month in Micro-Geography: {programs_for_breakeven_monthly:.2f}")
    print(f"Breakeven Participants/Month in Micro-Geography: {participants_for_breakeven_monthly:.2f}")
    print(f"Breakeven Active Full Members per Micro-Geography (monthly): {math.ceil(active_full_members_for_breakeven_monthly)}")
    print(f"Operational Cost Per Active Host Per Month (centralized): ${operational_cost_per_active_host_per_month:.2f}")

if __name__ == "__main__":
    test_model()
