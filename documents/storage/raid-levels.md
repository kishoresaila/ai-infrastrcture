# RAID levels

| Level | Min disks | Usable capacity | Fault tolerance | Notes |
|-------|-----------|-----------------|-----------------|-------|
| RAID 0 | 2 | N x disk | none | Striping, fastest, no redundancy |
| RAID 1 | 2 | 1 x disk | 1 disk | Mirroring |
| RAID 5 | 3 | (N-1) x disk | 1 disk | Distributed parity; slow rebuilds on large disks |
| RAID 6 | 4 | (N-2) x disk | 2 disks | Double parity; preferred for large SATA/NL-SAS |
| RAID 10 | 4 | N/2 x disk | 1 per mirror pair | Mirror + stripe; best for databases and random writes |

## RAID 10
RAID 10 (1+0) stripes across mirrored pairs. It survives one failure per pair, rebuilds fast (a copy, no parity maths), and has no write penalty like RAID 5 (write penalty 4) or RAID 6 (penalty 6). Cost: 50% usable capacity.

## Best practices
RAID is not a backup. Use hot spares, monitor SMART, and prefer RAID 6 or RAID 10 over RAID 5 for disks larger than 2 TB.
