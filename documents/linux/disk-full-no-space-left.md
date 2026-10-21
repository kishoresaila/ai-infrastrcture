# Linux: "No space left on device"

This error means the filesystem has no free blocks, no free inodes, or a deleted file is still held open by a process.

## Step 1 - Find which filesystem is full

```bash
df -hT          # block usage and filesystem type
df -i           # inode usage; 100% IUse% also causes this error
```

## Step 2 - Find what is using the space

```bash
sudo du -xh --max-depth=1 / | sort -h | tail -15
sudo du -xh --max-depth=1 /var | sort -h | tail -15
sudo find / -xdev -type f -size +500M -exec ls -lh {} \; 2>/dev/null
```

Use `-x` (du) and `-xdev` (find) so the scan stays on one filesystem and does not walk into other mounts such as /proc or NFS.

## Step 3 - Free space safely

```bash
# systemd journal
journalctl --disk-usage
sudo journalctl --vacuum-time=7d        # or: --vacuum-size=500M

# package caches
sudo apt clean                           # Debian/Ubuntu
sudo dnf clean all                       # RHEL/Fedora

# a huge log that a process is still writing: truncate, do not rm
sudo truncate -s 0 /var/log/app/big.log

# Docker data
docker system df
docker system prune                      # removes stopped containers, unused networks, dangling images - review first
```

## Deleted files that still use space

If `df` shows the disk full but `du` adds up to much less, a process is holding a deleted file open:

```bash
sudo lsof +L1
```

Space is released only when the process closes the file. Restart the owning service.

## Inode exhaustion

If `df -i` shows 100%, you have millions of tiny files (mail queue, PHP sessions, cache dirs):

```bash
sudo find /var -xdev -type f | cut -d/ -f1-4 | sort | uniq -c | sort -n | tail
```

Delete or archive the offending directory. You cannot add inodes to an existing ext4 filesystem; XFS allocates inodes dynamically.

## Long-term fix

- Extend the logical volume (see storage/lvm-extend.md).
- Configure logrotate and journald limits (SystemMaxUse=).
- Put /var/log and /var/lib/docker on their own volumes so one cannot starve the root filesystem.
- Alert at 80% usage.
