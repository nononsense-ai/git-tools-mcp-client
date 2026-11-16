from pathlib import Path

from mcp import StdioServerParameters
from pydantic import BaseModel, Field, ValidationError

from git_tools_mcp_client.exceptions import ConfigError


class McpConfig(BaseModel):
    servers: dict[str, StdioServerParameters] = Field(alias="mcpServers")


def format_errors(e: ValidationError) -> str:
    lines = []
    for err in e.errors():
        loc = ".".join(str(p) for p in err["loc"]) or "<root>"
        lines.append(f"  {loc}: {err['msg']}")
    return "\n".join(lines)


def resolve_repo(repo: Path) -> Path:
    repo_path = repo.expanduser().resolve()
    if not (repo_path / ".git").exists():
        raise ConfigError(f"not a git repo: {repo_path}")
    return repo_path


def load_config(path: Path) -> McpConfig:
    try:
        return McpConfig.model_validate_json(path.read_text())
    except FileNotFoundError:
        raise ConfigError(f"config not found: {path}") from None
    except ValidationError as e:
        raise ConfigError(f"invalid config: {path}: \n{format_errors(e)}") from e


def load_params(
    config_path: Path, server: str, repo: Path | None
) -> StdioServerParameters:
    config = load_config(config_path.expanduser())

    if server not in config.servers:
        raise ConfigError(
            f"server '{server}' not in config; have: {', '.join(config.servers)}"
        )

    params = config.servers[server]
    if repo is not None:
        params.env = {
            **(params.env or {}),
            "GIT_TOOLS_REPO": str(repo),
        }
    return params
