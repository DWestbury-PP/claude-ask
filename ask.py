#!/usr/bin/env python3
"""
ask - A command-line tool to interact with Claude AI
"""

import sys
import os
from pathlib import Path
from datetime import datetime
import anthropic
from dotenv import load_dotenv
from yaspin import yaspin


def load_api_key():
    """
    Load the Anthropic API key from .env file.
    Tries current directory first, then falls back to ~/.config/ask/.env
    """
    # Try current directory
    if Path('.env').exists():
        load_dotenv('.env')
    else:
        # Try config directory
        config_path = Path.home() / '.config' / 'ask' / '.env'
        if config_path.exists():
            load_dotenv(config_path)
    
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
    
    return api_key


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


def get_system_prompt():
    """
    Generate the system prompt with current date and time.
    """
    current_datetime = datetime.now().strftime("%A, %B %d, %Y at %I:%M %p %Z")
    return f"You are a helpful DevOps assistant. The current date and time is: {current_datetime}"


def ask_claude(api_key, prompt, system_prompt):
    """
    Send the prompt to Claude API and return the response.
    """
    try:
        client = anthropic.Anthropic(api_key=api_key)
        
        with yaspin(text="Thinking...", color="cyan") as spinner:
            message = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=4096,
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
    # Load API key
    api_key = load_api_key()
    
    # Get user input
    prompt = get_input()
    
    # Get system prompt
    system_prompt = get_system_prompt()
    
    # Ask Claude
    response = ask_claude(api_key, prompt, system_prompt)
    
    # Print the response
    print(response)


if __name__ == '__main__':
    main()

