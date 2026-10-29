# plan-comparison

## Purpose
Compare Northwind Mobile plans for a customer and recommend the best fit.

## Steps
1. Identify the customer's current plan via `get_customer_account`.
2. Check their typical usage via `get_data_usage`.
3. Call `get_plan_details` for each relevant plan and compare price, hotspot allotment, and roaming from its output.
4. Recommend one plan and say why in a single sentence.
