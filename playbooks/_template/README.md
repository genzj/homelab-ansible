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

| Name            | Type           | Required | Default | Description                    |
|-----------------|----------------|----------|---------|--------------------------------|
| `target`        | string         | no       | `all`   | Host pattern / inventory group |
| `example_name`  | string         | **yes**  | –       | <what it is>                   |
| `example_count` | integer        | no       | `3`     | <what it is>                   |
| `example_flag`  | boolean        | no       | `false` | Enables the destructive step   |

Example extra vars:

```json
{"example_name": "web", "example_count": 5}
```

## Survey variables

| Name            | Title           | Type                  | Required | Default |
|-----------------|-----------------|-----------------------|----------|---------|
| `example_name`  | Example name    | String                | yes      |         |
| `example_count` | Example count   | Integer               | no       | `3`     |
| `example_flag`  | Run destructive | Enum (`true`/`false`) | no       | `false` |

## Semaphore template

- Playbook filename: `playbooks/<playbook-name>/playbook.yml`
- Inventory: any inventory that contains the target group
- Survey variables: as listed above
