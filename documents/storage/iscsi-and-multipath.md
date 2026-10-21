# Storage: iSCSI login process and multipath

## iSCSI concepts

- **Target**: the storage array/server that exposes LUNs. Identified by an IQN (iqn.2026-01.com.example:storage1).
- **Initiator**: the host that connects. Also has an IQN (in /etc/iscsi/initiatorname.iscsi).
- **Portal**: target IP:port (default 3260).
- **LUN**: a block device presented by the target.

## Login process (Linux, open-iscsi)

```bash
sudo dnf install iscsi-initiator-utils device-mapper-multipath   # RHEL
sudo apt install open-iscsi multipath-tools                      # Debian/Ubuntu
cat /etc/iscsi/initiatorname.iscsi                               # give this IQN to the storage admin for LUN masking

# 1. Discovery - ask the portal which targets it offers
sudo iscsiadm -m discovery -t sendtargets -p 192.168.10.50:3260

# 2. Login - open the session
sudo iscsiadm -m node -T iqn.2026-01.com.example:storage1 -p 192.168.10.50 --login

# 3. Verify
sudo iscsiadm -m session -P 3
lsblk                                                            # new disk appears (e.g. /dev/sdb)

# 4. Make it persistent across reboots
sudo iscsiadm -m node -T iqn.2026-01.com.example:storage1 -p 192.168.10.50 \
  --op update -n node.startup -v automatic
sudo systemctl enable --now iscsid

# Logout
sudo iscsiadm -m node -T iqn.2026-01.com.example:storage1 -p 192.168.10.50 --logout
```

Flow: initiator -> discovery (SendTargets) -> target list -> login (authentication, optional CHAP, session negotiation) -> LUNs appear as SCSI disks -> partition/format/mount.

In /etc/fstab for iSCSI disks use `_netdev` so mounting waits for the network.

## Troubleshooting iSCSI

- Discovery works but no disk after login: LUN masking/ACL on the array does not include your initiator IQN.
- Login fails with authentication error: CHAP username/secret mismatch (`node.session.auth.*` in /etc/iscsi/iscsid.conf).
- Cannot reach portal: `nc -zv 192.168.10.50 3260`, check VLAN, MTU (jumbo frames must match end to end) and firewall.
- Session drops: check `journalctl -u iscsid`, network errors on the NIC (`ethtool -S`).

## Multipath

Multipath presents **several physical paths** (different HBAs/NICs/controllers) to the same LUN as **one device** (/dev/mapper/mpatha), giving redundancy (path failover) and optionally load balancing.

Without multipath the OS would see the same LUN as /dev/sdb, /dev/sdc, ... - writing to several of them corrupts data.

```bash
sudo mpathconf --enable --with_multipathd y         # RHEL; or create /etc/multipath.conf manually
sudo systemctl enable --now multipathd
sudo multipath -ll                                   # show maps and path states (active/ready vs failed/faulty)
sudo multipath -v2                                   # (re)create maps
sudo multipathd show paths
sudo multipath -f mpatha                             # flush a map (must be unused)
```

Minimal /etc/multipath.conf:

```
defaults {
    user_friendly_names yes
    find_multipaths yes
}
```

Path policies: `round-robin`, `service-time`, `queue-length`. Use the settings recommended by your storage vendor for the array model.

Always put the filesystem on the **/dev/mapper/mpathX** (or LVM on it), never on an individual /dev/sdX path.
