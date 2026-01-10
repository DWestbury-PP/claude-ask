"""Agent loop with tool execution"""

import sys
import anthropic
from yaspin import yaspin
from ask.tools import get_enabled_tools


def run_agent_loop(
    client: anthropic.Anthropic,
    config,
    session,
    user_prompt: str,
    system_prompt: str
) -> str:
    """
    Execute agent loop with tool support.

    Returns the final text response from Claude.
    """
    # Get enabled tools
    tools = get_enabled_tools(config)

    # Add user message to session
    session.add_message("user", user_prompt)

    # Execute API call with web search tool
    try:
        with yaspin(text="Thinking...", color="cyan") as spinner:
            response = client.beta.messages.create(
                model=config.model,
                max_tokens=config.max_tokens,
                system=system_prompt,
                messages=session.to_api_messages(),
                tools=tools
            )
            spinner.ok("✓")
    except anthropic.APIError as e:
        print(f"Error: API request failed: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    # Extract final text response
    final_text = extract_final_response(response)

    # Add assistant response to session (convert content blocks to dicts)
    content_dicts = []
    for block in response.content:
        if hasattr(block, 'model_dump'):
            content_dicts.append(block.model_dump())
        elif hasattr(block, 'dict'):
            content_dicts.append(block.dict())
        else:
            # Fallback for plain dicts
            content_dicts.append(block)

    session.add_message("assistant", content_dicts)

    # Save session
    session.save(config.session_dir)

    return final_text


def extract_final_response(response) -> str:
    """Extract text content from response"""
    # Response content is a list of content blocks
    # We want the final text block(s)
    text_parts = []

    for block in response.content:
        if hasattr(block, 'type') and block.type == 'text':
            text_parts.append(block.text)

    return '\n\n'.join(text_parts) if text_parts else ""
