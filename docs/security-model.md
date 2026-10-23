# Security model

## Trust boundaries

Contributed files are untrusted data until reviewed and merged. PR validation
uses tooling, schema and tests from the PR **base commit**, with the candidate
tree checked out separately. It does not import candidate modules, install its
dependencies, run its tests or launch an MCP. Python isolated mode prevents the
candidate working directory from shadowing trusted tooling or dependencies.
Git checkout does not persist credentials. Jobs have read-only repository access,
no repository secrets, timeouts and SHA-pinned Actions. Never switch this to
`pull_request_target` while checking out PR code.

Repository workflow changes still require human protection: configure the rules
in setup.md before accepting external PRs. A PR can edit its own workflow. The
base-tooling design alone cannot prevent a contributor removing workflow steps;
required code-owner approval, stale-review dismissal and protected main are
part of the security boundary. GitHub-hosted disposable runners are required.
Do not use a privileged self-hosted runner for public contributions.

## Checks

- Strict JSON Schema, duplicate-key rejection, explicit full file inventory,
  canonical identities and semantic versions; changes require version increases.
- Text-only allowlist, per-file/package limits, no dotfiles, symlinks, traversal,
  archives, binaries, hidden payloads or bidirectional control characters.
- Blocking indicators for common credentials, download-and-execute chains,
  encoded PowerShell, dynamic execution and some hostile prompt instructions.
  Matching secret values are never printed by the custom scanner.
- ClamAV scans the entire candidate tree after a successful signature update.
  Update failure or scan failure blocks the job. No contributed file is executed.
- Bandit statically examines candidate Python source. Findings are not waived
  by candidate configuration or inline suppression comments.
- GitHub dependency review checks added dependencies on public PRs. The initial
  MCP format forbids third-party dependencies; support for other runtimes must
  include lockfile, vulnerability and provenance policies before enabling it.

Only allowlisted files enter downloads. Entry permissions are declarations,
not a sandbox or a guarantee that code follows them. Review the source and match
actual behavior to permissions. High-risk permissions are computed by the
builder; contributors cannot label their own package low risk.

## Review requirements

Inspect every new source file and instruction. Look for obfuscation, misleading
URLs, credential collection, wallet access, unexpected subprocesses, network
destinations, shell hooks, data exfiltration and indirect prompt injection.
Check the license text matches its declared identifier, author ownership, official
references, meaningful functionality and network/API compatibility evidence.
For spending/signing tools require a second reviewer with relevant expertise,
explicit transaction previews and user approval, fee bounds and recovery tests.
The repository rules enforce one owner review; two-person high-risk review is a
manual policy until an additional reviewer and ruleset are configured.

Automated checks cannot prove absence of malware, identify every secret or
prompt injection, or audit an upstream URL. Passing CI means checks passed,
not "safe", "verified" or "official". Downloads carry no such badges.

## Publication

Only pushes to protected main produce the feed. The publish workflow validates,
scans and tests before deployment, builds deterministic archives, and publishes
catalog.json, SHA256SUMS and versioned downloads through GitHub Pages.
SHA-256 detects corruption against the catalog; it does not authenticate a
compromised catalog or compromised publisher. HTTPS, protected main and Pages
environment controls supply the initial publisher trust. Old version URLs are
not retained in Pages deployments; mirror releases to immutable object storage
if permanent historical downloads are required. Never overwrite a version with
changed content.

## Incident response

Use GitHub private vulnerability reporting. Do not paste credentials into issues.
Deprecate the affected package with a version bump, merge an emergency fix or
disable Pages, remove affected hosted files, rotate exposed credentials, and
publish a clear advisory. Downloaded copies cannot be revoked. Users should
check catalog status before installation and never grant tools wallet secrets.
