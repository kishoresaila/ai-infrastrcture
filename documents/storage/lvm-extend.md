# Extending an LVM logical volume

Order of operations: add disk -> pvcreate -> vgextend -> lvextend -> grow the filesystem.

```bash
lsblk
pvcreate /dev/sdb
vgextend vg_data /dev/sdb
vgs                                   # confirm free space
lvextend -L +50G /dev/vg_data/lv_data
# or use all free space:
lvextend -l +100%FREE /dev/vg_data/lv_data
```

## Grow the filesystem
```bash
resize2fs /dev/vg_data/lv_data        # ext4 (device path)
xfs_growfs /data                      # XFS (mount point, NOT device)
# shortcut: lvextend -r -L +50G ...   # resizes the filesystem in one step
```

## Notes
- XFS can only grow, never shrink. ext4 can be shrunk offline.
- Always verify with `df -h` and `lvs`.
- Take a backup/snapshot before any resize on production.
- Best practice: leave 10-20% free space in the VG for snapshots.
