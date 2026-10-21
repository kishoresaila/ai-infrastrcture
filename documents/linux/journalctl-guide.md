# Linux: journalctl guide

journalctl reads the systemd journal, the central log for services, the kernel and boot.

## Everyday commands

```bash
journalctl -u docker.service            # logs of one service
journalctl -xeu docker.service          # jump to the end with extra explanations
journalctl -u nginx -f                  # follow live (like tail -f)
journalctl -n 100 --no-pager            # last 100 lines
journalctl -p err -b                    # errors and worse since this boot
journalctl --since "1 hour ago"
journalctl --since "2026-10-20 09:00" --until "2026-10-20 10:00"
journalctl -k                           # kernel messages (like dmesg)
journalctl -b -1                        # previous boot
journalctl _PID=1234                    # one process
journalctl -o json-pretty -n 1          # show all fields of an entry
```

Priority levels for `-p`: emerg, alert, crit, err, warning, notice, info, debug.

## Disk usage and cleanup

```bash
journalctl --disk-usage
sudo journalctl --vacuum-time=7d        # delete entries older than 7 days
sudo journalctl --vacuum-size=500M      # shrink to 500 MB
```

Make the limit permanent in /etc/systemd/journald.conf: `SystemMaxUse=500M`, then `sudo systemctl restart systemd-journald`.

## Keep logs after reboot

By default the journal may be stored only in /run (lost on reboot). To persist it:

```bash
sudo mkdir -p /var/log/journal
sudo systemctl restart systemd-journald
# or set Storage=persistent in /etc/systemd/journald.conf
```

## Reading tips

- A service that "failed" usually has the real reason a few lines above the "Failed with result" line.
- Use `-b -1` after a crash or reboot to see what happened before.
- Non-root users need to be in the `systemd-journal` or `adm` group to read all logs.
