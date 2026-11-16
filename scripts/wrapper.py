import asyncio

from mcp import StdioServerParameters

from git_tools_mcp_client.client import GitToolsClient

SERVER_DIR = "/absolute/path/to/git-tools-mcp-server"

params = StdioServerParameters(
    command="uv",
    args=["run", "--directory", SERVER_DIR, "git-tools-mcp-server"],
    env={"GIT_TOOLS_REPO": "/tmp/scratch"},
)


async def main() -> None:
    async with GitToolsClient(params) as git:
        print(await git.list_tool_names())
        print(await git.git_diff())


asyncio.run(main())
