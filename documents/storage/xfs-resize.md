# Storage: resizing an XFS filesystem

## Key facts

- XFS can be **grown online** while mounted. It **cannot be shrunk**.
- `xfs_growfs` takes the **mount point**, not the device path.
- It grows to the size of the underlying block device (or LV) - you enlarge that first.

## Procedure on LVM

```bash
df -hT /data                                    # confirm it is xfs, note the size
sudo lvextend -L +20G /dev/vg_data/lv_data      # 1. grow the logical volume
sudo xfs_growfs /data                           # 2. grow the filesystem
df -h /data                                     # 3. verify
```

Shortcut: `sudo lvextend -r -L +20G /dev/vg_data/lv_data` does both.

## Procedure on a plain partition (no LVM)

```bash
sudo growpart /dev/sdb 1                        # from cloud-utils-growpart; grows partition 1
sudo xfs_growfs /data
```

## Inspect an XFS filesystem

```bash
xfs_info /data                                  # block size, agcount, ftype, log
sudo xfs_repair -n /dev/mapper/vg-lv            # dry-run check (filesystem must be unmounted)
```

## If you need a smaller XFS filesystem

You must back up, create a new smaller filesystem and restore:

```bash
sudo xfsdump -f /backup/data.xfsdump /data
# recreate LV smaller, mkfs.xfs, mount
sudo xfsrestore -f /backup/data.xfsdump /data
```

(Or `rsync -aHAX` to a new volume.) Verify the backup before destroying anything.

## Common errors

- `xfs_growfs: /dev/mapper/... is not a mounted XFS filesystem` - you passed a device or the filesystem is not XFS/mounted; use the mount point.
- `data size unchanged, skipping` - the underlying device was not enlarged first.
- Filesystem still looks full after growth - check `df -i` and deleted-but-open files (`lsof +L1`).
