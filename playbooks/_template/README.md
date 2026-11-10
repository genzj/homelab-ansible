# <playbook-name>

<What it does, in one or two sentences.>

| Item          | Value                                        |
|---------------|----------------------------------------------|
| Playbook path | `playbooks/<playbook-name>/playbook.yml`     |
| Default hosts | `all` (override with `target` / Limit)       |
| Needs sudo    | no (sudo is never allowed)                   |
| Destructive   | no                                           |
| Check mode    | supported                                    |

## Variables

| Name           | Default | Description                    |
|----------------|---------|--------------------------------|
| `target`       | `all`   | Host pattern / inventory group |
| `example_flag` | `false` | Enables the destructive step   |

## Semaphore template

- Playbook filename: `playbooks/<playbook-name>/playbook.yml`
- Inventory: any inventory that contains the target group
- Extra variables (optional): `{"target": "docker_hosts"}`
