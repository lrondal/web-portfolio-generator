#!/usr/bin/env python3
"""PreToolUse hook: blocks the git operations CLAUDE.md's "Git workflow"
section forbids agents from doing:
  - committing directly to main
  - pushing main
  - force-pushing (any branch)
  - merging (agents open PRs; humans merge)

Deliberately narrower than a "block every git push" hook: agents still
need to push feature branches to open PRs, so only main/force pushes
are blocked. Adapted from the vendored
.agents/skills/git-guardrails-claude-code skill, customized to this
project's actual rule instead of its generic blocklist.

Tokenizes the command with shlex instead of grepping the raw string.
A first version matched on substrings and blocked a legitimate commit
because its *commit message* happened to contain the words "git push"
and "main" -- raw substring matching can't tell code from a quoted
argument. shlex.split collapses a quoted "-m '...'" message into a
single token, so its contents can never equal a bare token like
"main" or "push" and trip the checks below.

Input: JSON on stdin, {"tool_input": {"command": "..."}, ...}
Exit 0 = allow. Exit 2 = block (stderr message is shown to the agent).
"""
import json
import shlex
import subprocess
import sys


def current_branch() -> str | None:
    try:
        out = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            capture_output=True, text=True, timeout=5,
        )
        return out.stdout.strip() if out.returncode == 0 else None
    except Exception:
        return None


def block(command: str, reason: str) -> None:
    sys.stderr.write(
        f"BLOCKED: '{command}' -- {reason}. See CLAUDE.md 'Git workflow': "
        "agents branch off main, never commit/push/merge to main, "
        "never force-push.\n"
    )
    sys.exit(2)


def main() -> None:
    try:
        payload = json.load(sys.stdin)
        command = payload.get("tool_input", {}).get("command", "")
    except Exception:
        return  # can't parse -> allow, don't crash every Bash call

    if not command:
        return

    try:
        tokens = shlex.split(command, posix=True)
    except ValueError:
        return  # unbalanced quotes etc. -- allow rather than guess

    branch = current_branch()

    # Walk the token stream looking for each `git <subcommand>` invocation
    # (there can be more than one, chained with && / ; / |).
    for i, tok in enumerate(tokens):
        if tok != "git":
            continue
        # skip git's own leading flags (e.g. `git -C path commit`)
        j = i + 1
        while j < len(tokens) and tokens[j].startswith("-"):
            j += 1
        if j >= len(tokens):
            continue
        subcmd = tokens[j]
        rest = tokens[j + 1:]

        if subcmd == "commit" and branch == "main":
            block(command, "committing directly to main is not allowed")

        if subcmd == "push":
            if any(t in ("-f", "--force", "--force-with-lease") for t in rest):
                block(command, "force-pushing is never allowed")
            # explicit ref args, e.g. `git push origin main`
            refs = [t for t in rest if not t.startswith("-")]
            if "main" in refs:
                block(command, "pushing main is not allowed")
            # bare `git push` (no ref given) while sitting on main
            if not refs and branch == "main":
                block(command, "current branch is main; pushing it is not allowed")

        if subcmd == "merge":
            block(command, "agents must not merge; open a pull request instead")


if __name__ == "__main__":
    main()
