# bill-explainer

## Purpose
Explain why a customer's bill changed month-over-month in plain language.

## Steps
1. Call `get_customer_account` for the plan and balance.
2. Call `get_data_usage` to check for overage against the plan cap.
3. Summarize the base plan price, any overage, and any one-time charges.
4. Offer one concrete next step (e.g., autopay, plan change) if the bill rose.
