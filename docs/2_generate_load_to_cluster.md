# Generate a load against the cluster

As part of this exercise, you will generate a load against the CockroachDB cluster that you created in previous exercise.

You have two options for generating load:

## Option 1: CockroachDB Built-in Workload (Recommended)

You will make use of `cockroach workload` command for this task. More info here. (<https://www.cockroachlabs.com/docs/stable/cockroach-workload.html>)

1. Load the initial schema. This would be run only once and creates the schema for the Bank database.

    ```bash
    cockroach workload init bank \
    'postgresql://root@cockroachdb.example.com:26257?sslmode=disable'
    ```

2. Run the workload for 60 minutes to go through the next exercise

    ```bash
    cockroach workload run bank \
    --duration=60m \
    'postgresql://root@cockroachdb.example.com:26257?sslmode=disable'
    ```

## Option 2: Simple Python Bank Workload (Alternative)

If you don't have access to the `cockroach workload` command or want a simpler Python-based approach, you can use the custom load generator:

1. Activate Python virtual environment:

    ```bash
    cd custom_loadgen
    source path/to/venv/bin/activate
    ```

1. Initialize the bank schema:

    ```bash
    python simple_bank_workload.py init \
    'postgresql://root@cockroachdb.example.com:26257/defaultdb?sslmode=disable'
    ```

    ```bash
    ##Sample Output##

    🏦 Initializing Bank schema...
    📊 Creating initial accounts...
    ✓ Created 1000 accounts with initial balance of $1000 each
    ✅ Bank schema initialization complete!
    ```

1. Run the workload with custom parameters:

    ```bash
    # Run for 60 minutes with 5 worker threads (default)
    python simple_bank_workload.py run --duration 3600 --workers 5 \
    'postgresql://root@cockroachdb.example.com:26257/defaultdb?sslmode=disable'
    ```

    ```bash
    # Or run a shorter test (5 minutes with 3 workers)
    python simple_bank_workload.py run --duration 300 --workers 3 \
    'postgresql://root@cockroachdb.example.com:26257/defaultdb?sslmode=disable'
    ```

    ```bash
    ##Sample Output##
    🚀 Starting Bank workload...
    Duration: 300s, Workers: 3
    ==================================================
    Worker 1 connected
    Worker 2 connected
    Worker 3 connected
    [10:06:15] Ops: 1,970 | Rate: 190.1 ops/sec | Errors: 0
    [10:06:25] Ops: 3,905 | Rate: 191.6 ops/sec | Errors: 0
    .
    .
    .
    [10:10:45] Ops: 49,924 | Rate: 177.6 ops/sec | Errors: 198
    [10:10:55] Ops: 51,658 | Rate: 177.5 ops/sec | Errors: 222
    Worker 1 completed 18941 operations
    Worker 2 completed 17100 operations
    Worker 3 completed 17117 operations
    [10:11:05] Ops: 52,916 | Rate: 175.7 ops/sec | Errors: 242

    ==================================================
    🏁 WORKLOAD COMPLETE
    ==================================================
    Total Runtime:     301.12s
    Total Operations:  52,916
    Total Errors:      242
    Average Rate:      175.73 ops/sec

    Operations Breakdown:
    Transfer: 42,277
    Read: 10,639
    ==================================================
    ```

### What the Simple Bank Workload Does

- **Creates 1000 accounts** with initial balance of $1000 each

- **Generates mixed workload**: 80% fund transfers, 20% balance reads

- **Provides real-time statistics**: Operations per second, error rates

- **Multi-threaded**: Configurable number of worker threads

- **Handles retries**: Basic error recovery for connection issues

-------------

Navigate to ([Task3](./3_scaling_and_failing.md) | [Main Page](../README.md))