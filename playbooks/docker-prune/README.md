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

| Name               | Default        | Description |
|--------------------|----------------|-------------|
| `target`           | `docker_hosts` | Host pattern / inventory group |
| `prune_all_images` | `false`        | Remove all unused images, not only dangling ones (`--all`) |
| `prune_volumes`    | `false`        | Remove unused volumes (`--volumes`). **Data loss risk.** Disables the `until` filter (docker limitation) |
| `prune_until`      | `24h`          | Only prune objects older than this; `""` disables the filter |

## Semaphore template

- Playbook filename: `playbooks/docker-prune/playbook.yml`
- Recommended: create two templates – one with `--check` in CLI args (dry run)
  and one real run. Keep `prune_volumes` off unless you mean it.
