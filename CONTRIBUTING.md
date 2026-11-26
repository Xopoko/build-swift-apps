# Contributing

Contributions are welcome for reusable Swift and Apple-platform development
workflows.

## Open an issue or pull request

- Use the [issue templates](https://github.com/Xopoko/build-swift-apps/issues/new/choose)
  for a reproducible bug or a proposed workflow. Report vulnerabilities
  through the [private reporting process](SECURITY.md).
- For a pull request, include the affected skill or script, the host and agent
  you tested, and the results. Use a small, standalone sample project where
  possible. Remove credentials, personal paths, and company details from
  examples, logs, and screenshots before sharing them.

## Run the checks

Run the package validator and tests from the repository root on macOS or Linux
(including WSL).

```bash
./scripts/validate-package.sh
python3 -m unittest discover -s scripts/tests
for test in scripts/tests/test-*.sh; do bash "$test" || exit 1; done
```

On a Mac with Xcode, check the required tools for Apple and MCP workflows.

```bash
./scripts/doctor.sh --profile core --profile mcp --strict
```

Windows can run the portable Python tests with
`python -m unittest discover -s scripts/tests`.

## Change a skill

Keep each skill focused on one job. Link to shared material in
[`shared/`](shared/) and keep examples reusable. When adding, renaming, or removing
a skill, update the catalog and affected agent manifests together. For a new
required tool, update the installation guide, doctor, and dependency installer.

See [AGENTS.md](AGENTS.md) for the repository layout and packaging details.
