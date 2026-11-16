import asyncio

from mcp import Client, StdioServerParameters

SERVER_DIR = "/absolute/path/to/git-tools-mcp-server"

params = StdioServerParameters(
    command="uv",
    args=["run", "--directory", SERVER_DIR, "git-tools-mcp-server"],
    env={"GIT_TOOLS_REPO": "/tmp/scratch"},
)


async def main() -> None:
    async with Client(params) as client:
        print("instructions:", client.instructions)
        for tool in (await client.list_tools()).tools:
            print(tool.name, "-", tool.description.splitlines()[0])


asyncio.run(main())
