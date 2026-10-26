# outage-triage

## Purpose
Triage a "no service / slow data" complaint.

## Steps
1. Get the customer's ZIP and run `check_network_status`.
2. If there is an outage, give the ETA and reassure the customer.
3. If no outage, delegate device-level troubleshooting to the
   `network-diagnostics` subagent.
