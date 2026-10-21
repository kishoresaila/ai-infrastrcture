# Linux: Fixing "Failed to start <service>" (systemd)

## Standard diagnosis

```bash
systemctl status myservice -l --no-pager     # state, exit code, last log lines
journalctl -xeu myservice                    # full log with explanations
systemctl cat myservice                      # the unit file actually in use, including drop-ins
systemctl list-units --failed                # everything that is failed
```

Read the status line:

- `code=exited, status=1/FAILURE` - the program itself returned an error; the reason is in the journal.
- `status=203/EXEC` - systemd could not execute the binary (wrong path, missing, not executable, bad shebang).
- `status=200/CHDIR`, `217/USER` - bad WorkingDirectory or User in the unit.
- `code=killed, signal=KILL` - often the OOM killer; check `journalctl -k | grep -i "out of memory"`.
- `Start request repeated too quickly` / `start-limit-hit` - crash loop; fix the cause, then `systemctl reset-failed myservice`.
- `Dependency failed` - a unit in Requires= did not start; check that unit first.

## Common root causes

1. Configuration syntax error - validate with the program's own test (`nginx -t`, `sshd -t`, `named-checkconf`).
2. Port already in use - `sudo ss -tlnp | grep :80`.
3. Permission problems or SELinux/AppArmor denial - `sudo ausearch -m avc -ts recent`, `journalctl | grep -i apparmor`.
4. Missing file, mount or directory not yet available at boot - add `RequiresMountsFor=/data` or `After=network-online.target`.
5. Disk full or out of memory.

## After changing a unit file

```bash
sudo systemctl daemon-reload
sudo systemctl restart myservice
sudo systemctl enable myservice          # start at boot
systemd-analyze verify /etc/systemd/system/myservice.service
```

Use `sudo systemctl edit myservice` to add overrides in a drop-in file instead of editing vendor unit files.
