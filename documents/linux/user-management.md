# Linux: user and group management

## Create a user

```bash
sudo useradd -m -s /bin/bash kishore         # -m creates the home directory
sudo passwd kishore                          # set the password
```

On Debian/Ubuntu the friendlier wrapper is `sudo adduser kishore`.

## Give sudo rights

```bash
sudo usermod -aG wheel kishore               # RHEL, Rocky, Alma, Fedora
sudo usermod -aG sudo kishore                # Debian, Ubuntu
```

Always use `-aG` (append). `-G` without `-a` replaces all existing supplementary groups.

## Common tasks

```bash
id kishore                                   # uid, gid, groups
sudo usermod -L kishore                      # lock the account
sudo usermod -U kishore                      # unlock
sudo chage -l kishore                        # password aging info
sudo chage -E 2026-12-31 kishore             # account expiry date
sudo userdel kishore                         # delete user, keep home
sudo userdel -r kishore                      # delete user and home directory
sudo groupadd developers
sudo gpasswd -d kishore developers           # remove from a group
```

## SSH key login for the new user

```bash
sudo mkdir -p /home/kishore/.ssh
sudo tee /home/kishore/.ssh/authorized_keys <<< "ssh-ed25519 AAAA... kishore@laptop"
sudo chown -R kishore:kishore /home/kishore/.ssh
sudo chmod 700 /home/kishore/.ssh && sudo chmod 600 /home/kishore/.ssh/authorized_keys
```
