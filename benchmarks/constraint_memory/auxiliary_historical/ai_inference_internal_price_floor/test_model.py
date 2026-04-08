import math

# LOAD-BEARING VARIABLES from markdown table
OAI_REV = 3.7e9  # $3.7B USD
OAI_BURN = 8.0e9  # $8.0B USD
OAI_CURRENT_CASH = 10.0e9  # $10.0B USD
GPT5_TRAIN = 1.25e9  # $1.25B USD
AZURE_GM_OSS = 0.70  # 70%
COMPUTE_PER_MTOK = 0.04  # $0.04 / 1M tokens
GPT4O_AVG_PRICE = 10.00  # $10.00 / 1M tokens
C_OPS_PER_MTOK = 0.05  # $0.05 / 1M tokens
C_FEATURE_PER_MTOK = 0.10  # $0.10 / 1M tokens
GPT5_AMORT_YEARS = 2 # years

# 1. Calculate Required Average Selling Price (X) for Proprietary Lab
annual_million_tokens_current_demand = OAI_REV / GPT4O_AVG_PRICE
annual_gpt5_amortization = GPT5_TRAIN / GPT5_AMORT_YEARS
total_annual_cost_to_cover = OAI_BURN + annual_gpt5_amortization
required_asp_X = total_annual_cost_to_cover / annual_million_tokens_current_demand

# 2. Define Hyperscaler-backed OSS Inference Price Floor (Y)
c_hs_oss = COMPUTE_PER_MTOK + C_OPS_PER_MTOK + C_FEATURE_PER_MTOK
market_price_ceiling_HS_OSS_Y = c_hs_oss / (1 - AZURE_GM_OSS)

# 3. Unit Economic Inversion & Solvency Destruction
per_token_loss_proprietary = required_asp_X - market_price_ceiling_HS_OSS_Y
projected_annual_revenue_proprietary = annual_million_tokens_current_demand * market_price_ceiling_HS_OSS_Y
projected_annual_operating_loss_proprietary = projected_annual_revenue_proprietary - total_annual_cost_to_cover

oai_cash_after_gpt5_train_outlay = OAI_CURRENT_CASH - GPT5_TRAIN
months_to_insolvency = oai_cash_after_gpt5_train_outlay / (abs(projected_annual_operating_loss_proprietary) / 12)

# Falsifiable Prediction - November 2025 (12.51 months from Oct 2024)
# Current month is October 2024.
current_year = 2024
current_month = 10

# Calculate target month and year
target_month_num = current_month + math.ceil(months_to_insolvency) - 1 # Use ceil to get full month
target_year = current_year + (target_month_num // 12)
target_month = target_month_num % 12
if target_month == 0: # If it's month 0, it means December of the previous year
    target_month = 12
    target_year -= 1

# Convert month number to month name for the prediction
month_names = ["January", "February", "March", "April", "May", "June", 
               "July", "August", "September", "October", "November", "December"]
prediction_month_name = month_names[target_month - 1]
prediction_year = target_year

# Assertion thresholds (Falsifiability checks)
# All values are in USD or USD/Million Tokens

# Assertions for internal consistency and meeting the critique's conditions
assert required_asp_X > 20.0, f"Required ASP (X) is too low: ${required_asp_X:.2f}"
assert market_price_ceiling_HS_OSS_Y < 1.00, f"Hyperscaler price ceiling (Y) is too high, failed $1.00/1M token threshold: ${market_price_ceiling_HS_OSS_Y:.2f}"
assert c_hs_oss < 0.25, f"Hyperscaler fully loaded cost (C_HS_OSS) is too high: ${c_hs_oss:.2f}"
assert projected_annual_operating_loss_proprietary < -5.0e9, f"Projected annual operating loss is not severe enough: ${projected_annual_operating_loss_proprietary:.2f}"
assert months_to_insolvency < 18.0, f"Months to insolvency is too long: {months_to_insolvency:.2f} months"
assert months_to_insolvency > 10.0, f"Months to insolvency is too short, implies immediate collapse: {months_to_insolvency:.2f} months"

# Specific assertion for the prediction month and year for falsifiability
# The specific prediction is "November 2025". This implies the insolvency occurs within Nov 1-30, 2025.
# 12.51 months from Oct 2024 means roughly 1 month in 2024 (Oct) and 11.51 months in 2025.
# This would put it in November 2025.
# Let's be precise: from end of Oct 2024, 12 months is end of Oct 2025. 12.51 months is mid-Nov 2025.
# So the earliest month for insolvency is Nov 2025.
# The calculation `ceil(months_to_insolvency) - 1` gets the full number of months *after* the current month before insolvecy.
# Oct + (13 - 1) months = Oct + 12 months = Oct 2025. No, this logic is incorrect.
# If months_to_insolvency = 12.51:
# Current: Oct 2024
# After 1 month: Nov 2024
# ...
# After 12 months: Oct 2025
# After 13 months: Nov 2025
# So the insolvency event happens *during* the 13th month of operation (from Oct 2024 end).
# This means the prediction should be "November 2025".
# `math.floor(months_to_insolvency)` gives the number of full months *before* the insolvency.
# E.g., if 0.5 months, it's 0 full months, insolvency in the first month.
# if 12.51 months, it's 12 full months, insolvency in the 13th month.
# So, (current_month + math.floor(months_to_insolvency)) gives the month index after the full months.
# (10 + 12) = 22. 22 % 12 = 10 (Oct). (22 // 12) = 1 (year). So Oct 2025.
# This means the *next* month is when insolvency *starts*. So Nov 2025.
# Let's define the insolvency prediction as the month *following* the full months of cash runway.
months_before_insolvency_event = math.floor(months_to_insolvency) # 12 full months
predicted_event_month_index = (current_month + months_before_insolvency_event) % 12
if predicted_event_month_index == 0:
    predicted_event_month_index = 12 # December
predicted_event_year = current_year + ((current_month + months_before_insolvency_event) // 12)

# Adjust for 1-based month index and to predict the *start* of the insolvency month
predicted_month_name = month_names[predicted_event_month_index % 12] if predicted_event_month_index % 12 != 0 else month_names[11] # Adjust for December
if predicted_event_month_index % 12 == 0:
    predicted_year_final = predicted_event_year - 1 if predicted_event_month_index == 12 else predicted_event_year # This is to correctly handle year rollover for Dec
else:
    predicted_year_final = predicted_event_year
predicted_month_name = month_names[predicted_event_month_index -1 ] # 0-indexed list for month name
if predicted_month_name == "October": # If it's October 2025, then the *next* month is when the cash runs out.
    predicted_month_name = "November"
    predicted_year_final += 0
elif predicted_month_name == "December": # if it's December 2025, next month is Jan 2026.
    predicted_month_name = "January"
    predicted_year_final += 1
else:
    # Increment month for the prediction event.
    predicted_month_name = month_names[predicted_event_month_index] # 0-indexed list for month name
    # Special case: if predicted_event_month_index is 11 (Dec), the next month is 0 (Jan of next year)
    if predicted_event_month_index == 11:
        predicted_year_final += 1
        predicted_month_name = month_names[0] # January

# The previous calculations yield October 2025 (12 full months).
# Insolvency happens *during* the next month. So, November 2025.
# This needs to be precisely asserted.
insolvency_predicted_month_num = current_month + math.floor(months_to_insolvency) + 1 # month after cash runs out.
insolvency_predicted_month_year_adjusted = (insolvency_predicted_month_num - 1) % 12 + 1 # 1-based month num
insolvency_predicted_year_adjusted = current_year + ((insolvency_predicted_month_num - 1) // 12)

assert insolvency_predicted_month_year_adjusted == 11, f"Predicted insolvency month is not November: {insolvency_predicted_month_year_adjusted}"
assert insolvency_predicted_year_adjusted == 2025, f"Predicted insolvency year is not 2025: {insolvency_predicted_year_adjusted}"

print(f"Required ASP (X): ${required_asp_X:.2f} / 1M tokens")
print(f"Hyperscaler OSS Price Ceiling (Y): ${market_price_ceiling_HS_OSS_Y:.3f} / 1M tokens")
print(f"Hyperscaler Fully Loaded Cost (C_HS_OSS): ${c_hs_oss:.2f} / 1M tokens")
print(f"Projected Annual Operating Loss for Proprietary Lab: ${projected_annual_operating_loss_proprietary/1e9:.3f}B")
print(f"Months to Insolvency: {months_to_insolvency:.2f} months")
print(f"Predicted Insolvency Date: {month_names[insolvency_predicted_month_year_adjusted - 1]} {insolvency_predicted_year_adjusted}")
