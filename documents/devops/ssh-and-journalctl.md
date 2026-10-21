# Troubleshooting SSH failure

```bash
ssh -vvv user@host                    # client-side verbose
systemctl status sshd                 # is the service up?
journalctl -u sshd -n 50 --no-pager   # server-side reason
ss -tlnp | grep :22                   # listening?
sshd -t                               # validate config
```
Common causes: sshd down, firewall blocking 22 (`firewall-cmd --list-all`, `ufw status`), wrong key permissions (~/.ssh 700, authorized_keys 600), PermitRootLogin/PasswordAuthentication settings, SELinux context, full disk.

# Explaining journalctl
journalctl reads the systemd journal.
```bash
journalctl -u docker.service          # one unit
journalctl -xe                        # recent with explanations
journalctl -b -p err                  # this boot, errors only
journalctl --since "1 hour ago"
journalctl -f                         # follow
journalctl --disk-usage
journalctl --vacuum-time=7d
```

# Failed to start docker.service
Check `systemctl status docker` and `journalctl -xeu docker`. Frequent causes: invalid /etc/docker/daemon.json, full disk, port/socket conflict, storage driver corruption, iptables/nftables issues.
