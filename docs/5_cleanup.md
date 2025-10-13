# Cleanup your Cockroach Labs Field Technical Exercise Environment

1. Delete the entire KinD cluster by running below command

    ```bash
    # First find the name of your KinD cluster
    kind get clusters
    ```

    ```bash
    ##Sample Output##

    crdb-3node-cluster
    ```

    ```bash
    # Delete the entire cluster
    kind delete cluster --name crdb-3node-cluster
    ```

1. To stop `docker-mac-net-connect` tool run below command

    ```bash
    sudo brew services stop chipmk/tap/docker-mac-net-connect 
    ```

-------------

Navigate to ([Main Page](../README.md))