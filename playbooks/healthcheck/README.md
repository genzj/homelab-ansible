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

| Name                | Default | Description                       |
|---------------------|---------|-----------------------------------|
| `target`            | `all`   | Host pattern / inventory group    |
| `disk_warn_percent` | `85`    | Usage % at which a mount is flagged |

## Semaphore template

- Playbook filename: `playbooks/healthcheck/playbook.yml`
- Good candidate for a scheduled (cron) task.
