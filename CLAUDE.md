# Claude Code Notes

For repository maintenance, read `AGENTS.md` first. It is the canonical
cross-agent instruction file for this project.

For plugin runtime behavior, Claude Code uses `.claude-plugin/plugin.json` and
the skill directories under `skills/`. Do not put skills, commands, agents, or
hooks inside `.claude-plugin/`; that directory is for manifests only.
