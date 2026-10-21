# Pod stuck in Pending

Pending means the scheduler has not placed the pod on a node yet (or images are still being prepared).

## Causes
- Insufficient CPU/memory on all nodes (requests too high)
- Node taints without matching tolerations
- nodeSelector / affinity matches no node
- PersistentVolumeClaim not bound (no StorageClass or no free PV)
- ResourceQuota exceeded in the namespace

## Diagnose
```bash
kubectl describe pod <pod>      # read the Events section: "FailedScheduling"
kubectl get nodes
kubectl describe node <node>    # Allocatable vs Allocated resources, Taints
kubectl get pvc
kubectl get resourcequota -n <ns>
```

## Fix
Lower resource requests, add nodes, add tolerations, fix the PVC/StorageClass, or raise the quota.
