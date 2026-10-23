# Tari Agent Registry

Community-contributed **agents, MCP servers and skills for Tari**, maintained by
TariTracker. Standard manifests, reviewable source, PR security checks and
versioned downloads for [taritracker.com](https://taritracker.com).

This is an independent community project, not an official Tari repository.
Passing automated checks is not a malware-free guarantee or a security audit.

## Use an entry

Download a ZIP from the [catalog](https://kstrycharz.github.io/tari-agent-registry/catalog.json),
verify its SHA-256 against the catalog, inspect its manifest, permissions and all
source files, then load it into your preferred host. See each README for details.
Do not give an unreviewed tool wallet credentials or signing authority.

| Kind | Starter | Behavior |
| --- | --- | --- |
| Skill | [tari-development](packages/skills/tari-development) | Source-based Tari development guidance |
| Agent | [tari-reviewer](packages/agents/tari-reviewer) | Portable Tari code-review instructions |
| MCP | [tari-reference](packages/mcps/tari-reference) | Working local stdio tool for official documentation links |

## Contribute

Read [CONTRIBUTING.md](CONTRIBUTING.md), scaffold an entry and open a PR.
Every package has a strict manifest, semantic version, license, explicit file
inventory, permission declarations, Tari references and compatibility notes.

```sh
python -m pip install --require-hashes -r requirements-ci.lock
python -m registry.scaffold skill my-tari-skill --maintainer YOUR_GITHUB_LOGIN
python -m registry.core validate
python -m unittest discover -s tests -v
python -m registry.core build --revision local
```

Use a virtual environment; see the contributor guide for Windows instructions.
Build output is dist/catalog.json, dist/SHA256SUMS and dist/downloads/*.zip.
Builds are deterministic for the same source, revision and Python/zlib toolchain.

## Review and publication

```
Fork → PR → base-policy validation + static checks + antivirus
        → owner review → protected main → scan + test + build → GitHub Pages
                                                             → TariTracker
```

PR tooling comes from the trusted base commit. Submitted code is scanned as data,
never installed or executed. ClamAV, Bandit, strict packaging rules and credential/
command indicators provide complementary checks. Dependency review checks new
dependency risks. See the [security model](docs/security-model.md) for limitations
and the required repository protection settings.

The distribution feed is static JSON and ZIPs; the website stays independent.
[TariTracker integration](docs/taritracker.md) includes a framework-neutral client
that displays permissions and verifies downloads. [Maintainer setup](docs/setup.md)
explains Pages, protection rules and private vulnerability reporting.

## Official reference material

- [Tari](https://tari.com/)
- [Tari Ootle documentation](https://ootle.tari.com/)
- [Tari source organization](https://github.com/tari-project)
- [MCP specification](https://modelcontextprotocol.io/specification/2025-11-25)
- [GitHub Actions secure-use reference](https://docs.github.com/en/actions/reference/security/secure-use)

Repository tooling and starters are MIT licensed. Each contributed entry declares
and bundles its own allowed license; contributors retain their copyrights.
