# Semaphore-UI setup

One-time setup of a Semaphore project that uses this repo.

## 1. Key Store

| Key | Type | Used for |
|---|---|---|
| `ansible-ssh` | SSH Key | Private key of the `ansible` user on managed hosts |
| `git-deploy` *(if repo is private)* | SSH Key | Read-only deploy key for cloning this repo |
| `jumper-ssh` *(only if proxied)* | SSH Key | Key for the jump host, see [ssh-proxy.md](ssh-proxy.md) |

Use **None** for the git key if the repo is public over HTTPS.

## 2. Repository

- URL: this repo's clone URL
- Branch: `main`
- Access Key: `git-deploy` (or None)

Before each task, Semaphore installs `collections/requirements.yml` and
`roles/requirements.yml` (if present) automatically.

## 3. Inventory

Create a **Static YAML** inventory. Hosts and group names live only here.

- *User Credentials*: `ansible-ssh`
- *Sudo Credentials*: **None**. `ansible` has no sudo rights and playbooks never escalate.

Direct (runner is on the same network as the hosts):

```yaml
all:
  children:
    docker_hosts:
      hosts:
        docker1.example.lan:
```

Through a jump host: add `ansible_ssh_common_args` (all hosts or per group).
See [ssh-proxy.md](ssh-proxy.md).

```yaml
all:
  vars:
    ansible_ssh_common_args: >-
      -o ProxyCommand="ssh -W %h:%p -q -o StrictHostKeyChecking=accept-new proxy@jumper.example.com"
  children:
    docker_hosts:
      hosts:
        docker1.example.lan:
```

Groups used by playbooks in this repo:

| Group | Used by |
|---|---|
| `docker_hosts` | `docker-ps`, `docker-prune` |
| *(all)* | `healthcheck` |

## 4. Environment

Create an Environment (it can be empty). Useful environment variables:

```json
{ "ANSIBLE_HOST_KEY_CHECKING": "False" }
```

Only use this if you can't pre-populate `known_hosts` in the Semaphore
container. Prefer `-o StrictHostKeyChecking=accept-new` in the inventory,
which trusts a host on first use and still rejects changed keys.

## 5. Task Templates

Create one template per playbook folder. *Playbook Filename* is relative to the
repo root:

| Template | Playbook Filename | CLI args |
|---|---|---|
| Healthcheck | `playbooks/healthcheck/playbook.yml` | |
| Docker ps | `playbooks/docker-ps/playbook.yml` | |
| Docker prune (dry run) | `playbooks/docker-prune/playbook.yml` | `["--check"]` |
| Docker prune | `playbooks/docker-prune/playbook.yml` | |

Run **Docker ps** first: it validates the key, the proxy, and docker group access.
