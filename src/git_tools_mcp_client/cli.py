import argparse
import os
from pathlib import Path


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(prog="git-tools-mcp-client")
    p.add_argument(
        "--config",
        type=Path,
        default=Path(os.environ.get("GIT_TOOLS_CONFIG", "mcp.json")),
        help="path to the MCP servers config",
    )
    p.add_argument(
        "--timeout",
        type=float,
        default=30.0,
        help="seconds to wait for a server response (default: 30s)",
    )
    p.add_argument("--server", default="git-tools", help="server name in the config")
    p.add_argument(
        "--repo", default=".", type=Path, help="repo the server should operate on"
    )

    sub = p.add_subparsers(dest="cmd", required=True)

    t = sub.add_parser("tools", help="list server tools")
    t.set_defaults(needs_repo=False)

    d = sub.add_parser("diff", help="show git diff")
    d.set_defaults(needs_repo=True)
    d.add_argument("--unstaged", action="store_true")
    d.add_argument("--path")

    c = sub.add_parser("commit", help="commit staged changes")
    c.set_defaults(needs_repo=True)
    c.add_argument("-m", "--message", required=True)

    return p.parse_args()
