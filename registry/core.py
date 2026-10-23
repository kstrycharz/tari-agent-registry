"""Validate inert package data and build reproducible downloads."""
import argparse
import hashlib
import io
import json
import os
import re
import stat
import sys
import zipfile
from pathlib import Path, PurePosixPath

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
KINDS = {"agents": "agent", "mcps": "mcp", "skills": "skill"}
EXTENSIONS = {".md", ".json", ".py", ".js", ".ts", ".rs", ".toml", ".txt", ".yaml", ".yml", ".sh", ".ps1"}
MAX_FILE = 512 * 1024
MAX_PACKAGE = 2 * 1024 * 1024
MAX_FILES = 100
SLUG = re.compile(r"[a-z][a-z0-9]*(?:-[a-z0-9]+)*\Z")
# These are blocking indicators, not a malware verdict. Keep rules in trusted code.
RULES = [
    ("private-key", re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----")),
    ("github-token", re.compile(r"\b(?:gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{30,})\b")),
    ("aws-key", re.compile(r"\b(?:AKIA|ASIA)[A-Z0-9]{16}\b")),
    ("download-and-execute", re.compile(r"(?:curl|wget)[^\n]{0,300}\|\s*(?:sh|bash|zsh|python|pwsh)", re.I)),
    ("encoded-powershell", re.compile(r"(?:powershell|pwsh)[^\n]{0,150}-(?:enc|encodedcommand)\b", re.I)),
    ("dynamic-execution", re.compile(r"\b(?:eval|exec)\s*\(", re.I)),
    ("prompt-override", re.compile(r"ignore\s+(?:all\s+)?(?:previous|prior|system)\s+instructions", re.I)),
    ("secret-exfiltration", re.compile(r"(?:upload|send|exfiltrate)\s+(?:the\s+)?(?:seed phrase|private key|wallet seed)", re.I)),
]


class Invalid(ValueError):
    pass


def read_text(path):
    if path.is_symlink() or not path.is_file():
        raise Invalid(f"Expected regular file: {path.name}")
    if path.stat().st_size > MAX_FILE:
        raise Invalid(f"File exceeds {MAX_FILE} bytes: {path.name}")
    raw = path.read_bytes()
    try:
        value = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise Invalid(f"Not UTF-8 text: {path.name}") from exc
    if any(ord(c) < 32 and c not in "\n\r\t" for c in value) or any(c in value for c in "\u202a\u202b\u202d\u202e\u2066\u2067\u2068\u2069"):
        raise Invalid(f"Binary/control or bidi content: {path.name}")
    return value


def no_duplicates(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise Invalid(f"Duplicate JSON key: {key}")
        result[key] = value
    return result


def read_json(path):
    return json.loads(read_text(path), object_pairs_hook=no_duplicates)


def safe_relative(value):
    p = PurePosixPath(value)
    reserved = {"con", "prn", "aux", "nul"} | {f"com{i}" for i in range(1, 10)} | {f"lpt{i}" for i in range(1, 10)}
    return bool(value) and not p.is_absolute() and not any(x in {"", ".", ".."} for x in value.split("/")) and not re.search(r"[^a-zA-Z0-9_./-]", value) and all(not x.startswith(".") and not x.endswith(".") and x.split(".")[0].lower() not in reserved for x in p.parts)


def scan_text(value, label):
    for name, pattern in RULES:
        if pattern.search(value):
            # Do not echo matching text: it might contain a real credential.
            raise Invalid(f"Security indicator {name} in {label}; maintainer review required")


def risk(manifest):
    permissions = set(manifest["permissions"])
    if permissions & {"wallet:sign", "wallet:spend", "process:execute", "filesystem:write"}:
        return "high"
    return "medium" if permissions else "low"


def inspect_package(folder, schema, kind):
    scan_text(read_text(folder / "manifest.json"), "manifest.json")
    manifest = read_json(folder / "manifest.json")
    errors = sorted(Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(manifest), key=lambda e: str(e.path))
    if errors:
        raise Invalid(f"{folder.name}/manifest.json: {errors[0].json_path}: {errors[0].message}")
    if manifest["kind"] != kind or manifest["id"] != folder.name:
        raise Invalid(f"Kind/id does not match directory: {folder.name}")
    actual, total = [], 0
    for base, dirs, files in os.walk(folder, followlinks=False):
        if len(dirs) + len(files) > MAX_FILES:
            raise Invalid("Too many directory entries")
        for name in dirs + files:
            p = Path(base) / name
            rel = p.relative_to(folder).as_posix()
            if p.is_symlink() or not safe_relative(rel):
                raise Invalid(f"Unsafe path: {rel}")
            if name in files:
                if len(actual) >= MAX_FILES:
                    raise Invalid("Too many package files")
                if p.suffix not in EXTENSIONS and name != "LICENSE":
                    raise Invalid(f"Disallowed file type: {rel}")
                content = read_text(p)
                total += p.stat().st_size
                if total > MAX_PACKAGE:
                    raise Invalid("Package too large")
                scan_text(content, rel)
                actual.append(rel)
    expected = set(manifest["files"]) | {"manifest.json"}
    if "manifest.json" in manifest["files"] or len({x.casefold() for x in actual}) != len(actual):
        raise Invalid("Manifest cannot list itself; case-colliding paths are forbidden")
    if set(actual) != expected:
        raise Invalid(f"File inventory mismatch in {folder.name}: undeclared={sorted(set(actual)-expected)}, missing={sorted(expected-set(actual))}")
    if not {"README.md", "LICENSE", manifest["entrypoint"]}.issubset(manifest["files"]):
        raise Invalid("README.md, LICENSE and entrypoint must be declared")
    for value in manifest["files"]:
        if not safe_relative(value):
            raise Invalid("Unsafe manifest file path")
    if "network:read" not in manifest["permissions"] and manifest["network_hosts"]:
        raise Invalid("network_hosts requires network:read permission")
    if "network:read" in manifest["permissions"] and not manifest["network_hosts"]:
        raise Invalid("network:read requires explicit host allowlist")
    if kind == "skill":
        if manifest["runtime"] != "instructions":
            raise Invalid("Skills use runtime instructions")
        if manifest["entrypoint"] != "SKILL.md":
            raise Invalid("Skills require SKILL.md entrypoint")
        text = read_text(folder / "SKILL.md")
        match = re.match(r"\A---\r?\nname: ([a-z0-9-]+)\r?\ndescription: ([^\r\n]+)\r?\n---(?:\r?\n|$)", text)
        if not match or match[1] != manifest["id"]:
            raise Invalid("SKILL.md needs simple name/description YAML frontmatter matching id")
    if kind == "agent" and (manifest["entrypoint"] != "AGENT.md" or manifest["runtime"] != "instructions"):
        raise Invalid("Agents require AGENT.md entrypoint and runtime instructions")
    if kind == "mcp":
        if manifest["runtime"] != "python3" or not manifest["entrypoint"].endswith(".py"):
            raise Invalid("Initial MCP format supports dependency-free Python stdio servers")
    return manifest


def validate(root, policy_root=ROOT):
    packages = root / "packages"
    if packages.is_symlink() or not packages.is_dir():
        raise Invalid("Missing regular packages directory")
    schema = read_json(policy_root / "schemas" / "manifest.schema.json")
    results, identities = [], set()
    if {p.name for p in packages.iterdir()} != set(KINDS):
        raise Invalid("packages must contain exactly agents/, mcps/, skills/")
    for group, kind in KINDS.items():
        parent = packages / group
        if parent.is_symlink() or not parent.is_dir():
            raise Invalid(f"Unsafe kind directory: {group}")
        for folder in sorted(parent.iterdir()):
            if folder.is_symlink() or not folder.is_dir() or not SLUG.fullmatch(folder.name):
                raise Invalid(f"Unsafe package directory: {folder.name}")
            if len(results) >= 1000:
                raise Invalid("Registry package limit reached")
            manifest = inspect_package(folder, schema, kind)
            identity = (kind, manifest["id"])
            if identity in identities:
                raise Invalid("Duplicate package identity")
            identities.add(identity)
            results.append((folder, manifest))
    if not results:
        raise Invalid("Registry cannot be empty")
    return results


def scan_repository_secrets(root):
    count = 0
    for base, dirs, files in os.walk(root, followlinks=False):
        dirs[:] = [d for d in dirs if d not in {".git", ".venv", ".deps", "node_modules", "__pycache__", "dist"}]
        for name in dirs + files:
            path = Path(base) / name
            if path.is_symlink():
                raise Invalid("Repository symlinks are not accepted")
        for name in files:
            count += 1
            if count > 20000:
                raise Invalid("Repository file limit reached")
            path = Path(base) / name
            if path.stat().st_size > 2 * 1024 * 1024:
                raise Invalid("Repository file exceeds scan size limit")
            if name == ".gitmodules":
                raise Invalid("Submodules are not accepted")
            try:
                content = path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                continue  # binary payloads are forbidden in entries; ClamAV scans the tree
            for rule, pattern in RULES[:3]:
                if pattern.search(content):
                    raise Invalid(f"Credential indicator {rule} in {path.relative_to(root)}")


def check_versions(root, previous, policy_root=ROOT):
    current = {(m["kind"], m["id"]): (p, m) for p, m in validate(root, policy_root)}
    for old_path, old in validate(previous, policy_root):
        key = old["kind"], old["id"]
        if key not in current:
            raise Invalid("Remove packages through a reviewed deprecation release, not deletion")
        new_path, new = current[key]
        changed = set(new["files"]) != set(old["files"]) or any((new_path / f).read_bytes() != (old_path / f).read_bytes() for f in set(old["files"]) & set(new["files"])) or new != old
        if changed and tuple(map(int, new["version"].split("."))) <= tuple(map(int, old["version"].split("."))):
            raise Invalid(f"Changed package needs version increase: {new['id']}")


def archive(folder, manifest):
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for name in sorted(manifest["files"] + ["manifest.json"]):
            info = zipfile.ZipInfo(f"{manifest['id']}/{name}", (2020, 1, 1, 0, 0, 0))
            info.create_system = 3
            info.external_attr = (stat.S_IFREG | 0o644) << 16
            info.compress_type = zipfile.ZIP_DEFLATED
            z.writestr(info, (folder / name).read_bytes())
    return buffer.getvalue()


def build(root, output, revision, policy_root=ROOT):
    entries = validate(root, policy_root)
    if output.exists() and any(output.iterdir()):
        raise Invalid("Output must be absent or empty; use a fresh directory")
    output.mkdir(parents=True, exist_ok=True)
    (output / "downloads").mkdir()
    catalog, sums = [], []
    for folder, manifest in entries:
        data = archive(folder, manifest)
        name = f"{manifest['kind']}-{manifest['id']}-{manifest['version']}.zip"
        digest = hashlib.sha256(data).hexdigest()
        (output / "downloads" / name).write_bytes(data)
        catalog.append({**manifest, "risk": risk(manifest), "download": f"downloads/{name}", "sha256": digest, "size": len(data)})
        sums.append(f"{digest}  downloads/{name}")
    feed = {"schema_version": 1, "revision": revision, "publisher": "TariTracker community", "packages": catalog}
    data = (json.dumps(feed, indent=2, sort_keys=True) + "\n").encode()
    (output / "catalog.json").write_bytes(data)
    sums.append(f"{hashlib.sha256(data).hexdigest()}  catalog.json")
    (output / "SHA256SUMS").write_text("\n".join(sums) + "\n", encoding="utf-8", newline="\n")
    (output / ".nojekyll").touch()
    return feed


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["validate", "build"])
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--previous", type=Path)
    parser.add_argument("--output", type=Path, default=ROOT / "dist")
    parser.add_argument("--revision", default="local")
    args = parser.parse_args()
    try:
        scan_repository_secrets(args.root)
        if args.previous:
            check_versions(args.root, args.previous)
        if args.command == "build":
            feed = build(args.root, args.output, args.revision)
            print(f"Built {len(feed['packages'])} packages in {args.output}")
        else:
            print(f"Validated {len(validate(args.root))} packages")
    except (Invalid, ValueError, OSError) as exc:
        print(f"Registry check failed: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
