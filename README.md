# CRDB

CockroachDB test out

## Launch and Initialize CRDB

### Start 3 node KIND cluster

1. Install [kind](https://kind.sigs.k8s.io/docs/user/quick-start/#installation).

    ```bash
    brew install kind
    ```

1. Creating Kind cluster. Find the latest image of Kind from dockerhub.(<https://hub.docker.com/r/kindest/node/tags>). Create your Kind config file accordingly.

    ```bash
    kind create cluster --config kind/3node-config.yaml
    ```

1. Setup kubernetes context

    ```bash
    kubectl cluster-info --context kind-crdb-3node-cluster
    ```

1. validate 3 node kubernetes cluster is running

    ```bash
    kubectl get nodes
    ```

### Start Cockroach DB

Follow below guide(<https://www.cockroachlabs.com/docs/v25.3/orchestrate-a-local-cluster-with-kubernetes>) for details.

1. Change directory to the `<project_working_dir>/cockroachdb`

    ```bash
    cd cockroachdb
    ```

1. Install needed CRDs

    ```bash
    curl -O https://raw.githubusercontent.com/cockroachdb/cockroach-operator/v2.18.2/install/crds.yaml 
    k apply -f crds.yaml 
    ```

    ```bash
    ##Sample Output##
    ## Ignore the warnings

    ~/CRDB/cockroachdb » k apply -f crds.yaml

    Warning: unrecognized format "int64"
    Warning: unrecognized format "int32"
    customresourcedefinition.apiextensions.k8s.io/crdbclusters.crdb.cockroachlabs.com created
    ```

1. Install operator

    ```bash
    curl -O https://raw.githubusercontent.com/cockroachdb/cockroach-operator/v2.18.2/install/operator.yaml 
    k apply -f operator.yaml
    ```

    ```bash
    ##Sample Output##                                                                                       
    ~/CRDB/cockroachdb » k apply -f operator.yaml

    namespace/cockroach-operator-system created
    serviceaccount/cockroach-operator-sa created
    clusterrole.rbac.authorization.k8s.io/cockroach-operator-role created
    clusterrolebinding.rbac.authorization.k8s.io/cockroach-operator-rolebinding created
    service/cockroach-operator-webhook-service created
    deployment.apps/cockroach-operator-manager created
    mutatingwebhookconfiguration.admissionregistration.k8s.io/cockroach-operator-mutating-webhook-configuration created
    validatingwebhookconfiguration.admissionregistration.k8s.io/cockroach-operator-validating-webhook-configuration created
    ```

1. [Optional Step] Set your current namespace to the one used by the Public operator

    ```bash
    kubectl config set-context --current --namespace=cockroach-operator-system
    ```

1. Validate that the operator is running:

    ```bash
    kubectl get pods [-n cockroach-operator-system]
    ```

    ```bash
    ##Sample Output##
    ~/CRDB/cockroachdb » k get pods -n cockroach-operator-system

    NAME                                          READY   STATUS    RESTARTS   AGE
    cockroach-operator-manager-5cfd4f9b99-qp2xq   1/1     Running   0          6m32s
    ```

1. Download example.yaml, a custom resource that tells the operator how to configure the Kubernetes cluster.

    ```bash
    curl -O https://raw.githubusercontent.com/cockroachdb/cockroach-operator/v2.18.2/examples/example.yaml
    ```

1. Change the storage from `"60Gi"` to `"20Gi"` within the downloaded `example.yaml` file and then apply it to your cluster

    ```bash
    kubectl apply -f example.yaml [-n cockroach-operator-system]
    ```

    ```bash
    ##Sample Output##
    crdbcluster.crdb.cockroachlabs.com/cockroachdb creted
    ```

1. Check that the pods were running:

    ```bash
    kubectl get pods [-n cockroach-operator-system]
    ```

### Use the built-in SQL client

1. To use the CockroachDB SQL client, first launch a secure pod running the `cockroach` binary.

    ```bash
    curl -O https://raw.githubusercontent.com/cockroachdb/cockroach-operator/v2.18.2/examples/client-secure-operator.yaml
    ```

    ```bash
    kubectl apply -f client-secure-operator.yaml -n cockroach-operator-system
    ```

1. Get a shell into the CockroachDB SQL client pod:

    ```bash
    kubectl exec -it cockroachdb-client-secure -n cockroach-operator-system -- /bin/bash 
    ```

1. Start the CockroachDB built-in SQL client:

    ```bash
    ./cockroach sql --certs-dir=/cockroach/cockroach-certs --host=cockroachdb-public
    ```

    ```bash
    ##Sample Output##
    [root@cockroachdb-client-secure cockroach]# ./cockroach sql --certs-dir=/cockroach/cockroach-certs --host=cockroachdb-public

    #
    # Welcome to the CockroachDB SQL shell.
    # All statements must be terminated by a semicolon.
    # To exit, type: \q.
    #
    # Server version: CockroachDB CCL v25.2.2 (aarch64-unknown-linux-gnu, built 2025/06/23 13:45:32, go1.23.7 X:nocoverageredesign) (same version as client)
    # Cluster ID: 6fe0de8a-9a57-4b86-a2f7-71da42e4fd50
    #
    # Enter \? for a brief introduction.
    #
    root@cockroachdb-public:26257/defaultdb>                                                                                                                                              
    M-? toggle key help • C-d erase/stop • C-c clear/cancel • M-. hide/show prompt
    ```

1. Run some basic SQL statements to build a database:

    ```sql
    CREATE DATABASE bank;

    CREATE TABLE bank.accounts (id INT PRIMARY KEY, balance DECIMAL);

    INSERT INTO bank.accounts VALUES (1, 1000.50);

    SELECT * FROM bank.accounts;
    ```

    ```bash
    ##Sample Output##
    root@cockroachdb-public:26257/defaultdb> CREATE DATABASE bank;
    CREATE DATABASE

    Time: 176ms total (execution 166ms / network 10ms)

    root@cockroachdb-public:26257/defaultdb> CREATE TABLE bank.accounts (id INT PRIMARY KEY, balance DECIMAL);
    CREATE TABLE

    Time: 39ms total (execution 28ms / network 10ms)

    root@cockroachdb-public:26257/defaultdb> INSERT INTO bank.accounts VALUES (1, 1000.50);                                                         INSERT 0 1

    Time: 29ms total (execution 29ms / network 0ms)

    root@cockroachdb-public:26257/defaultdb> SELECT * FROM bank.accounts;                                                                           
    id | balance
    -----+----------
    1 | 1000.50
    (1 row)

    Time: 5ms total (execution 5ms / network 0ms)
    ```

1. Create a user with a password. You will need this username and password to access the DB Console later.

    ```sql
    CREATE USER shouvik WITH PASSWORD 'shouvik';
    ```

    ```bash
    ##Sample Output##
    root@cockroachdb-public:26257/defaultdb> CREATE USER shouvik WITH PASSWORD 'shouvik';
    CREATE ROLE

    Time: 99ms total (execution 98ms / network 0ms)
    ```

1. Exit the SQL shell

    ```sql
    \q
    ```

1. Exit pod

    ```bash
    exit
    ```

### Access the DB console

1. Get a shell into the CockroachDB SQL client pod:

    ```bash
    kubectl exec -it cockroachdb-client-secure -n cockroach-operator-system -- /bin/bash 
    ```

1. Start the CockroachDB built-in SQL client:

    ```bash
    ./cockroach sql --certs-dir=/cockroach/cockroach-certs --host=cockroachdb-public
    ```

1. Assign user that you created in previous section (`shouvik` in my case) to the admin role (you only need to do this once):

    ```sql
    GRANT admin TO shouvik;
    ```

    ```bash
    root@cockroachdb-public:26257/defaultdb> GRANT admin TO shouvik;
    GRANT

    Time: 92ms total (execution 92ms / network 0ms)
    ```

1. Exit the SQL shell

    ```sql
    \q
    ```

1. Exit pod

    ```bash
    exit
    ```

1. In a new terminal window, port-forward from your local machine to the `cockroachdb-public` service:

    ```bash
    kubectl port-forward service/cockroachdb-public -n cockroach-operator-system 8080
    ```

1. Go to <https://localhost:8080> and log in with the username and password you created earlier.

1. In the UI, verify that the cluster is running as expected:

    - View the Node List to ensure that all nodes successfully joined the cluster.
    - Click the Databases tab on the left to verify that bank is listed.

### Setup NGINX Ingress controller as the load balancer

To install NGINX Plus Ingress controller use this [official guide](https://docs.nginx.com/nginx-ingress-controller/installation/installing-nic/installation-with-manifests/)

1. Change directory to the `<project_working_dir>/nginx`

    ```bash
    cd nginx
    ```

1. Install needed manifest files

    ```bash
    kubectl apply -f https://raw.githubusercontent.com/nginx/kubernetes-ingress/v5.2.0/deployments/common/ns-and-sa.yaml
    kubectl apply -f https://raw.githubusercontent.com/nginx/kubernetes-ingress/v5.2.0/deployments/rbac/rbac.yaml
    kubectl apply -f https://raw.githubusercontent.com/nginx/kubernetes-ingress/v5.2.0/examples/common-secrets/default-server-secret-NGINXIngressController.yaml
    kubectl apply -f https://raw.githubusercontent.com/nginx/kubernetes-ingress/v5.2.0/deployments/common/nginx-config.yaml
    kubectl apply -f https://raw.githubusercontent.com/nginx/kubernetes-ingress/v5.2.0/deployments/common/plus-mgmt-configmap.yaml
    kubectl apply -f https://raw.githubusercontent.com/nginx/kubernetes-ingress/v5.2.0/deploy/crds.yaml
    
    ```

    ```bash
    ##Sample Output##
    namespace/nginx-ingress created
    serviceaccount/nginx-ingress created
    clusterrole.rbac.authorization.k8s.io/nginx-ingress created
    clusterrolebinding.rbac.authorization.k8s.io/nginx-ingress created
    secret/default-server-secret created
    configmap/nginx-config created
    Warning: unrecognized format "int64"
    configmap/nginx-config-mgmt created
    customresourcedefinition.apiextensions.k8s.io/dnsendpoints.externaldns.nginx.org created
    customresourcedefinition.apiextensions.k8s.io/globalconfigurations.k8s.nginx.org created
    customresourcedefinition.apiextensions.k8s.io/policies.k8s.nginx.org created
    customresourcedefinition.apiextensions.k8s.io/transportservers.k8s.nginx.org created
    customresourcedefinition.apiextensions.k8s.io/virtualserverroutes.k8s.nginx.org created
    customresourcedefinition.apiextensions.k8s.io/virtualservers.k8s.nginx.org created
    ```

1. Export NGINX Plus jwt token into an environment variable

    ```bash
    export jwt_token=$(cat nginx-repo.jwt)
    ```

1. Create two secrets using the jwt token

    ```bash
    kubectl create secret docker-registry regcred --docker-server=private-registry.nginx.com --docker-username=$jwt_token --docker-password=none -n nginx-ingress

    kubectl create secret generic license-token --from-file=license.jwt=nginx-repo.jwt --type=nginx.com/license -n nginx-ingress
    ```

1. Install modified manifest files

    ```bash
    kubectl apply -f ingress-class.yaml
    kubectl apply -f nginx-config-mgmt.yaml
    kubectl apply -f nginx-plus-ingress.yaml
    ```

    ```bash
    ##Sample Output##
    ingressclass.networking.k8s.io/nginx created
    deployment.apps/nginx-ingress created
    ```

1. Install `docker-mac-net-connect`. It is a tool that allows you to connect directly to containers running inside Docker Desktop's virtual machine on macOS via their internal IP addresses. It works by creating a virtual network interface on your Mac that routes traffic to the Docker VM.

    ```bash
    brew install chipmk/tap/docker-mac-net-connect
    ```

    ```bash
    sudo brew services start chipmk/tap/docker-mac-net-connect 
    ```

1. Install metallb to expose nginx service using loadbalancer type

    ```bash
    kubectl apply -f https://raw.githubusercontent.com/metallb/metallb/v0.15.2/config/manifests/metallb-native.yaml
    ```

1. Install metallb related config manifest file

    ```bash
    kubectl apply -f metallb/metallb-config.yaml
    ```

1. Create a LoadBalancer service

    ```bash
    kubectl apply -f https://raw.githubusercontent.com/nginx/kubernetes-ingress/v5.2.0/deployments/service/loadbalancer.yaml
    ```

1. Expose NGINX Plus Dashboard for live monitoring

    ```bash
    kubectl apply -f dashboard-vs.yaml
    ```

1. Update your local host file to accordingly to resolve the new FQDN to the external IP of `nginx-ingress` service.

    ```bash
    vi /etc/hosts
    ```

    Add an entry in the file similar to below

    ```bash
    # Kind related 
    172.18.5.10 dashboard.example.com
    ```


### Expose CockroachDB services

1. Apply a self-signed cert

    ```bash
    kubectl apply -f cockroachdb-secret.yaml
    ```

1. Apply the virtual server to create the FQDN

    ```bash
    kubectl apply -f cockroachdb-vs.yaml
    ```

1. Add an entry in `/etc/hosts` file

    ```bash
    sudo vi /etc/hosts
    ```

    Add an entry in the file similar to below

    ```bash
    # Kind related
    172.18.5.10 dashboard.example.com cockroachdb.example.com
    ```

### [Optional] Cleanup

1. To stop `docker-mac-net-connect` tool run below command

    ```bash
    sudo brew services stop chipmk/tap/docker-mac-net-connect 
    ```
