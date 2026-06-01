# Contributing

Contributions are welcome when they keep the plugin focused on reusable
Swift and Apple-platform development workflows.

## Principles

- Keep every skill narrow, actionable, and evidence-oriented.
- Prefer references to `shared/` over duplicating long procedures.
- Keep examples generic; do not include private company names, project names,
  customer names, credentials, or internal URLs.
- Document every new required host tool in `docs/INSTALL.md`,
  `scripts/doctor.sh`, and `scripts/install-deps.sh`.
- Update all agent packaging surfaces when adding or removing skills.

## Before Opening A PR

```bash
./scripts/validate-package.sh
./scripts/doctor.sh --profile core --profile mcp
```

If your change touches Codex plugin metadata and you have the Codex plugin
validator available, also run it against the repository root:

```bash
validate_plugin.py "$PWD"
```

External contributors can still run `scripts/validate-package.sh` without a
Codex-specific validator checkout.

## Skill Changes

When adding, removing, or renaming a skill, update:

- `README.md`
- `AGENTS.md`
- `.cursor-plugin/plugin.json`
- `package.json`
- dependency documentation and scripts when new tools are required

Keep `SKILL.md` frontmatter concise and trigger-friendly. The description should
make it clear when an agent should load the skill.
