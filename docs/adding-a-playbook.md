# Adding a new playbook

## 1. Create the folder

```sh
cp -R playbooks/_template playbooks/<name>
```

Use a short kebab-case `<name>` that describes the operation, e.g.
`apt-upgrade` or `restart-container`. The folder must contain:

- `playbook.yml`: the entry point Semaphore runs.
- `README.md`: purpose, variables, Semaphore template settings. Fill in the
  table copied from the template.

Optional, per-playbook files stay inside the folder:

```
playbooks/<name>/
  playbook.yml
  README.md
  vars/defaults.yml     # loaded via vars_files: [vars/defaults.yml]
  templates/*.j2        # referenced relative to the playbook
  files/*
```

Logic shared by several playbooks belongs in a role under `roles/<role>/`
(`roles_path` already points there).

## 2. Follow the conventions

| Convention | Why |
|---|---|
| `hosts: "{{ target \| default('<group>') }}"` | Semaphore can retarget a template with the extra var `target` without editing code. Use inventory **group names** (e.g. `docker_hosts`), never hostnames. |
| Don't set `remote_user` in the playbook | It comes from `ansible.cfg` (`ansible`). |
| Know whether targets have Python | Regular modules (`command`, `copy`, `setup`, ...) need Python on the target. For Python-less hosts (e.g. Flatcar Container Linux), use `gather_facts: false` and `ansible.builtin.raw`, and add `check_mode: false` to read-only `raw` tasks. Controller-side modules (`debug`, `set_fact`) always work. See `playbooks/docker-ps`. |
| Prefer `ansible.builtin` modules | No extra Python libraries on targets. If you need a collection, add it to `collections/requirements.yml`. |
| `changed_when: false` on read-only commands | Keeps Semaphore's "changed" count accurate. |
| Parameters are variables, never hard-coded | Semaphore Survey Variables can supply them per run. See [Good practices](#good-practices-parameters-and-survey-variables). |
| Destructive steps: opt-in var **and** `when: not ansible_check_mode` | Safe defaults. `--check` works as a dry run. |
| **Never use `become`** | `ansible` cannot sudo. See [No privilege escalation](#no-privilege-escalation). |
| End with `ansible.builtin.debug` output | The Semaphore task log is the "report". |
| Fully-qualified module names (`ansible.builtin.command`) | Required by ansible-lint. |
| No hostnames, IPs, or secrets in the repo | Hosts belong in Semaphore inventories. Secrets belong in Semaphore Key Store / Variable Groups (secret). |

If a new playbook needs a new group (e.g. `proxmox_hosts`), document it in
the playbook README and in `inventory.example.yml`, then add it to the
Semaphore inventory.

## No privilege escalation

The `ansible` user is unprivileged and **cannot run sudo**. Playbooks in this
repo must not escalate privileges:

- No `become: true`, `become_user`, or `become_method` on plays, blocks,
  tasks, or roles. Don't call `sudo`/`su` inside `command`, `shell`, or `raw`.
- Don't pass `--become`/`-b`, and don't set *Sudo Credentials* in Semaphore.
- If an operation needs elevated access, grant it on the host through group
  membership or file permissions (e.g. `docker` group for the Docker socket,
  `systemd-journal` for logs). Do that outside this repo. If root really is
  unavoidable, it doesn't belong in this repo.

Enforcement:

- `ansible.cfg` sets `become = False`.
- `lint-rules/no_become.py` is a custom ansible-lint rule (`no-become`). It
  fails on any truthy `become`, on `become_user`/`become_method`, and on
  `sudo`/`su` in command-like tasks. Run `ansible-lint` before pushing.

## Good practices: parameters and Survey Variables

Every value an operator might change between runs is a **variable**. Don't
hard-code it in tasks. Semaphore can then ask for it with **Survey
Variables** when the task starts, and one template covers many runs.

### Declare every parameter

- **Optional parameters** get a default in the play's `vars:` block, with a
  short comment:

  ```yaml
  vars:
    prune_until: 24h        # only prune objects older than this
    prune_volumes: false    # opt-in: DATA LOSS RISK
  ```

- **Required parameters** have no sensible default. Don't define them in
  `vars:`. Validate them in the first task so a missing value fails fast with
  a clear message:

  ```yaml
  tasks:
    - name: Validate parameters
      ansible.builtin.assert:
        that:
          - container_name is defined
          - container_name | string | length > 0
        fail_msg: >-
          container_name is required (name of the container to restart).
          Example: {"container_name": "web"}
        quiet: true
  ```

  `assert` runs on the controller, so it also works for Python-less hosts.

- Keep names `snake_case` and prefixed by the playbook topic
  (`prune_*`, `docker_ps_*`). Survey variables are passed as extra vars and
  override everything else, so generic names like `name` or `path` can clash
  with inventory variables.
- `target` (the host pattern) is the only shared parameter name. Every
  playbook supports it.

### Make values survey-friendly

Semaphore passes survey values as extra vars, often as **strings**:

- Always cast: `flag | bool`, `count | int`. Never test a raw value with
  `when: flag`, because the string `"false"` is truthy.
- Booleans: use an **Enum** survey var with values `true` / `false`, and set the
  survey default to the playbook default.
- An empty optional survey field may arrive as `""` and **override** the
  `vars:` default. Either set the same default in the survey, or give `""`
  a defined meaning and document it. For example, `docker-prune` treats an
  empty `prune_until` as "no age filter".
- Validate allowed values for enums and formats with `assert`. Don't rely
  on the survey alone, since the playbook can also run without it.
- Secrets (tokens, passwords): use the **Secret** survey type or a secret
  Variable Group. Add `no_log: true` to tasks that use them. Never put them in
  defaults.
- Destructive switches default to the safe value (`false`). The survey
  should default to safe too.

### Document parameters in the playbook folder

Each playbook's `README.md` must list **all** parameters, with an
example for every required one:

```markdown
## Variables

| Name             | Required | Default | Description                     |
|------------------|----------|---------|---------------------------------|
| `target`         | no       | `all`   | Host pattern / inventory group  |
| `container_name` | **yes**  | –       | Container to restart            |
| `restart_wait`   | no       | `10`    | Seconds to wait after restart   |

Example extra vars:

    {"container_name": "web", "restart_wait": 30}

## Survey variables

| Name             | Title             | Type    | Required | Default |
|------------------|-------------------|---------|----------|---------|
| `container_name` | Container name    | String  | yes      |         |
| `restart_wait`   | Wait (seconds)    | Integer | no       | `10`    |
```

The playbook header comment lists the required variables too, so they're
visible to anyone reading the YAML. `playbooks/_template` has this structure
ready to fill in.

## 3. Test locally

```sh
uvx --from ansible-core ansible-playbook -i local/inventory.yml playbooks/<name>/playbook.yml --syntax-check
uvx --from ansible-core ansible-playbook -i local/inventory.yml playbooks/<name>/playbook.yml --check --diff
uvx --from ansible-core ansible-playbook -i local/inventory.yml playbooks/<name>/playbook.yml
uvx yamllint . && uvx --from ansible-lint ansible-lint
```

`local/` is git-ignored. See the README for its format.

## 4. Register it in Semaphore

1. Commit and push. Semaphore pulls the branch configured on its Repository.
2. **Task Templates → New Template**:
   - *Playbook Filename*: `playbooks/<name>/playbook.yml`
   - *Inventory*: one containing the target group
   - *Repository*, *Environment*: the project defaults
   - *Survey Variables*: add the entries from the playbook README's
     "Survey variables" table (see
     [Good practices](#good-practices-parameters-and-survey-variables))
   - Optionally add a second "dry run" template with `["--check"]` as CLI args
3. Run it once with the dry-run template, then for real.

See [semaphore-setup.md](semaphore-setup.md) for the one-time project setup.
