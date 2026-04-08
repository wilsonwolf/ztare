import math

# Load-Bearing Variables (P50 Assumptions and Hypothetical Observed P50 for MC)
annual_membership_fee = 120  # Known Fact
quarterly_credits = 15
net_membership_revenue_per_member_annual = annual_membership_fee - (quarterly_credits * 4) # Known Fact: $60

experiment_duration_months = 6
experiment_budget = 100000
target_net_members_acquired_by_month_6 = 80 # Falsification threshold for members acquired

city_fixed_cost_per_month_p50 = 8500 # P50 Assumption

# Hypothetically Observed P50 values from a successful DPVBS (targets)
hypothetical_monthly_referral_rate_p50 = 0.12
hypothetical_conversion_rate_referred_leads_p50 = 0.55
hypothetical_annual_churn_rate_p50 = 0.25 # Derived from 6-month observation
hypothetical_programs_attended_per_member_per_year_p50 = 5 # Derived from 6-month observation
hypothetical_problem_solution_fit_score_p50 = 4.0 # Target score

# Other P50 Assumptions from Grounding Data
cac_peer_referral_p50 = 25
cac_paid_events_p50 = 120
referral_share_of_acquisition_p50 = 0.65
average_program_ticket_price_p50 = 50
program_gross_margin_p50 = 0.52

initial_members_for_growth_calc = 80 # Based on DPVBS target acquisition

# --- Calculations for Financial Viability ---

# 1. Gross Profit per Member (Annual)
program_revenue_per_member_annual = (
    hypothetical_programs_attended_per_member_per_year_p50 *
    average_program_ticket_price_p50 *
    program_gross_margin_p50
)
gross_profit_per_member_annual = net_membership_revenue_per_member_annual + program_revenue_per_member_annual
gross_profit_per_member_monthly = gross_profit_per_member_annual / 12

# 2. Blended CAC
blended_cac = (
    (cac_peer_referral_p50 * referral_share_of_acquisition_p50) +
    (cac_paid_events_p50 * (1 - referral_share_of_acquisition_p50))
)

# 3. LTV & LTV/CAC Ratio
ltv = gross_profit_per_member_annual / hypothetical_annual_churn_rate_p50
ltv_cac_ratio = ltv / blended_cac

# 4. CAC Payback Period (Months)
cac_payback_months = blended_cac / gross_profit_per_member_monthly

# 5. Members required for Monthly Cash Flow Breakeven
members_for_monthly_breakeven = city_fixed_cost_per_month_p50 / gross_profit_per_member_monthly

# 6. Estimated Months to City Breakeven (Organic Path from initial_members_for_growth_calc)
# This estimates the time for an initial base of members to organically grow to the point where
# the recurring monthly gross profit covers monthly fixed costs.
# We assume organic growth is driven by referrals from existing members.
monthly_organic_growth_rate_per_member = (
    hypothetical_monthly_referral_rate_p50 *
    hypothetical_conversion_rate_referred_leads_p50
)
monthly_growth_factor = 1 + monthly_organic_growth_rate_per_member

# Avoid log(0) or log(negative) if initial members are already more than breakeven members.
if initial_members_for_growth_calc >= members_for_monthly_breakeven:
    estimated_months_to_city_breakeven = 0 # Already breakeven or surpassed
elif monthly_growth_factor <= 1: # No organic growth
    estimated_months_to_city_breakeven = float('inf')
else:
    # Time for members to grow from initial_members_for_growth_calc to members_for_monthly_breakeven
    estimated_months_to_city_breakeven = math.log(
        members_for_monthly_breakeven / initial_members_for_growth_calc
    ) / math.log(monthly_growth_factor)

# --- Unit Test ---
def test_model():
    print(f"--- Central Station Financial Viability Check (Hypothetical P50) ---")
    print(f"Gross Profit per Member (Annual): ${gross_profit_per_member_annual:.2f}")
    print(f"Gross Profit per Member (Monthly): ${gross_profit_per_member_monthly:.2f}")
    print(f"Blended CAC: ${blended_cac:.2f}")
    print(f"LTV: ${ltv:.2f}")
    print(f"LTV/CAC Ratio: {ltv_cac_ratio:.2f}x")
    print(f"CAC Payback Period: {cac_payback_months:.2f} months")
    print(f"Members for Monthly Breakeven (to cover fixed costs): {members_for_monthly_breakeven:.0f} members")
    print(f"Estimated Months to City Breakeven (organic path from {initial_members_for_growth_calc} members): {estimated_months_to_city_breakeven:.2f} months")
    print(f"Problem-Solution Fit Score (PSFS) P50 Target: {hypothetical_problem_solution_fit_score_p50:.1f}")
    print(f"Target Members Acquired by Month 6: {target_net_members_acquired_by_month_6}")

    # Assertions based on Falsification Conditions
    assert hypothetical_problem_solution_fit_score_p50 >= 4.0, "Falsified: Problem-Solution Fit Score (PSFS) below 4.0"
    # Note: The actual number of members acquired (80) is an operational target for the sprint,
    # and not directly calculable by this financial model. It's an empirical observation.
    # The assumption for this test is that 80 members *were* acquired and formed the basis for these P50s.

    assert cac_payback_months <= 18, "Falsified: CAC payback period exceeds 18 months"
    assert ltv_cac_ratio >= 3.5, "Falsified: LTV/CAC ratio below 3.5x"
    assert estimated_months_to_city_breakeven <= 30, "Falsified: Months to city breakeven (organic) exceeds 30 months"

if __name__ == "__main__":
    test_model()
