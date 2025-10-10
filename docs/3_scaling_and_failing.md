# Scaling and Failing

As part of this exercise, you will scale up and scale down your CockroachDB cluster with an active load and observe the way it behaves.

1. Update your CockroachDB cluster from 3 nodes to 4 nodes and watch for 5 minutes.

    ```bash
    kubectl scale statefulset cockroachdb --replicas=4
    ```

     ```bash
    ##Sample Output##
    statefulset.apps/cockroachdb scaled
    ```

    {{TODO: Add screenshot for observation}}

1. Now gracefully remove a node from the cluster and see how the system behaves. 

    For this task, first you will run below command to check the node status for your CockroachDB cluster.

    ```bash
    cockroach node status --host=cockroachdb.example.com:26257 --insecure
    ```

    ```bash
       id |                          address                          |                        sql_address                        |  build  |              started_at              |              updated_at              | locality | attrs | is_available | is_live
     -----+-----------------------------------------------------------+-----------------------------------------------------------+---------+--------------------------------------+--------------------------------------+----------+-------+--------------+----------
        1 | cockroachdb-0.cockroachdb.default.svc.cluster.local:26257 | cockroachdb-0.cockroachdb.default.svc.cluster.local:26257 | v25.3.2 | 2025-10-10 03:03:45.372156 +0000 UTC | 2025-10-10 03:57:45.357952 +0000 UTC |          | []    | true         | true
        2 | cockroachdb-2.cockroachdb.default.svc.cluster.local:26257 | cockroachdb-2.cockroachdb.default.svc.cluster.local:26257 | v25.3.2 | 2025-10-10 03:36:33.870979 +0000 UTC | 2025-10-10 03:57:45.956039 +0000 UTC |          | []    | true         | true
        3 | cockroachdb-1.cockroachdb.default.svc.cluster.local:26257 | cockroachdb-1.cockroachdb.default.svc.cluster.local:26257 | v25.3.2 | 2025-10-10 03:36:33.604466 +0000 UTC | 2025-10-10 03:57:45.686746 +0000 UTC |          | []    | true         | true
        4 | cockroachdb-3.cockroachdb.default.svc.cluster.local:26257 | cockroachdb-3.cockroachdb.default.svc.cluster.local:26257 | v25.3.2 | 2025-10-10 03:24:39.978172 +0000 UTC | 2025-10-10 03:27:14.668713 +0000 UTC |          | []    | false        | false
    (4 rows)
    ```

    You will then remove node 4 (cockroachdb-3) from the cluster gracefully. To do that first you have to decommission node 4 by running below command

    ```bash
    cockroach node decommission 4 --host=cockroachdb.example.com:26257 --insecure
    ```

    ```bash
    ##Sample Output##

    id | is_live | replicas | is_decommissioning |   membership    | is_draining | readiness | blocking_ranges
    -----+---------+----------+--------------------+-----------------+-------------+-----------+------------------
    4 |  true   |       50 |        true        | decommissioning |    false    |   ready   |               0
    (1 row)
    ..
    id | is_live | replicas | is_decommissioning |   membership    | is_draining | readiness | blocking_ranges
    -----+---------+----------+--------------------+-----------------+-------------+-----------+------------------
    4 |  true   |       49 |        true        | decommissioning |    false    |   ready   |               0
    (1 row)
    ....
    id | is_live | replicas | is_decommissioning |   membership    | is_draining | readiness | blocking_ranges
    -----+---------+----------+--------------------+-----------------+-------------+-----------+------------------
    4 |  true   |       38 |        true        | decommissioning |    false    |   ready   |               0
    (1 row)
    .
    .
    .
    id | is_live | replicas | is_decommissioning |   membership    | is_draining | readiness | blocking_ranges
    -----+---------+----------+--------------------+-----------------+-------------+-----------+------------------
    4 |  true   |        1 |        true        | decommissioning |    false    |   ready   |               0
    (1 row)

    id | is_live | replicas | is_decommissioning |   membership    | is_draining | readiness | blocking_ranges
    -----+---------+----------+--------------------+-----------------+-------------+-----------+------------------
    4 |  true   |        0 |        true        | decommissioning |    false    |   ready   |               0
    (1 row)
    draining node n4
    node is draining... remaining: 65
    node is draining... remaining: 0 (complete)
    node n4 drained successfully

    No more data reported on target nodes. Please verify cluster health before removing the nodes.
    ```

    Once Node 4 has been `Decommissioned`, you can now scale down your Statefulset to 3 nodes by running below command

    ```bash
    kubectl scale sts cockroachdb --replicas=3
    ```

    ```bash
    ##Sample Output##
    statefulset.apps/cockroachdb scaled
    ```


1. Now remove 1 node forcefully

    ```bash
    kubectl scale sts cockroachdb --replicas=2
    ```


-------------

Navigate to ([Task4](./4_execute_code_example.md) | [Main Page](../README.md))