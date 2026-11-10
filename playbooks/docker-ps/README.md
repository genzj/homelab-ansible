# docker-ps

Smoke test for docker hosts: confirms SSH as `ansible` (including any proxy
hop) and access to the Docker engine, then prints `docker ps`. Use it first when
wiring up a new Semaphore inventory or SSH key.

| Item          | Value                                           |
|---------------|-------------------------------------------------|
| Playbook path | `playbooks/docker-ps/playbook.yml`              |
| Default hosts | `docker_hosts` (override with `target` / Limit) |
| Needs sudo    | no; `ansible` must be in the `docker` group     |
| Destructive   | no                                              |
| Check mode    | supported                                       |

## Variables

| Name            | Type           | Required | Default        | Description                    |
|-----------------|----------------|----------|----------------|--------------------------------|
| `target`        | string         | no       | `docker_hosts` | Host pattern / inventory group |
| `docker_ps_all` | boolean        | no       | `false`        | Include stopped containers     |

No required variables. Example extra vars:

```json
{"docker_ps_all": true}
```

## Survey variables

| Name            | Title                      | Type                  | Required | Default |
|-----------------|----------------------------|-----------------------|----------|---------|
| `docker_ps_all` | Include stopped containers | Enum (`true`/`false`) | no       | `false` |

## Semaphore template

- Playbook filename: `playbooks/docker-ps/playbook.yml`
- Survey variables: as listed above
