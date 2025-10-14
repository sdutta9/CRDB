# Executing a Code Example

As part of the exercise, you will first clone the git repo here

1. Clone gitrepo.

    ```bash
    git clone https://github.com/cockroachlabs/hello-world-python-psycopg2
    ```

1. Change directory to the `<project_working_dir>/hello-world-python-psycopg2`

    ```bash
    cd hello-world-python-psycopg2
    ```

1. Create a python virtual environment and then source it.

    ```bash
    python3 -m venv path/to/venv
    source path/to/venv/bin/activate
    ```

1. Within the virtual environment install `psycopg2-binary` using below command

    ```bash
    pip install psycopg2-binary
    ```

1. Export your Database url as an environment variable

    ```bash
    export DATABASE_URL="postgresql://root@cockroachdb.example.com:26257/bank?sslmode=disable"
    ```

1. Make sure it is set properly

    ```bash
    echo $DATABASE_URL 
    ```

## Option 1: Run Basic Example

1. Make sure you delete the Accounts table that you previously created manually

    ```bash
    cockroach sql --host=cockroachdb.example.com:26257 --insecure --database=bank
    ```

    Run below sql command to delete "Accounts" table

    ```sql
    drop table accounts;
    ```

1. Run the basic example code

    ```bash
    python example.py
    ```

1. For verbose output with debug information

    ```bash
    python example.py --verbose
    ```

## Option 2: Run Enhanced Example (Advanced Features)

For a more comprehensive demonstration with advanced CockroachDB features, you can run the enhanced example:

1. Make sure you delete the Accounts table that you previously created in the basic example.

    ```bash
    cockroach sql --host=cockroachdb.example.com:26257 --insecure --database=bank
    ```

    Run below sql command to delete "Accounts" table

    ```sql
    drop table accounts;
    ```

1. Run the enhanced example with advanced features demonstration

    ```bash
    python enhanced_example.py --demo
    ```

    ```bash
    ##Sample Output##

    🚀 Enhanced CockroachDB Example
    ==================================================
    2025-10-13 12:03:24,919 - INFO - ✓ Enhanced schema created successfully
    2025-10-13 12:03:24,926 - INFO - ✓ Created 5 sample accounts
    2025-10-13 12:03:24,937 - INFO - ✓ Bulk deposit completed for 3 accounts

    📊 Account Analytics:
    Total Accounts: 5
    Total Balance: $17,766.42
    Average Balance: $3,553.28

    📋 Recent Transactions for Account 98cde87c-a56d-4715-9c4a-d2d94e98cbbc:
    Outgoing: $250.00 - Demo transfer
    Incoming: $347.63 - Bulk deposit of $347.63223024849304

    ✅ All enhanced features demonstrated successfully!
    ```

1. For verbose output with debug information

    ```bash
    python enhanced_example.py --verbose --demo
    ```

### What the Enhanced Example Demonstrates

The enhanced example showcases advanced CockroachDB features including:

- **Connection pooling** for better performance
- **Enhanced schema** with multiple tables, indexes, and triggers
- **Bulk operations** and batch processing
- **Advanced analytics** using window functions and aggregations
- **Account search** with multiple filters
- **Transaction history** tracking
- **Materialized views** for performance optimization
- **Data lifecycle management** features

## Cleanup

1. To drop all the schema created by Enhanced Example run below command

    ```bash
    python enhanced_example.py --cleanup
    ```

    ```bash
    ##Sample Output##
    🧹 Enhanced CockroachDB Schema Cleanup
    ==================================================
    ⚠️  This will permanently delete the following objects:
    • accounts table (and all data)
    • transactions table (and all data)
    • account_summaries materialized view
    • update_account_timestamp function
    • account_update_trigger trigger

    Are you sure you want to proceed? (yes/no): yes
    🧹 Cleaning up enhanced schema...
    2025-10-13 12:03:04,813 - INFO - ✓ Dropped materialized view: account_summaries
    2025-10-13 12:03:04,823 - INFO - ✓ Dropped trigger: account_update_trigger
    2025-10-13 12:03:04,827 - INFO - ✓ Dropped function: update_account_timestamp
    2025-10-13 12:03:05,262 - INFO - ✓ Dropped table: transactions
    2025-10-13 12:03:05,595 - INFO - ✓ Dropped table: accounts
    ✅ Schema cleanup completed successfully!
    ```

1. To stop python virtual environment run below command

    ```bash
    deactivate
    ```

-------------

Navigate to ([Task5](./5_cleanup.md) | [Main Page](../README.md))