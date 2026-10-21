# No space left on device

The error appears when a filesystem is out of blocks OR out of inodes.

## Check
```bash
df -h                 # block usage per filesystem
df -i                 # inode usage (100% IUse% also causes this error)
du -xh / --max-depth=1 2>/dev/null | sort -h | tail
lsof +L1              # deleted files still held open by a process
```

## Free space
```bash
journalctl --vacuum-time=7d       # or --vacuum-size=500M
apt clean   # or: dnf clean all
docker system prune               # review first; removes unused data
find /var/log -name "*.gz" -mtime +30 -delete
```
Deleted-but-open files: restart the owning process to release the space.

## Prevention
Configure logrotate, monitor with alerts at 80% usage, and extend the volume (see LVM notes).
