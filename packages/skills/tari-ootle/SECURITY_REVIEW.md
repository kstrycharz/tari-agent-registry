# Pre-submission source review

Review date: 2026-10-23. Scope: the single installed Markdown skill and the four
declared payload files in this proposed registry entry. Only the package files
are submitted. No home-directory config, environment files, caches, wallet data
or unrelated installed skills are included.

## Credential and privacy checks

- Gitleaks 8.30.1 scanned the installed source locally with redacted output and
  reported no leaks. The official scanner release archive was checked against
  its published SHA-256 before use. Source content was not sent to a hosted scanner.
- Additional local patterns found no private-key blocks, JWT-shaped credentials,
  cloud/GitHub credentials, long hexadecimal/base64 key-like values, email
  addresses or absolute personal filesystem paths.
- Credential-related examples were inspected. `PrivateKeyProvider::random` and
  the test harness create keys at runtime; variable names such as `secret_key`
  do not contain stored key material. Address arguments use placeholders.
- External URL hosts were inventoried. A concrete public testnet indexer IP was
  removed rather than redistributing a deployment-specific endpoint. Remaining
  explicit URLs use official Tari/source/crate sites or local loopback examples.
- No credential removal was necessary because no embedded credential was found.

## Behavioral and packaging review

The payload is Markdown and license text, with no executable entrypoint,
dependencies, environment file or installation hook. The original source passed
the registry's suspicious-command and credential indicator checks. Commands in
the skill were reviewed as text; none were executed during this audit.

The instructions describe privileged development and wallet operations, so the
manifest declares conservative high-risk permissions and the skill adds an
explicit consent boundary. No transactions were signed, published or submitted.
No wallet was opened and no live endpoint was contacted as part of the skill audit.

## Limits

Pattern scans and source inspection cannot prove that every possible secret or
malicious instruction is absent. This is not an ABI, contract, fee or network
compatibility audit. Follow the normal protected PR checks and maintainer review
before merging or distributing an approved download. Passing automated checks
does not authorize transactions or certify the entry as safe.
