"""ansible-lint rule: forbid privilege escalation.

The `ansible` user on managed hosts has no sudo rights, so playbooks in this
repo must never escalate. See docs/adding-a-playbook.md.
"""

from __future__ import annotations

import re
from typing import TYPE_CHECKING, Any

from ansiblelint.rules import AnsibleLintRule

if TYPE_CHECKING:
    from ansiblelint.errors import MatchError
    from ansiblelint.file_utils import Lintable
    from ansiblelint.utils import Task

ESCALATION_KEYS = ("become_user", "become_method", "become_flags", "become_exe")
COMMAND_MODULES = {
    "command", "shell", "raw", "script",
    "ansible.builtin.command", "ansible.builtin.shell",
    "ansible.builtin.raw", "ansible.builtin.script",
}
SUDO_RE = re.compile(r"(^|[\s;&|(`])(sudo|su|doas|pkexec)(\s|$)")
FALSE_VALUES = (False, "false", "False", "no", "No", "0", 0)


def _violations(data: dict[str, Any]) -> list[str]:
    found = []
    if "become" in data and data["become"] not in FALSE_VALUES:
        found.append(f"become: {data['become']!r}")
    found.extend(key for key in ESCALATION_KEYS if key in data)
    return found


class NoBecomeRule(AnsibleLintRule):
    """Privilege escalation is not allowed."""

    id = "no-become"
    shortdesc = "Privilege escalation (become/sudo) is not allowed"
    description = (
        "The `ansible` user cannot sudo. Remove become/become_user/"
        "become_method and sudo/su calls; grant access via group membership."
    )
    severity = "VERY_HIGH"
    tags = ["homelab", "security"]
    version_changed = "1.0.0"

    def matchplay(self, file: Lintable, data: dict[str, Any]) -> list[MatchError]:
        found = _violations(data)
        if not found:
            return []
        return [
            self.create_matcherror(
                message=f"Play uses privilege escalation: {', '.join(found)}",
                lineno=data.get("__line__", 1),
                filename=file,
            ),
        ]

    def matchtask(self, task: Task, file: Lintable | None = None) -> bool | str:
        found = _violations(task.raw_task)
        if found:
            return f"Task uses privilege escalation: {', '.join(found)}"
        action = task["action"]
        if action.get("__ansible_module__") in COMMAND_MODULES:
            args = action.get("__ansible_arguments__") or []
            cmd = action.get("_raw_params") or action.get("cmd") or action.get("argv") or args
            text = " ".join(cmd) if isinstance(cmd, list) else str(cmd)
            if SUDO_RE.search(text):
                return "Task calls sudo/su in a command"
        return False
