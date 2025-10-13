kubectl delete  -f cockroachdb-statefulset.yaml
kubectl delete -f cluster-init.yaml
kubectl delete pvc -l app=cockroachdb