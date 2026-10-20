# ADR 0001: Keep order state in Postgres

Status: accepted

The API owns order state in Postgres. AcmePay remains the payment system of record. Charging stays
synchronous for the first release; a queue may be considered if provider latency breaches the API
budget. We have not yet defined reconciliation after an ambiguous AcmePay timeout.
