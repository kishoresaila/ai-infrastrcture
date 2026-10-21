# DevOps: a repeatable troubleshooting method

## 1. Define the problem
What exactly fails? Since when? What changed (deploy, config, patch, certificate, network)? Who is affected - one host, one app, everyone?

## 2. Check the basics bottom-up

| Layer | Quick checks |
|---|---|
| Resources | `df -h`, `df -i`, `free -m`, `uptime`, `top`, `vmstat 1` |
| Process / service | `systemctl status <svc>`, `ps aux \| grep <svc>`, `journalctl -u <svc>` |
| Network | `ip a`, `ip r`, `ping`, `nc -zv host port`, `ss -tlnp`, `dig name` |
| Storage | `lsblk`, `mount`, `dmesg -T \| tail`, `iostat -xz 1` |
| Logs | `/var/log/messages` or `syslog`, `journalctl -p err -b` |
| Containers | `docker ps -a`, `docker logs`, `kubectl describe`, `kubectl logs` |

## 3. Form one hypothesis, test it, change one thing at a time
Record every change so you can revert it.

## 4. Fix, verify, and prevent
Confirm from the user's point of view, then add monitoring or automation so the failure is caught earlier next time (alerts at 80% disk, health checks, log rotation).

## Useful resource commands

```bash
free -h                         # memory (look at "available", not "free")
top -o %MEM                     # sort by memory
sudo dmesg -T | grep -i -E "oom|error|fail"
iostat -xz 1 5                  # disk latency (await) and utilisation (%util)
sudo ss -tlnp                   # listening ports and owning processes
```

## Out-of-memory (OOM) kills

```bash
sudo journalctl -k | grep -i "out of memory"
```

Log line `Out of memory: Killed process 2211 (java)` means the kernel killed the process because RAM and swap ran out. Fix by raising memory, setting application limits (for example the JVM -Xmx), adding swap as a stopgap, or fixing the leak.
