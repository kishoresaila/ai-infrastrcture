# Container restarting continuously

## Diagnose
```bash
docker ps -a                                   # STATUS: Restarting (1) ...
docker logs --tail 100 <container>
docker inspect <container> --format '{{.State.ExitCode}} {{.State.OOMKilled}}'
docker inspect <container> --format '{{json .HostConfig.RestartPolicy}}'
docker events --since 10m
```

## Common causes
- Exit code 1: application error. 137: OOM killed or SIGKILL. 139: segfault. 127: command not found.
- Restart policy `always` / `unless-stopped` re-launches a crashing process forever.
- Failing HEALTHCHECK (with an orchestrator that restarts unhealthy containers).
- Missing env vars, wrong volume permissions, port already in use.

## Fix
Fix the root cause shown in the logs, raise `--memory`, or temporarily set `docker update --restart=no <container>` to stop the loop while debugging. Add a HEALTHCHECK with a sensible start period.
