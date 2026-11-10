# docker-container-exec

Runs a command inside a running container with `docker exec` and prints its
output and exit code. The task fails if the command exits non-zero.

| Item          | Value                                                   |
|---------------|---------------------------------------------------------|
| Playbook path | `playbooks/docker-container-exec/playbook.yml`          |
| Default hosts | `docker_hosts` (use Limit / `target` to pick the host)  |
| Needs sudo    | no; `ansible` must be in the `docker` group             |
| Destructive   | **depends on the command**: it runs arbitrary commands  |
| Check mode    | supported (validates and prints the command, runs nothing) |

## Variables

| Name               | Type           | Required | Default | Description |
|--------------------|----------------|----------|---------|-------------|
| `exec_container`   | string         | **yes**  | –       | Container name or ID |
| `exec_command`     | string \| list | **yes**  | –       | Command to run. String or list (see below) |
| `target`           | string         | no       | `docker_hosts` | Host pattern / inventory group |
| `exec_interactive` | boolean        | no       | `false` | Add `--interactive` (keep STDIN open) |
| `exec_tty`         | boolean        | no       | `false` | Add `--tty` (allocate a pseudo-TTY) |
| `exec_use_shell`   | boolean        | no       | `false` | Run a string command as `<exec_shell> -c "<command>"` |
| `exec_shell`       | string         | no       | `sh`    | Shell inside the container, e.g. `bash` |
| `exec_user`        | string         | no       | `""`    | `--user` (name, UID or `uid:gid`); `""` = image default |
| `exec_workdir`     | string         | no       | `""`    | `--workdir`; `""` = image default |
| `exec_env`         | mapping        | no       | `{}`    | Extra env vars: mapping, or JSON string from a survey |
| `exec_changed`     | boolean        | no       | `true`  | Report the task as changed; set `false` for read-only commands |

How `exec_command` is run:

- **String, `exec_use_shell: false`** (default): split on whitespace and run
  directly, with no shell involved. Works on images without a shell
  (distroless, scratch). Quoting, pipes, `;`, redirects and `$VARS` aren't
  supported. Use a list if an argument contains spaces.
- **String, `exec_use_shell: true`**: runs as `<exec_shell> -c "<command>"`,
  so pipes, `;`, `&&`, redirects and `$VARS` work **inside the container**.
  The image must have that shell (`sh` by default).
- **List** (extra vars JSON): passed as exact arguments. `exec_use_shell` is
  ignored.

All values are shell-quoted on the docker host, so nothing in the command is
interpreted by the host's shell.

Example extra vars:

```json
{"exec_container": "web", "exec_command": "ls -la /data"}
```

```json
{"exec_container": "web", "exec_command": "ls -la /data | head", "exec_use_shell": true}
```

```json
{"exec_container": "web", "exec_command": ["cat", "/etc/os-release"],
 "exec_user": "nobody", "exec_env": {"LANG": "C"}, "exec_changed": false}
```

## Survey variables

| Name               | Title                         | Type                  | Required | Default |
|--------------------|-------------------------------|-----------------------|----------|---------|
| `exec_container`   | Container name or ID          | String                | yes      |         |
| `exec_command`     | Command                       | String                | yes      |         |
| `exec_use_shell`   | Run via shell                 | Enum (`true`/`false`) | no       | `false` |
| `exec_interactive` | Interactive (`-i`)            | Enum (`true`/`false`) | no       | `false` |
| `exec_tty`         | TTY (`-t`)                    | Enum (`true`/`false`) | no       | `false` |
| `exec_user`        | User                          | String                | no       |         |
| `exec_workdir`     | Working directory             | String                | no       |         |
| `exec_env`         | Env vars (JSON object)        | String                | no       |         |
| `exec_changed`     | Report as changed             | Enum (`true`/`false`) | no       | `true`  |

## Semaphore template

- Playbook filename: `playbooks/docker-container-exec/playbook.yml`
- Survey variables: as listed above
- Set **Limit** to the host running the container. Otherwise every host in
  `docker_hosts` is tried, and hosts without the container fail.
- Commands and their output appear in the task log. Don't pass secrets in
  `exec_command` or `exec_env`.
