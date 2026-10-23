# Contributing Tari tools

Fork the repository, branch from main, add or update one entry, and open a PR.
Use Python 3.11+ locally; CI uses Python 3.13. No contributed code runs in PR checks.

```sh
python -m venv .venv
# Linux/macOS: source .venv/bin/activate
# Windows PowerShell: .\.venv\Scripts\Activate.ps1
python -m pip install --require-hashes -r requirements-ci.lock
python -m registry.scaffold skill my-tari-skill --maintainer YOUR_GITHUB_LOGIN
python -m registry.core validate
python -m unittest discover -s tests -v
```

Choose `agent`, `mcp` or `skill`. The scaffold supplies a starter manifest,
LICENSE and README. Replace the starter content with useful, original work;
update every manifest field, and document actual compatibility and verification.
New MCP scaffolds copy the reference server as an example; rename its server
identity, version and tools when implementing your own behavior.

## Package layout

```
packages/skills/my-tari-skill/
  manifest.json
  SKILL.md
  README.md
  LICENSE
packages/agents/my-agent/       # entrypoint AGENT.md
packages/mcps/my-mcp/           # entrypoint server.py
```

The JSON Schema is the source of truth. Unknown fields are rejected. IDs are
lowercase kebab-case, directories match ids, versions use MAJOR.MINOR.PATCH
(without prerelease suffixes), and all payload files must be explicitly declared.
The manifest is automatically included; do not list it in files.
Skills use simple frontmatter with exactly `name:` and a one-line `description:`
before `---`. Agent instructions use AGENT.md; adapt them to host-specific agent
formats yourself. No universal agent-runtime compatibility is implied.

Initially, MCP entries must be dependency-free Python stdio servers. Other text
source extensions may be included as reviewed examples/resources, but CI does
not build or run them. Bundled dependencies, archives, executables, symlinks,
dotfiles and installation hooks are not accepted. Each file is limited to 512 KiB,
each entry to 2 MiB and 100 files. Text must be UTF-8 without hidden controls.
Use MIT, Apache-2.0, BSD-3-Clause or ISC, and include the corresponding full license.

## Permissions and compatibility

Declare all necessary capabilities: network:read, filesystem:read/write,
process:execute, wallet:read/sign/spend. Network access requires explicit hostnames,
without schemes, ports or wildcards. These are review metadata, not enforcement;
the client/host is responsible for sandboxing and consent. Any write/process/sign/
spend permission yields high risk. Other permissions yield medium; none yields low.
Instruction-only agents and skills must use runtime instructions.

List Tari network scope, exact tested versions and dates in the README. Include
at least one official Tari reference. Do not submit unrelated tools, repackaged
malware, secrets, unauthorized material or claims that checks certify safety.

Changing any file or metadata in an existing entry requires a higher version.
Use status deprecated and a version bump to retire an entry. The feed hides
deprecated entries from default UI. Update security_notes with migration guidance.

Maintainers review every file and permission before merging. Passing CI is
necessary and insufficient for approval; see docs/security-model.md. Scanner
exceptions require a separately reviewed trusted-policy change and explanation.
Never obscure a finding just to make a check pass.
