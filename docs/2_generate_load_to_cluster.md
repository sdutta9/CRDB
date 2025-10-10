# Generate a load against the cluster

As part of this exercise, you will generate a load against the CockroachDB cluster that you created in previous exercise.

You will make use of `cockroach workload` command for this task. More info here. (<https://www.cockroachlabs.com/docs/stable/cockroach-workload.html>)

## Run CockroachDB provided load test

1. Load the initial schema. This would be run only once and creates the schema for the Bank database.

    ```bash
    cockroach workload init bank \
    'postgresql://root@cockroachdb.example.com:26257/bank?sslmode=disable'
    ```

1. Run the workload for 60 minutes to go through the next exercise

    ```bash
    cockroach workload run bank \
    --duration=60m \
    'postgresql://root@cockroachdb.example.com:26257?sslmode=disable'
    
    ```

-------------

Navigate to ([Task3](./3_scaling_and_failing.md) | [Main Page](../README.md))