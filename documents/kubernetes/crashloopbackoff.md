# CrashLoopBackOff

CrashLoopBackOff means a container starts, crashes, and kubelet keeps restarting it with an exponentially increasing back-off delay (10s, 20s, 40s ... up to 5 minutes). It is a symptom, not a root cause.

## Common causes
- Application error or bad config at startup (missing env var, wrong ConfigMap/Secret key)
- Wrong container command or entrypoint
- Liveness probe failing, so kubelet kills a healthy-but-slow app
- OOMKilled: memory limit too low (exit code 137)
- Missing dependency (database, service not reachable)
- Permission problems on a mounted volume

## Diagnose
```bash
kubectl get pods
kubectl logs <pod> --previous          # logs of the crashed container
kubectl describe pod <pod>             # Events, Last State, Exit Code, Reason
kubectl get events --sort-by=.lastTimestamp
```

## Exit codes
- 0 = process finished (not a long-running process)
- 1 = application error
- 137 = SIGKILL, usually OOMKilled
- 143 = SIGTERM

## Fix
Correct the config/command, raise memory limits, relax the liveness probe (initialDelaySeconds), or fix the dependency. Then `kubectl rollout restart deployment/<name>`.
