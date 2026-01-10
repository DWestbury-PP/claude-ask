"""Tool definitions and configuration"""

from typing import Optional


def get_web_search_tool(
    max_uses: int = 5,
    allowed_domains: Optional[list[str]] = None,
    blocked_domains: Optional[list[str]] = None
) -> dict:
    """Build web search tool configuration"""

    tool = {
        "type": "web_search_20250305",
        "name": "web_search",
        "max_uses": max_uses
    }

    # Add domain filtering (mutually exclusive)
    if allowed_domains:
        tool["allowed_domains"] = allowed_domains
    elif blocked_domains:
        tool["blocked_domains"] = blocked_domains

    return tool


def get_enabled_tools(config) -> list:
    """Return list of enabled tools based on configuration"""
    tools = []

    if config.enable_web_search:
        tools.append(get_web_search_tool(
            max_uses=config.web_search_max_uses,
            allowed_domains=config.allowed_domains,
            blocked_domains=config.blocked_domains
        ))

    return tools
