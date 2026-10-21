# Kubernetes: kubectl cheat sheet and pod status guide

## Everyday commands

```bash
kubectl get pods -A -o wide                    # all namespaces, with node and IP
kubectl get pods -n <ns> -w                    # watch changes
kubectl describe pod <pod> -n <ns>
kubectl logs <pod> -n <ns> -f --tail=100
kubectl exec -it <pod> -n <ns> -- sh
kubectl get events -n <ns> --sort-by=.lastTimestamp
kubectl get deploy,svc,ing -n <ns>
kubectl rollout restart deployment/<name> -n <ns>
kubectl scale deployment/<name> --replicas=3 -n <ns>
kubectl top pods -n <ns>                       # needs metrics-server
kubectl port-forward svc/<svc> 8080:80 -n <ns>
kubectl get pod <pod> -o yaml
kubectl auth can-i create pods -n <ns>
```

## What each pod STATUS means

| Status | Meaning | First command |
|---|---|---|
| Pending | Not scheduled yet (resources, taints, PVC) | `kubectl describe pod` |
| ContainerCreating | Scheduled; pulling image, mounting volumes, setting up network | `kubectl describe pod` (events) |
| ImagePullBackOff / ErrImagePull | Cannot pull the image: wrong name/tag, private registry without imagePullSecret, rate limit | `kubectl describe pod`; check image name and secret |
| CrashLoopBackOff | Container keeps crashing | `kubectl logs --previous` |
| OOMKilled | Container exceeded its memory limit (exit 137) | Raise limit, fix leak |
| CreateContainerConfigError | Missing ConfigMap/Secret key | `kubectl get cm,secret` |
| Error | Container exited non-zero | `kubectl logs` |
| Completed | Container finished successfully (normal for Jobs) | - |
| Evicted | Node under pressure (disk, memory) removed the pod | `kubectl describe node`; look for DiskPressure/MemoryPressure |
| Terminating (stuck) | Finalizer or node unreachable | `kubectl get pod -o yaml` for finalizers; last resort `kubectl delete pod <pod> --force --grace-period=0` |
| Running but 0/1 READY | Readiness probe failing | `kubectl describe pod`; check probe path/port |

## Context and namespace

```bash
kubectl config get-contexts
kubectl config use-context <name>
kubectl config set-context --current --namespace=<ns>
```
