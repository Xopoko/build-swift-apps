---
name: appstore-workflow-runner
description: Define, validate, run, resume, and audit repo-local `.asc/workflow.json` automations with current `asc workflow`, including safe release/TestFlight flows and step outputs.
---

# App Store Workflow Runner

Use `asc workflow` for lane-style repo-local automation. Workflows run trusted shell commands, stream step output to stderr, and keep stdout machine-readable JSON.

## Commands

Verify flags first:

```bash
asc workflow --help
asc workflow validate --help
asc workflow list --help
asc workflow run --help
```

Run flow:

```bash
asc workflow validate
asc workflow list
asc workflow list --all
asc workflow run --dry-run beta BUILD_ID:123 GROUP_ID:abc
asc workflow run beta BUILD_ID:123 GROUP_ID:abc
asc workflow run release --resume "release-20260312T120000Z-deadbeef"
```

Do not pass new `KEY:VALUE` params with `--resume`; saved workflow, params, and outputs are reused.

## File Contract

- Default: `.asc/workflow.json`; override with `--file`.
- JSONC comments supported.
- Top-level hooks: `before_all`, `after_all`, `error`.
- Workflow keys: `description`, `private`, `env`, `steps`.
- Step forms: string shorthand, `run`, `workflow`, `name`, `if`, `with`, `outputs`.
- Runtime params accept `KEY:VALUE` and `KEY=VALUE`; repeated keys are last-write-wins.
- Env precedence: `definition.env < workflow.env < CLI params`; for sub-workflows: `sub env < caller env/params < step with`.
- Conditional truthy values: `1`, `true`, `yes`, `y`, `on`.

Outputs:

- `run` steps that declare `outputs` must emit JSON stdout, have unique reference-safe `name`, and should call `asc ... --output json`.
- Reference as `${steps.step_name.OUTPUT_NAME}`.
- Do not map secrets into persisted outputs.

## Minimal Example

```json
{
  "env": { "APP_ID": "123", "VERSION": "1.0.0", "GROUP_ID": "" },
  "before_all": "asc auth status",
  "workflows": {
    "beta": {
      "description": "Resolve latest build and distribute to TestFlight",
      "steps": [
        {
          "name": "resolve_build",
          "run": "asc builds info --app $APP_ID --latest --platform IOS --output json",
          "outputs": { "BUILD_ID": "$.data.id" }
        },
        { "name": "groups", "run": "asc testflight groups list --app $APP_ID --limit 20 --output json" },
        { "name": "add", "if": "GROUP_ID", "run": "asc builds add-groups --build-id ${steps.resolve_build.BUILD_ID} --group $GROUP_ID" }
      ]
    },
    "release": {
      "steps": [
        { "name": "validate", "run": "asc validate --app $APP_ID --version $VERSION --platform IOS --output json" },
        { "name": "stage", "run": "asc release stage --app $APP_ID --version $VERSION --build $BUILD_ID --metadata-dir ./metadata/version/$VERSION --confirm --output json" },
        { "name": "submit", "if": "SUBMIT_FOR_REVIEW", "run": "asc review submit --app $APP_ID --version $VERSION --build $BUILD_ID --confirm --output json" }
      ]
    }
  }
}
```

## Agent Rules

- Keep workflows repo-local and reviewed; do not put secrets in workflow JSON or outputs.
- Prefer dry-run before mutating release/TestFlight flows.
- Use `private: true` for helper workflows not meant for direct listing.
- After failures, preserve run ID and resume only when the command indicates recovery is safe.
