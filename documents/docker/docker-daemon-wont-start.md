# Docker: "Failed to start docker.service"

## Diagnose

```bash
sudo systemctl status docker --no-pager -l
sudo journalctl -u docker.service -n 100 --no-pager
sudo systemctl status containerd
sudo dockerd -D                          # run the daemon in the foreground with debug output (stop the service first)
```

The journal line just above "Failed to start" holds the real cause.

## Common causes

### 1. Bad /etc/docker/daemon.json
Invalid JSON or an unknown option stops the daemon.

```bash
python3 -m json.tool /etc/docker/daemon.json
sudo dockerd --validate --config-file=/etc/docker/daemon.json
```

### 2. "directives are specified both as a flag and in the configuration file: hosts"
The systemd unit starts dockerd with `-H fd://` while daemon.json also defines `hosts`. Remove one of them, or add a drop-in that clears ExecStart:

```bash
sudo systemctl edit docker
# [Service]
# ExecStart=
# ExecStart=/usr/bin/dockerd
sudo systemctl daemon-reload && sudo systemctl restart docker
```

### 3. Disk full on /var/lib/docker
```bash
df -h /var/lib/docker ; df -i /var/lib/docker
```
Free space or move the data root (`"data-root": "/data/docker"` in daemon.json).

### 4. Storage driver or corrupt data
Errors mentioning overlay2, "failed to mount", or "error creating overlay mount" - check the filesystem supports overlay (XFS needs `ftype=1`: `xfs_info /var/lib/docker | grep ftype`). As a last resort, move /var/lib/docker aside - this deletes all images, containers and volumes.

### 5. Network / iptables problems
Messages about iptables or bridge `docker0`: ensure iptables/nftables is installed and not blocked by another firewall service; restart firewalld, then docker.

### 6. containerd or socket problems
```bash
sudo systemctl restart containerd
sudo systemctl status docker.socket
ls -l /var/run/docker.sock
```

### 7. SELinux / permissions
Check `sudo ausearch -m avc -ts recent` on RHEL-family hosts.

## Verify after the fix

```bash
sudo systemctl restart docker
docker info | head
docker run --rm hello-world
sudo systemctl enable docker
```
