# homelab-ansible

Ansible playbooks for homelab operations, run from
[Semaphore-UI](https://semaphoreui.com/). Semaphore clones this repo. Each
operation is a separate folder under `playbooks/`, and inventories are managed
in Semaphore, not here.

## Layout

```
ansible.cfg                  # repo-wide settings (remote_user=ansible, no inventory)
collections/requirements.yml # collections; Semaphore installs these automatically
roles/                       # shared roles (optional)
lint-rules/                  # custom ansible-lint rules (no-become)
inventory.example.yml        # example inventory shape (placeholder hosts only)
playbooks/
  _template/                 # copy this to create a new playbook
  healthcheck/               # read-only host report
  docker-ps/                 # smoke test: SSH + docker access + docker ps
  docker-prune/              # docker system prune (opt-in flags)
  docker-container-exec/     # docker exec a command in a container
  docker-container-restart/  # restart a container from any state
docs/
  adding-a-playbook.md
  semaphore-setup.md
  ssh-proxy.md
local/                       # git-ignored: your test inventories, real hostnames
```

## Prerequisites on managed hosts

- A user named `ansible` that accepts the Semaphore/runner SSH key.
- **No sudo.** `ansible` is an unprivileged user and cannot run sudo.
  Playbooks never use `become` (enforced by config and lint, see
  [adding-a-playbook.md](docs/adding-a-playbook.md#no-privilege-escalation)).
  Grant access via group membership instead.
- For docker playbooks: `ansible` in the `docker` group.
- Python is **not** required by the bundled playbooks. They use
  `ansible.builtin.raw`, so they also work on Python-less hosts such as Flatcar
  Container Linux. Playbooks that use regular modules need Python 3 on the
  target.

## Run locally

Real hostnames go in a **git-ignored** `local/` inventory only:

```yaml
# local/inventory.yml
all:
  children:
    docker_hosts:
      hosts:
        docker1.example.lan:
          # ansible_ssh_private_key_file: ~/.ssh/<ansible-user-key>
```

```sh
# no global install needed
uvx --from ansible-core ansible-playbook -i local/inventory.yml playbooks/docker-ps/playbook.yml
uvx --from ansible-core ansible-playbook -i local/inventory.yml playbooks/docker-prune/playbook.yml --check
```

Ansible uses the system OpenSSH client, so any `ProxyCommand`/`ProxyJump` in
your `~/.ssh/config` is used as-is. `remote_user = ansible` in `ansible.cfg`
overrides any `User` set there. See [docs/ssh-proxy.md](docs/ssh-proxy.md).

A `bash: warning: setlocale: LC_ALL ...` line in output is harmless. It comes
from macOS forwarding `LC_*` over SSH to a host without that locale.

## Security and privacy

This repo is **public**. Every commit, including commit messages, branch
names, and PR text, must be safe to publish. Git history is permanent:
deleting a file later doesn't remove it from history or from forks.

**Never commit:**

- **Concrete domain names or hostnames.** No real domains, subdomains, FQDNs,
  or tunnel/proxy endpoints. Use reserved placeholders: `example.com`,
  `example.lan`, `host1.example.lan`, `jumper.example.com`.
- **Concrete usernames.** Only generic names are allowed: `ansible`, `user`,
  `root`, `proxy`, `admin`. No personal accounts, GitHub handles, or emails,
  except in git author metadata.
- **Real network topology.** No real IP addresses or subnets, VLAN IDs, port
  mappings, which service runs on which host, jump host chains, or
  hypervisor/VM layout. Use the documentation ranges `192.0.2.0/24`,
  `198.51.100.0/24`, or `203.0.113.0/24` for example IPs.
- **Secrets.** SSH keys, tokens, passwords, Cloudflare service tokens, vault
  passwords. Keep them in the Semaphore Key Store or secret Variable Groups.
- **Inventories, and output captured from real runs.** Pasted logs leak
  hostnames, container names, and paths.

**Where real values go instead:**

| Kind | Location |
|---|---|
| Hosts, groups, per-host vars | Semaphore inventory |
| Keys, tokens, passwords | Semaphore Key Store / secret Variable Groups |
| Per-run parameters | Semaphore Survey Variables |
| Local testing | `local/` (git-ignored) |

**Check before every commit.** Keep your own denylist of real names (domains,
usernames, IPs, subnets) in the git-ignored `local/denylist.txt`, one
pattern per line. Then run:

```sh
# staged changes (also re-read your commit message)
git diff --cached | grep -n -i -f local/denylist.txt && echo "LEAK: fix before committing"
# whole tree (tracked files)
git grep -n -i -f local/denylist.txt
```

If something leaks into a commit that's already pushed, treat it as
disclosed. Rotate any secret, then rewrite history (`git filter-repo`) and
force-push. Removing it in a new commit isn't enough.

## Lint

```sh
uvx yamllint .
uvx --from ansible-lint ansible-lint
```

## More

- [Adding a new playbook](docs/adding-a-playbook.md)
- [Semaphore-UI setup](docs/semaphore-setup.md)
- [SSH through a proxy / jump host](docs/ssh-proxy.md)

> Never commit real hostnames, usernames, IPs or network layout. See
> [Security and privacy](#security-and-privacy).
