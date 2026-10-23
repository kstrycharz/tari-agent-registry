# Tari Reference MCP

A working, dependency-free Python MCP stdio server returning curated official
Tari documentation links. It does not retrieve pages or query live chain data.
Community maintained; not an official Tari product.

## Install

Extract the archive and inspect all files. Configure a compatible MCP client:

```json
{
  "mcpServers": {
    "tari-reference": {
      "command": "python3",
      "args": ["/absolute/path/to/tari-reference/server.py"]
    }
  }
}
```

Use `python` on Windows where appropriate and replace the path. Python 3.11+.
No packages, API keys, environment variables, wallet or network access required.
Supports stdio protocol negotiation for 2025-11-25, 2025-06-18 and 2024-11-05.

## Tools

`tari_reference` accepts `{"topic":"tari"}`, `{"topic":"ootle"}` or
`{"topic":"source"}`. The result contains title, URL and scope. Links were
checked on 2026-10-23; the server makes no claim about live content or API versions.

## Verification

Maintainer tests exercise initialize, tools/list, tools/call, ping, invalid input
and the actual newline-delimited subprocess transport. Untrusted PR checks do
not execute this server. Run only after inspecting the extracted source.
