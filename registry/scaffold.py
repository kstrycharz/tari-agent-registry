"""Generate a portable, dependency-free contribution starter."""
import argparse
import json
from pathlib import Path

from registry.core import ROOT, KINDS, SLUG


def create(root, kind, slug, maintainer):
    if kind not in KINDS.values() or not SLUG.fullmatch(slug):
        raise ValueError("Choose agent/mcp/skill and a lowercase kebab-case id")
    group = next(k for k, v in KINDS.items() if v == kind)
    folder = root / "packages" / group / slug
    if folder.exists():
        raise ValueError("Package already exists")
    entry = {"agent": "AGENT.md", "mcp": "server.py", "skill": "SKILL.md"}[kind]
    title = slug.replace("-", " ").title()
    manifest = {
        "schema_version": 1, "kind": kind, "id": slug, "name": title,
        "description": f"Community Tari {kind}: {title}.", "version": "1.0.0",
        "license": "MIT", "maintainers": [maintainer], "entrypoint": entry,
        "files": ["README.md", "LICENSE", entry], "permissions": [],
        "network_hosts": [], "networks": ["none"], "tags": ["tari", kind],
        "tari_references": ["https://tari.com/", "https://ootle.tari.com/"],
        "compatibility": "Python 3.11+; dependency-free MCP stdio." if kind == "mcp" else "Portable Markdown instructions; configure host tools independently.",
        "security_notes": "No credentials or automatic transactions. Review all files and host permissions before use.",
        "runtime": "python3" if kind == "mcp" else "instructions", "status": "active"
    }
    folder.mkdir(parents=True)
    (folder / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8", newline="\n")
    (folder / "LICENSE").write_bytes((ROOT / "LICENSE").read_bytes())
    (folder / "README.md").write_text(f"# {title}\n\nDescribe purpose, installation, permission boundaries, compatibility and verification.\n\nCommunity maintained; not an official Tari product.\n", encoding="utf-8", newline="\n")
    if kind == "mcp":
        (folder / entry).write_bytes((ROOT / "packages/mcps/tari-reference/server.py").read_bytes())
    else:
        header = f"---\nname: {slug}\ndescription: Guide Tari work using official sources and explicit network boundaries.\n---\n\n" if kind == "skill" else ""
        (folder / entry).write_text(header + f"# {title}\n\nDescribe the task, tool boundaries, review process and output contract.\n", encoding="utf-8", newline="\n")
    return folder


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("kind", choices=list(KINDS.values()))
    parser.add_argument("id")
    parser.add_argument("--maintainer", required=True)
    args = parser.parse_args()
    print(create(ROOT, args.kind, args.id, args.maintainer))


if __name__ == "__main__":
    main()
