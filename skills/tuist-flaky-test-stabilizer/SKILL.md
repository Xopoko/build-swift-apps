---
name: tuist-flaky-test-stabilizer
description: Investigate and fix flaky tests using Tuist test insights and local repeated test runs. Use when a user provides a flaky test URL, test case identifier, or asks to find and stabilize flaky tests.
---

# Tuist Flaky Test Stabilizer

Use this skill to move from flaky-test evidence to a small code or test fix.

## Inputs

Accept any of:

- Tuist test case URL or UUID
- `Module/Suite/testName` identifier
- request to discover flaky tests in the current project

## Discover Evidence

```bash
tuist test case list --flaky --json --page-size 50
tuist test case show <id-or-identifier> --json
tuist test case run list <module/suite/test> --flaky --json
tuist test case run show <run-id> --json
```

Collect:

- reliability/flakiness rate and sample size
- failure messages, source path, and line
- branch/CI clustering
- retry sequence if present
- crash report details if the test runner crashed

## Analyze The Test

Open the reported source line, then inspect setup, teardown, shared fixtures,
global state, async waits, mocked services, file system use, and clock/timezone
dependencies.

Common root causes:

- async assertion before work completes
- fixed sleeps instead of condition-based waits
- shared singleton or static state leaking between tests
- non-unique temp files, ports, identifiers, users, or database rows
- real network/service dependency
- order dependence exposed by parallel testing
- force unwrap/precondition crash hidden by retry

## Fix Rules

- Make the test deterministic at the smallest relevant boundary.
- Prefer dependency injection, explicit clocks, temp directories, mocks, and
  condition-based waits.
- Reset shared state in setup/teardown or remove the shared state dependency.
- Do not quarantine, skip, or weaken assertions unless the user explicitly asks.
- Avoid broad refactors while stabilizing one flaky test.

## Verify

Run the narrow test repeatedly:

```bash
xcodebuild test \
  -workspace <workspace> \
  -scheme <scheme> \
  -only-testing <module>/<suite>/<test> \
  -test-iterations 50 \
  -run-tests-until-failure
```

If the flake depends on parallelism, broaden the scope:

```bash
xcodebuild test \
  -workspace <workspace> \
  -scheme <scheme> \
  -only-testing <module> \
  -parallel-testing-enabled YES \
  -test-iterations 20 \
  -run-tests-until-failure
```

Use Thread Sanitizer when a data race is plausible and the project can run with
TSan enabled.

## Output

Report the root cause, fix, before/after evidence, exact verification command,
and any residual risk if the original flake could not be reproduced locally.
