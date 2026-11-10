# SSH through a proxy / jump host

Ansible connects with the system OpenSSH client. Anything that works with
plain `ssh ansible@host` works for Ansible too. Pick the option that matches
where the runner (your laptop or Semaphore) sits.

## Option A: direct (runner inside the LAN)

Nothing to configure. Semaphore on the same network as the hosts connects
directly.

## Option B: local runs from a laptop (`~/.ssh/config`)

If your `~/.ssh/config` already has a `ProxyCommand`/`ProxyJump` for the
hosts, Ansible uses it. For example:

```sshconfig
Host jumper.example.com
    User proxy
    ProxyCommand cloudflared access ssh --hostname %h

Host *.example.lan 192.0.2.*
    ProxyJump jumper.example.com
```

`remote_user = ansible` in `ansible.cfg` is passed as `-o User=ansible`. That
takes precedence over any `User` line in `~/.ssh/config`, so the target hop
uses `ansible` while the jump hop keeps its own user.

## Option C: Semaphore outside the LAN (inventory vars)

The Semaphore container has no `~/.ssh/config`, so define the hop in the
inventory with `ansible_ssh_common_args`:

```yaml
all:
  vars:
    # Plain SSH jump host
    ansible_ssh_common_args: >-
      -o ProxyCommand="ssh -W %h:%p -q -o StrictHostKeyChecking=accept-new proxy@jumper.example.com"
```

If the jump host itself sits behind Cloudflare Access, nest the
`cloudflared` hop:

```yaml
all:
  vars:
    ansible_ssh_common_args: >-
      -o ProxyCommand="ssh -W %h:%p -q
      -o StrictHostKeyChecking=accept-new
      -o ProxyCommand='cloudflared access ssh --hostname %%h'
      proxy@jumper.example.com"
```

Requirements for option C:

- **Jump-host key.** The jump hop uses the same key Semaphore loads for the
  inventory (the `ansible` key), unless the container's ssh-agent or
  `~/.ssh` provides another one. Simplest setup: authorize the `ansible`
  public key for the `proxy` user on the jump host.
- **cloudflared** (only for the Cloudflare variant). It must be installed in
  the Semaphore container (custom image or mounted binary). It also needs
  non-interactive auth with a Cloudflare Access **service token**: set
  `TUNNEL_SERVICE_TOKEN_ID` / `TUNNEL_SERVICE_TOKEN_SECRET` as secret
  environment variables in Semaphore. `cloudflared access ssh` reads them,
  which is equivalent to `--service-token-id` / `--service-token-secret`.
- **Scope.** Set the vars per group instead of `all` if only some hosts need
  the hop.

## Troubleshooting

```sh
# What ssh command does Ansible build?
ansible-playbook ... -vvvv

# Test the raw hop outside Ansible
ssh -o User=ansible <host> 'id && docker ps'
```
