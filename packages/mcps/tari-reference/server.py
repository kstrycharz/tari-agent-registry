"""Local MCP reference lookup. Does not fetch URLs or access wallets/files."""
import json
import sys

VERSIONS = {"2025-11-25", "2025-06-18", "2024-11-05"}
REFERENCES = {
    "tari": {"title": "Tari", "url": "https://tari.com/", "scope": "Protocol, mining and ecosystem overview"},
    "ootle": {"title": "Tari Ootle Playground", "url": "https://ootle.tari.com/", "scope": "L2 concepts, wallet, templates and transaction guides"},
    "source": {"title": "Tari source repositories", "url": "https://github.com/tari-project", "scope": "Verify exact released source and dependencies"},
}


def handle(request):
    if not isinstance(request, dict) or request.get("jsonrpc") != "2.0" or not isinstance(request.get("method"), str):
        return {"jsonrpc": "2.0", "id": None, "error": {"code": -32600, "message": "Invalid request"}}
    if "id" not in request:
        return None
    ident = request["id"]
    method = request["method"]
    params = request.get("params", {})
    result, error = None, None
    if not isinstance(params, dict):
        error = {"code": -32602, "message": "params must be an object"}
    elif method == "initialize":
        requested = params.get("protocolVersion")
        result = {"protocolVersion": requested if isinstance(requested, str) and requested in VERSIONS else "2025-11-25", "capabilities": {"tools": {}}, "serverInfo": {"name": "tari-reference", "version": "1.0.0"}}
    elif method == "ping":
        result = {}
    elif method == "tools/list":
        result = {"tools": [{"name": "tari_reference", "description": "Return curated official Tari links. No network fetch or live chain data.", "inputSchema": {"type": "object", "properties": {"topic": {"type": "string", "enum": list(REFERENCES)}}, "required": ["topic"], "additionalProperties": False}, "annotations": {"readOnlyHint": True, "destructiveHint": False, "openWorldHint": False}}]}
    elif method == "tools/call":
        args = params.get("arguments", {})
        if params.get("name") != "tari_reference" or not isinstance(args, dict) or set(args) != {"topic"} or not isinstance(args.get("topic"), str) or args["topic"] not in REFERENCES:
            error = {"code": -32602, "message": "Use tari_reference with topic tari, ootle or source"}
        else:
            result = {"content": [{"type": "text", "text": json.dumps(REFERENCES[args["topic"]])}], "isError": False}
    else:
        error = {"code": -32601, "message": "Method not found"}
    return {"jsonrpc": "2.0", "id": ident, **({"error": error} if error else {"result": result})}


def main():
    while True:
        line = sys.stdin.buffer.readline(65538)
        if not line:
            break
        if len(line) > 65536:
            print("Input line limit exceeded", file=sys.stderr)
            return 1
        try:
            response = handle(json.loads(line))
        except (ValueError, UnicodeError):
            response = {"jsonrpc": "2.0", "id": None, "error": {"code": -32700, "message": "Parse error"}}
        if response is not None:
            print(json.dumps(response), flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
