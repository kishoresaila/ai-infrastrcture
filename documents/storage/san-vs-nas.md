# Storage: SAN vs NAS, NFS vs SMB

## SAN vs NAS

| | SAN (Storage Area Network) | NAS (Network Attached Storage) |
|---|---|---|
| Access level | **Block** - the server sees a raw disk (LUN) and puts its own filesystem on it | **File** - the server mounts a shared filesystem |
| Protocols | Fibre Channel, iSCSI, FCoE, NVMe-oF | NFS, SMB/CIFS |
| Network | Dedicated FC fabric or a separate Ethernet VLAN | Normal LAN |
| Best for | Databases, VMs, clusters needing low latency | File shares, home directories, media, backups |
| Sharing | One LUN is normally used by one host (unless a cluster filesystem is used) | Many clients share the same files concurrently |
| Complexity / cost | Higher | Lower |

Short version: SAN delivers disks; NAS delivers files.

## NFS vs SMB

| | NFS | SMB/CIFS |
|---|---|---|
| Typical clients | Linux/Unix | Windows (also Linux, macOS) |
| Authentication | Host/IP based or Kerberos (NFSv4) | User-based, Active Directory integration |
| Strength | Simple, fast for Linux workloads, VM datastores | Windows file sharing, ACLs, AD |
| Ports | 2049 (NFSv4) | 445 |

### Mount examples

```bash
# NFS
sudo mount -t nfs4 nas01:/export/data /mnt/data
showmount -e nas01                                    # list exports (NFSv3)
# /etc/fstab
nas01:/export/data  /mnt/data  nfs4  defaults,_netdev  0 0

# SMB
sudo mount -t cifs //filer01/share /mnt/share -o username=svc_user,vers=3.0
```

### Quick troubleshooting

- `mount.nfs: Connection timed out` - firewall, wrong server, or nfs service down (`rpcinfo -p nas01`).
- `access denied by server` - the export list does not include this client IP; fix /etc/exports and run `exportfs -ra`.
- Hung NFS mounts block processes: use `soft` only when the application tolerates I/O errors; otherwise keep `hard` and fix the network.
- SMB `Permission denied` - check credentials, share and NTFS permissions, SMB version.
