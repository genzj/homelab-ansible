# healthcheck

Read-only report per host: connectivity, OS, uptime/load, disk and memory
usage, plus a warning for mounts above `disk_warn_percent`.

| Item          | Value                                   |
|---------------|-----------------------------------------|
| Playbook path | `playbooks/healthcheck/playbook.yml`    |
| Default hosts | `all` (override with `target` / Limit)  |
| Needs sudo    | no                                      |
| Destructive   | no                                      |
| Check mode    | supported                               |

## Variables

| Name                | Type           | Required | Default | Description                         |
|---------------------|----------------|----------|---------|-------------------------------------|
| `target`            | string         | no       | `all`   | Host pattern / inventory group      |
| `disk_warn_percent` | integer        | no       | `85`    | Usage % at which a mount is flagged |

No required variables. Example extra vars:

```json
{"target": "docker_hosts", "disk_warn_percent": 90}
```

## Survey variables

| Name                | Title                | Type    | Required | Default |
|---------------------|----------------------|---------|----------|---------|
| `disk_warn_percent` | Disk warn threshold % | Integer | no       | `85`    |

## Semaphore template

- Playbook filename: `playbooks/healthcheck/playbook.yml`
- Good candidate for a scheduled (cron) task.
