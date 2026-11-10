# docker-container-restart

Restarts a container whatever state it's in. It then waits until the
container is running (and healthy, if it has a healthcheck) and checks that it
stays up, so a crash-looping container isn't reported as success.

| Current state          | Action                                   |
|------------------------|------------------------------------------|
| `running`, `restarting`| `docker restart --time <restart_stop_timeout>` |
| `paused`               | `docker unpause`, then `docker restart`  |
| `created`, `exited`    | `docker start`                           |
| `dead`, `removing`     | **fails**: Docker can't start these. Recreate the container (e.g. `docker compose up -d`) |

The task fails if:

- the container doesn't exist,
- it isn't running (and healthy) within `restart_wait_seconds`, or
- it restarts or stops during the following `restart_stable_seconds`
  (crash loop).

The error message shows the last status, health and restart count.

| Item          | Value                                                  |
|---------------|--------------------------------------------------------|
| Playbook path | `playbooks/docker-container-restart/playbook.yml`      |
| Default hosts | `docker_hosts` (use Limit / `target` to pick the host) |
| Needs sudo    | no; `ansible` must be in the `docker` group            |
| Destructive   | yes: interrupts the container's service                |
| Check mode    | supported (inspects and prints the planned action)     |

## Variables

| Name                      | Type    | Required | Default        | Description |
|---------------------------|---------|----------|----------------|-------------|
| `restart_container`       | string  | **yes**  | –              | Container name or ID |
| `target`                  | string  | no       | `docker_hosts` | Host pattern / inventory group |
| `restart_stop_timeout`    | integer | no       | `10`           | Seconds to wait for a graceful stop before `SIGKILL` |
| `restart_wait_seconds`    | integer | no       | `60`           | Max seconds to wait for running/healthy; `0` = don't wait or verify |
| `restart_require_healthy` | boolean | no       | `true`         | If the container has a healthcheck, also wait for `healthy` |
| `restart_stable_seconds`  | integer | no       | `5`            | After it comes up, it must stay running without restarting this long; `0` = skip |

Example extra vars:

```json
{"restart_container": "web"}
```

```json
{"restart_container": "web", "restart_stop_timeout": 30, "restart_wait_seconds": 120}
```

## Survey variables

| Name                      | Title                        | Type                  | Required | Default |
|---------------------------|------------------------------|-----------------------|----------|---------|
| `restart_container`       | Container name or ID         | String                | yes      |         |
| `restart_stop_timeout`    | Stop timeout (seconds)       | Integer               | no       | `10`    |
| `restart_wait_seconds`    | Wait for up (seconds)        | Integer               | no       | `60`    |
| `restart_require_healthy` | Wait for healthy             | Enum (`true`/`false`) | no       | `true`  |
| `restart_stable_seconds`  | Stable for (seconds)         | Integer               | no       | `5`     |

## Semaphore template

- Playbook filename: `playbooks/docker-container-restart/playbook.yml`
- Survey variables: as listed above
- Set **Limit** to the host running the container. Otherwise every host in
  `docker_hosts` is tried, and hosts without the container fail.
- Optional dry-run template with `["--check"]` as CLI args.
