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

| Name            | Default        | Description                                        |
|-----------------|----------------|----------------------------------------------------|
| `target`        | `docker_hosts` | Host pattern / inventory group                     |
| `docker_ps_all` | `false`        | Include stopped containers                         |

## Semaphore template

- Playbook filename: `playbooks/docker-ps/playbook.yml`
- Extra variables (optional): `{"docker_ps_all": true}`
