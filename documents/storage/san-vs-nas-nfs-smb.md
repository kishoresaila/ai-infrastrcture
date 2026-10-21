# SAN vs NAS

- SAN: block-level storage over a dedicated network (Fibre Channel or iSCSI). Hosts see a raw disk (LUN) and put their own filesystem on it. Low latency, used for databases and VMs.
- NAS: file-level storage over the LAN (NFS, SMB). Clients see shared folders; the NAS owns the filesystem. Easy sharing.

# NFS vs SMB
- NFS: native to Linux/Unix, stateless-ish (NFSv4 is stateful), uses exports (/etc/exports), mounted with `mount -t nfs server:/share /mnt`.
- SMB/CIFS: native to Windows, uses user/AD authentication, mounted with `mount -t cifs //server/share /mnt -o username=...`.

# iSCSI login process
```bash
iscsiadm -m discovery -t sendtargets -p <portal-ip>:3260
iscsiadm -m node -T <iqn> -p <portal-ip> --login
lsblk                       # new disk appears
iscsiadm -m session
```
Make it persistent: `iscsiadm -m node -T <iqn> --op update -n node.startup -v automatic`.

# Multipath
Multipath (dm-multipath) combines several physical paths to the same LUN into one device (/dev/mapper/mpathX) for failover and load balancing. Check with `multipath -ll`, config in /etc/multipath.conf.
