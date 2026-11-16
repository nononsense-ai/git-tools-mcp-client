import sys
from typing import Any, ClassVar

from mcp import Client, StdioServerParameters

from git_tools_mcp_client.exceptions import ServerMismatchError, ToolCallError

class GitToolsClient:
    REQUIRED_TOOLS: ClassVar[frozenset[str]] = frozenset({"git_diff", "git_commit"})

    def __init__(self, params: StdioServerParameters) -> None:
        self._client = Client(params)

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
