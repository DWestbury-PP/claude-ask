"""Configuration management for ask-claude"""

import os
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv


@dataclass
class AskConfig:
    """Configuration for ask-claude"""

    api_key: str
    model: str = "claude-sonnet-4-20250514"
    max_tokens: int = 4096
    enable_tools: bool = True
    enable_web_search: bool = True
    web_search_max_uses: int = 5
    allowed_domains: Optional[list[str]] = None
    blocked_domains: Optional[list[str]] = None
    session_timeout_hours: int = 24
    session_dir: Path = field(
        default_factory=lambda: Path.home() / ".cache" / "ask-claude" / "sessions"
    )

    @classmethod
    def from_env(cls) -> "AskConfig":
        """Load configuration from environment variables and .env files"""
        # Load .env files (current dir, then ~/.config/ask/.env)
        if Path('.env').exists():
            load_dotenv('.env')
        else:
            config_path = Path.home() / '.config' / 'ask' / '.env'
            if config_path.exists():
                load_dotenv(config_path)

        # Get API key (required)
        api_key = os.getenv('ANTHROPIC_API_KEY')
        if not api_key:
            print("Error: ANTHROPIC_API_KEY environment variable is not set.", file=sys.stderr)
            print("", file=sys.stderr)
            print("To fix this:", file=sys.stderr)
            print("  1. Get your API key from https://console.anthropic.com/settings/keys", file=sys.stderr)
            print("  2. Create a .env file in one of these locations:", file=sys.stderr)
            print("     - Current directory: .env", file=sys.stderr)
            print("     - Config directory: ~/.config/ask/.env", file=sys.stderr)
            print("  3. Add this line to the file:", file=sys.stderr)
            print("     ANTHROPIC_API_KEY=your-key-here", file=sys.stderr)
            sys.exit(1)

        # Create config with default values
        config = cls(api_key=api_key)

        # Parse optional config from environment
        if model := os.getenv('ASK_MODEL'):
            config.model = model

        if max_tokens := os.getenv('ASK_MAX_TOKENS'):
            config.max_tokens = int(max_tokens)

        if enable_tools := os.getenv('ASK_ENABLE_TOOLS'):
            config.enable_tools = enable_tools.lower() == 'true'

        if enable_web_search := os.getenv('ASK_ENABLE_WEB_SEARCH'):
            config.enable_web_search = enable_web_search.lower() == 'true'

        if max_uses := os.getenv('ASK_WEB_SEARCH_MAX_USES'):
            config.web_search_max_uses = int(max_uses)

        if allowed := os.getenv('ASK_ALLOWED_DOMAINS'):
            config.allowed_domains = [d.strip() for d in allowed.split(',') if d.strip()]

        if blocked := os.getenv('ASK_BLOCKED_DOMAINS'):
            config.blocked_domains = [d.strip() for d in blocked.split(',') if d.strip()]

        if timeout := os.getenv('ASK_SESSION_TIMEOUT_HOURS'):
            config.session_timeout_hours = int(timeout)

        return config
