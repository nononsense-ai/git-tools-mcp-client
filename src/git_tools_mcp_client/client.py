import asyncio
import sys
from argparse import Namespace
from collections.abc import Awaitable, Callable
from typing import Any, ClassVar

from mcp import Client, StdioServerParameters
from mcp.shared.exceptions import MCPError

from git_tools_mcp_client.cli import parse_args
from git_tools_mcp_client.config import load_params, resolve_repo
from git_tools_mcp_client.exceptions import (
    ClientError,
    ServerMismatchError,
    ToolCallError,
)

DEFAULT_TIMEOUT = 30.0


class GitToolsClient:
    REQUIRED_TOOLS: ClassVar[frozenset[str]] = frozenset({"git_diff", "git_commit"})

    def __init__(
        self, params: StdioServerParameters, timeout: float | None = DEFAULT_TIMEOUT
    ) -> None:
        self._client = Client(params, read_timeout_seconds=timeout)

    async def __aenter__(self):
        await self._client.__aenter__()
        try:
            await self._verify_tools()
        except BaseException:
            await self._client.__aexit__(*sys.exc_info())
            raise
        return self

    async def __aexit__(self, *exc) -> None:
        return await self._client.__aexit__(*exc)

    async def _verify_tools(self) -> None:
        names = {t.name for t in (await self._client.list_tools()).tools}
        missing = self.REQUIRED_TOOLS - names
        if missing:
            raise ServerMismatchError(
                f"Server is missing tools: {', '.join(sorted(missing))}"
            )

    async def _call(self, name: str, args: dict[str, Any]) -> str:
        result = await self._client.call_tool(name, args)
        text = "\n".join(b.text for b in result.content if b.type == "text")
        if result.is_error:
            raise ToolCallError(text or f"{name} failed with no message")
        return text

    async def git_diff(self, staged: bool = True, path: str | None = None) -> str:
        args: dict[str, Any] = {"staged": staged}
        if path:
            args["path"] = path
        return await self._call("git_diff", args)

    async def git_commit(self, message: str) -> str:
        return await self._call("git_commit", {"message": message})

    async def list_tool_names(self) -> list[str]:
        return [t.name for t in (await self._client.list_tools()).tools]


Handler = Callable[[GitToolsClient, Namespace], Awaitable[None]]


async def cmd_diff(git: GitToolsClient, args: Namespace) -> None:
    print(await git.git_diff(staged=not args.unstaged, path=args.path))


async def cmd_commit(git: GitToolsClient, args: Namespace) -> None:
    print(await git.git_commit(args.message))


async def cmd_tools(git: GitToolsClient, args: Namespace) -> None:
    for name in await git.list_tool_names():
        print(name)


COMMANDS: dict[str, Handler] = {
    "diff": cmd_diff,
    "commit": cmd_commit,
    "tools": cmd_tools,
}


async def run(args: Namespace) -> None:
    repo = resolve_repo(args.repo) if args.needs_repo else None
    params = load_params(args.config, args.server, repo)

    async with GitToolsClient(params, timeout=args.timeout) as git:
        handler = COMMANDS[args.cmd]
        await handler(git, args)


def leaves(exc: BaseException):
    if isinstance(exc, BaseExceptionGroup):
        for sub in exc.exceptions:
            yield from leaves(sub)
    else:
        yield exc


def main() -> None:
    args = parse_args()
    try:
        asyncio.run(run(args))
    except* (ClientError, OSError, MCPError) as eg:
        for e in leaves(eg):
            print(f"error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
