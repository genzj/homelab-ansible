# docker-prune

Runs `docker system prune` to reclaim disk space. By default removes stopped
containers, unused networks, dangling images and build cache older than
`prune_until`. Prints `docker system df` before and after.

| Item          | Value                                           |
|---------------|-------------------------------------------------|
| Playbook path | `playbooks/docker-prune/playbook.yml`           |
| Default hosts | `docker_hosts` (override with `target` / Limit) |
| Needs sudo    | no; `ansible` must be in the `docker` group     |
| Destructive   | **yes** – removed objects cannot be recovered   |
| Check mode    | supported (reports only, prunes nothing)        |

## Variables

| Name               | Type           | Required | Default        | Description |
|--------------------|----------------|----------|----------------|-------------|
| `target`           | string         | no       | `docker_hosts` | Host pattern / inventory group |
| `prune_all_images` | boolean        | no       | `false`        | Remove all unused images, not only dangling ones (`--all`) |
| `prune_volumes`    | boolean        | no       | `false`        | Remove unused volumes (`--volumes`). **Data loss risk.** Disables the `until` filter (docker limitation) |
| `prune_until`      | string         | no       | `24h`          | Only prune objects older than this; `""` disables the filter |

No required variables. Example extra vars:

```json
{"prune_all_images": true, "prune_until": "168h"}
```

## Survey variables

| Name               | Title                   | Type                  | Required | Default |
|--------------------|-------------------------|-----------------------|----------|---------|
| `prune_all_images` | Prune all unused images | Enum (`true`/`false`) | no       | `false` |
| `prune_volumes`    | Prune volumes (DANGER)  | Enum (`true`/`false`) | no       | `false` |
| `prune_until`      | Older than (e.g. `24h`) | String                | no       | `24h`   |

## Semaphore template

- Playbook filename: `playbooks/docker-prune/playbook.yml`
- Recommended: create two templates – one with `--check` in CLI args (dry run)
  and one real run. Keep `prune_volumes` off unless you mean it.
