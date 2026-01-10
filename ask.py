#!/usr/bin/env python3
"""
ask - A command-line tool to interact with Claude AI
"""

import sys
from datetime import datetime
import anthropic
from yaspin import yaspin
from rich.console import Console
from rich.markdown import Markdown

from ask.config import AskConfig
from ask.session import SessionManager
from ask.agent_loop import run_agent_loop


def get_input():
    """
    Get input from command-line arguments and/or stdin.
    Returns the formatted prompt string.
    """
    # Get command-line arguments (excluding script name)
    args_prompt = ' '.join(sys.argv[1:])
    
    # Check if stdin has data (piped input)
    piped_input = ""
    if not sys.stdin.isatty():
        piped_input = sys.stdin.read().strip()
    
    # Combine piped input with prompt
    if piped_input:
        if args_prompt:
            # User provided both piped input and a question
            prompt = f"{args_prompt}\n\n```\n{piped_input}\n```"
        else:
            # Only piped input, no question
            prompt = piped_input
    else:
        prompt = args_prompt
    
    # Ensure we have something to ask
    if not prompt:
        print("Usage: ask 'your question' or command | ask 'analyze this'", file=sys.stderr)
        sys.exit(1)
    
    return prompt


def get_system_prompt(enable_tools: bool = True):
    """
    Generate system prompt with current date and tool guidance.
    """
    current_datetime = datetime.now().strftime("%A, %B %d, %Y at %I:%M %p %Z")

    base_prompt = f"""You are a helpful DevOps assistant. The current date and time is: {current_datetime}

When responding, format your answers for optimal terminal readability:
- Use emojis to make output more engaging and scannable
- Use markdown formatting (headers, bold, code blocks, lists) to structure your response
- Keep responses concise and well-organized
- Use bullet points and numbered lists where appropriate"""

    if enable_tools:
        tool_guidance = """

You have access to a web_search tool that can find current information from the internet.

When to use web_search:
- For current events, news, or time-sensitive information
- When you need to verify recent data or statistics
- For documentation, package versions, or API references
- When the user asks about something that requires up-to-date information
- When your knowledge cutoff (January 2025) might make your response outdated

When NOT to use web_search:
- For general knowledge questions you can answer confidently
- For coding or technical questions within your expertise
- When analyzing user-provided data (piped input)
- For simple calculations or transformations

Be judicious with web searches - use them when they add real value, not reflexively."""

        return base_prompt + tool_guidance

    return base_prompt


def ask_claude(config, prompt, system_prompt):
    """
    Send the prompt to Claude API and return the response.
    """
    try:
        client = anthropic.Anthropic(api_key=config.api_key)

        with yaspin(text="Thinking...", color="cyan") as spinner:
            message = client.messages.create(
                model=config.model,
                max_tokens=config.max_tokens,
                system=system_prompt,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            spinner.ok("✓")
        
        # Extract the text from the response
        return message.content[0].text
    
    except anthropic.APIError as e:
        print(f"Error: API request failed: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def main():
    """
    Main entry point for the ask command.
    """
    # Load configuration
    config = AskConfig.from_env()

    # Get user input
    prompt = get_input()

    # Initialize API client
    client = anthropic.Anthropic(api_key=config.api_key)

    # Get system prompt
    system_prompt = get_system_prompt(enable_tools=config.enable_tools)

    # Determine whether to use agent loop or simple query
    if config.enable_tools:
        # Initialize session manager
        session_manager = SessionManager(config)
        session_manager.cleanup_expired_sessions()
        session = session_manager.get_or_create_session()

        # Run agent loop with tools
        response = run_agent_loop(client, config, session, prompt, system_prompt)
    else:
        # Fallback to simple query (backward compatible)
        response = ask_claude(config, prompt, system_prompt)

    # Print the response with rich formatting
    console = Console()
    md = Markdown(response)
    console.print(md)


if __name__ == '__main__':
    main()

