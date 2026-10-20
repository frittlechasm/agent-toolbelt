# Orders API

Orders API accepts authenticated order requests, stores order state in Postgres, and charges
customers through the AcmePay HTTP API. It runs as one Kubernetes deployment.
