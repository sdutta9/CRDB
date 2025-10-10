# Executing a Code Example

As part of the exercise, you will first clone the git repo here

1. Clone gitrepo. (This has been done within this repo so you can skip)

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

1. Make sure you delete the Accounts table that you previously created manually

    ```bash
    cockroach sql --host=cockroachdb.example.com:26257 --insecure --database=bank
    ```

    Run below sql command to delete "Accounts" table

    ```sql
    drop table accounts;
    ```

1. Export your Database url as an environment variable

    ```bash
    export DATABASE_URL="postgresql://root@cockroachdb.example.com:26257/bank?sslmode=disable"
    ```

1. Make sure it is set properly

    ```bash
    echo $DATABASE_URL 
    ```

1. Run the code

    ```bash
    python example.py
    ```

-------------

Navigate to ([Task5](./5_present_your_findings.md) | [Main Page](../README.md))