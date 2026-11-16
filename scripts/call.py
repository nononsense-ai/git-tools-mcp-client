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
        result = await client.call_tool("git_diff", {"staged": True})
        print("is_error:", result.is_error)
        print("blocks:", [b.type for b in result.content])
        print(result.content[0].text)

        bad = await client.call_tool("git_diff", {"path": "no/such/file.txt"})
        print("is_error:", bad.is_error)
        print(bad.content[0].text)


asyncio.run(main())
