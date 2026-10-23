# Maintainer setup

Repository: https://github.com/kstrycharz/tari-agent-registry

## Repository controls

Set default branch main. Enable Issues, private vulnerability reporting,
Dependabot alerts, dependency graph and secret scanning/push protection where
available. Use GitHub-hosted runners and default read-only workflow permissions.
Keep Actions restricted to approved SHA-pinned actions. Do not add production
website deployment credentials to PR workflows.

Protect main with a ruleset / branch protection requiring:

- A pull request and one approving review, required code-owner review,
  dismissal of stale reviews, and resolution of review conversations.
- Required checks `Registry and security` and `review`, with branches up to date.
- No force pushes or branch deletion; apply rules to administrators too.
- No bypass for routine contributions. Enable an emergency bypass only through
  an explicit maintainer procedure with a recorded security reason.

The owner cannot approve their own PR when approval is required. Add another
trusted reviewer before accepting maintainer PRs under enforced protection;
do not weaken external-contribution review to work around that limitation.
CODEOWNERS covers every file, including workflows and validator changes. Policy
changes use the base validator on that PR; the new validator takes effect after
review and merge. Ensure it is tested in an isolated maintainer environment.

## Pages

Enable Settings → Pages → Source → GitHub Actions. The `Publish registry`
workflow scans, tests, packages and deploys main. Configure github-pages
environment deployment branch policy to main. For larger teams add required
deployment reviewers. A skipped or failed scan prevents publication.
GitHub's first Pages deployment can take a few minutes. Verify catalog and ZIP
checksums over HTTPS and test cross-origin access from the actual website.

## Dependencies

requirements-ci.lock pins tooling and all transitive dependencies with PyPI hashes
for cross-platform installation. requirements.txt declares the runtime validator
dependency. When Dependabot proposes an update, refresh the resolved wheel set
in a fresh .deps directory and run tools/lock_dependencies.py; review lock diffs,
run tests and install with --require-hashes. Do not merge mismatched pins and lock.

## Verification

```sh
python -m pip install --require-hashes -r requirements-ci.lock
python -I registry/core.py validate
python -I -m unittest discover -s tests -v
python -I -m bandit -r registry packages --ignore-nosec
node --test integrations/taritracker/registry.test.mjs
python -I registry/core.py build --revision local
```

Use Python from your virtual environment for isolated mode. On Windows an
unactivated user-site Python may not see jsonschema under -I. Antivirus runs on
Linux CI; local validation alone does not claim that ClamAV ran.

Open a trial PR to prove required checks run, modify a harmless entry without a
version increase to confirm failure, then bump it to confirm recovery. Do not
merge malicious test payloads. Review the code-owner gate and Pages environment
before advertising public contribution support.
