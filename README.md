# git-tools-mcp-client

An MCP client written in Python from scratch, with no model and no API key. It starts the
[git-tools-mcp-server](https://github.com/nononsense-ai/git-tools-mcp-server) from part 1 of the
series, does the handshake, lists its tools and calls them. A small command line program sits on
top.

This is part 2 of the MCP series.

- Website: https://nononsensecode.dev
- YouTube: [@nononsenseaeye](https://www.youtube.com/@nononsenseaeye)

## What it does

- `GitToolsClient` wraps the SDK's `Client` and gives you typed methods: `git_diff`, `git_commit`
  and `list_tool_names`.
- On connect it checks that the server still has the tools it needs (`REQUIRED_TOOLS`). If one is
  missing, it stops and names it.
- `_call` turns a failed tool call (`is_error=True`) into a `ToolCallError`, so that check lives
  in one place.
- Launch details live in `mcp.json`, which pydantic validates.
- Errors print as one line, `error: ...`, with exit code 1. The task group wraps the real error
  in `ExceptionGroup`s, so `main()` uses `except*` and walks down to it.
- Every request times out after 30 seconds unless you pass `--timeout`.

## Requirements

- Python 3.14 or newer
- [uv](https://docs.astral.sh/uv/)
- git
- The git tools server from part 1:

```
git clone https://github.com/nononsense-ai/git-tools-mcp-server.git
```

## Setup

```
uv sync

# scratch repo for the server to work on
rm -rf /tmp/scratch && mkdir /tmp/scratch && cd /tmp/scratch
git init -q
echo "hello" > a.txt
git add a.txt
cd -

# config: copy the example and put in the absolute path to your server project
cp mcp.example.json mcp.json
```

Edit `mcp.json` and replace `/path/to/git-tools-mcp-server` with the absolute path of the server
project. A relative path is resolved from wherever you run the command, so use an absolute one.
`mcp.json` is in `.gitignore` because it holds a path (and possibly API keys) that only exist on
your machine.

If git complains about who you are when committing, set `user.email` and `user.name` inside the
scratch repo.

## Usage

```
uv run git-tools-mcp-client --repo /tmp/scratch tools
uv run git-tools-mcp-client --repo /tmp/scratch diff
uv run git-tools-mcp-client --repo /tmp/scratch diff --unstaged
uv run git-tools-mcp-client --repo /tmp/scratch diff --path a.txt
uv run git-tools-mcp-client --repo /tmp/scratch commit -m "add a.txt"
```

Global options go before the subcommand:

| Option | Default | Meaning |
|---|---|---|
| `--config` | `$GIT_TOOLS_CONFIG`, else `mcp.json` | Path to the MCP servers config |
| `--server` | `git-tools` | Server name in the config |
| `--repo` | `.` | Repo the server should operate on |
| `--timeout` | `30.0` | Seconds to wait for a server response |

Subcommands:

| Command | Options |
|---|---|
| `tools` | none; works even if `--repo` is not a git repo |
| `diff` | `--unstaged`, `--path PATH` (staged changes by default) |
| `commit` | `-m/--message` (required) |

A failing call prints a single line:

```
$ uv run git-tools-mcp-client --repo /tmp/scratch diff --path no/such/file.txt
error: Error executing tool git_diff: ERROR: path not found in the repo: no/such/file.txt
```

The server's own git calls give up after 10 seconds, so the client's 30 second default leaves room
for a slow first start without hiding a real hang. If you raise the server's limit, raise
`--timeout` too.

## Project layout

```
mcp.example.json                 example config with a placeholder path
scripts/
  hello.py                       step 2: connect and list tools
  call.py                        step 3: call a tool, see is_error
  wrapper.py                     step 4: the same through GitToolsClient
src/git_tools_mcp_client/
  exceptions.py                  ClientError, ServerMismatchError, ToolCallError, ConfigError
  config.py                      McpConfig (pydantic), load_params, resolve_repo
  cli.py                         argparse setup
  client.py                      GitToolsClient, commands, run, main
```

## Following the video: tags

Each step of the video is one commit with an annotated tag. Check one out to see the code as it
stands at the end of that step:

```
git checkout step-04-typed-client
```

Go back with `git checkout main`. To see what a step changed, compare it with the previous one:

```
git diff step-03-call step-04-typed-client
```

| Tag | Step | What is added |
|---|---|---|
| `step-01-project` | 1. Create the project | uv package, `mcp` and `pydantic` dependencies |
| `step-02-connect` | 2. Connect and list the tools | `scripts/hello.py` |
| `step-03-call` | 3. Call a tool | `scripts/call.py` |
| `step-04-typed-client` | 4. The typed client | `exceptions.py`, `GitToolsClient`, `scripts/wrapper.py` |
| `step-05-config` | 5. mcp.json and pydantic | `config.py`, `mcp.example.json`, `mcp.json` in `.gitignore` |
| `step-06-cli` | 6. The command line | `cli.py`, commands in `client.py`, the `[project.scripts]` entry |
| `step-07-errors` | 7. Readable errors | `except*` in `main()`, `leaves()` |
| `step-08-timeout` | 8. Timeout | `--timeout` flag, `DEFAULT_TIMEOUT` |

`main` is the same code as `step-08-timeout`, plus this README. The README is empty in the tags.

Steps 9 (break it on purpose) and 10 (the `git_status` challenge) are exercises, so they have no
tag.

## License

MIT. See [LICENSE](LICENSE).
