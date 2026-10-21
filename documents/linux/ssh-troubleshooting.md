# Linux: Troubleshooting SSH failures

Start from the error message - it tells you which layer is broken.

| Error | Meaning |
|---|---|
| Connection timed out | Packets are dropped: firewall, security group, wrong IP, host down |
| Connection refused | Host reachable but nothing listening on that port (sshd stopped or different port) |
| Permission denied (publickey) | Key not accepted: wrong user, wrong key, bad permissions, key not authorized |
| Permission denied (password) | Wrong password, or PasswordAuthentication disabled, or user not allowed |
| REMOTE HOST IDENTIFICATION HAS CHANGED | Host key differs from ~/.ssh/known_hosts |

## Client side

```bash
ssh -vvv user@host                 # verbose: shows which keys are offered and why auth fails
nc -zv host 22                     # is the port reachable?
ssh-keygen -R host                 # remove an outdated host key (only if you trust the change)
```

## Server side (use console access if SSH is down)

```bash
sudo systemctl status sshd         # service is "ssh" on Debian/Ubuntu
sudo ss -tlnp | grep :22           # is sshd listening, and on which port?
sudo sshd -t                       # test config syntax before restarting
sudo journalctl -u sshd -n 50      # on Debian/Ubuntu: -u ssh
sudo tail -f /var/log/secure       # RHEL; Debian/Ubuntu: /var/log/auth.log
```

## Firewall

```bash
sudo firewall-cmd --list-all                      # RHEL/Fedora
sudo firewall-cmd --permanent --add-service=ssh && sudo firewall-cmd --reload
sudo ufw status                                   # Ubuntu
```

Also check cloud security groups and any network firewall in between.

## Key authentication problems

Permissions must be strict or sshd silently ignores the keys:

```bash
chmod 700 ~/.ssh
chmod 600 ~/.ssh/authorized_keys
chmod go-w ~            # the home directory must not be group/world writable
```

On SELinux systems restore the context: `restorecon -Rv ~/.ssh`

## Common sshd_config causes

- `PermitRootLogin no` - root cannot log in.
- `PasswordAuthentication no` - password logins rejected.
- `AllowUsers` / `AllowGroups` - user not listed.
- `MaxStartups` reached or fail2ban/sshguard banned your IP (`sudo fail2ban-client status sshd`).
- Disk full or /etc/nologin present, or the account is locked (`sudo passwd -S user`).

After editing: `sudo sshd -t && sudo systemctl reload sshd`.
