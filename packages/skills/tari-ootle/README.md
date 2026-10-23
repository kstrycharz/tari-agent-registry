# Tari Ootle development skill

Detailed guidance for Tari Ootle Rust/WASM templates, resources, access rules,
cross-component calls, events, client transactions, wallet CLI workflows and
local engine tests. This contribution imports the contributor's installed
`tari-ootle` skill, with limited safety and portability edits. It is independent
community material, not an official Tari release.

## Installation

Download the reviewed versioned ZIP, verify its catalog SHA-256, extract it,
and inspect every file. Load `SKILL.md` into an assistant that supports skills or
use it as project instructions. The archive includes no scripts or executables.
Host tool permissions are configured separately; loading the text grants none.

## Permissions and network scope

The documented workflows can involve shell execution, reading/writing project
files, fetching official documentation and public Rust dependencies, and wallet
reads, signing and spending. The manifest conservatively declares those
capabilities, which yields **high declared risk**. This is not automatic consent
to use any of them. Require user authorization for the specific transaction,
effects, fee and network before following a signing, publishing or spend example.

Examples target localnet and Esmeralda testnet. No mainnet capability is claimed.
Loopback wallet/indexer addresses are illustrative local services; they contain
no credentials and are not contacted by this package. The manifest's host list
describes public documentation and toolchain sources. A user-selected wallet or
indexer endpoint requires separate host approval and current network verification.
The package does not provide a remote endpoint or a functioning wallet connection.

## Compatibility and verification

Imported examples mention `tari_template_lib` 0.31 and
`tari_template_test_tooling` 0.40. They have **not** been compiled, tested against
released ABI versions, or submitted on-chain for this contribution. Preserve
your project's proven pins and verify each example against the exact SDK,
network and current [official documentation](https://ootle.tari.com/).
Historical statements about fees, defaults and API behavior require rechecking.

The submission audit is recorded in [SECURITY_REVIEW.md](SECURITY_REVIEW.md).
It checks source text and packaging; it does not certify smart-contract correctness.

## Provenance and changes

The installed source was a single Markdown file with no bundled dependencies,
wallet/config files, attribution notice or separate license file. This submitted
package uses the registry's MIT license. Maintainers should review redistribution
rights and attribution as part of the normal contribution review.

Changes made for this submission:

- Shortened the frontmatter description for a portable registry entry.
- Added explicit consent, secret-handling and network/version boundaries.
- Removed a concrete public testnet indexer IP; consult official configuration instead.
- Reworded historical "current release" and automatic upgrade advice to avoid
  implying current compatibility.
- Added the manifest, license, installation notes and security-review record.

The contributor's installed copy was not modified.
