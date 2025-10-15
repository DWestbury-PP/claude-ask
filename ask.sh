#!/usr/bin/env bash
# Save this as /usr/local/bin/ask

ask() {
  local prompt=""
  local piped_input=""
  
  # Check for API key first
  if [ -z "$ANTHROPIC_API_KEY" ]; then
    echo "Error: ANTHROPIC_API_KEY environment variable is not set." >&2
    echo "" >&2
    echo "To fix this:" >&2
    echo "  1. Get your API key from https://console.anthropic.com/settings/keys" >&2
    echo "  2. Add to your shell config (~/.bashrc or ~/.zshrc):" >&2
    echo "     export ANTHROPIC_API_KEY='your-key-here'" >&2
    echo "  3. Reload your shell: source ~/.bashrc (or ~/.zshrc)" >&2
    return 1
  fi
  
  # Check if stdin is piped
  if [ ! -t 0 ]; then
    piped_input=$(cat)
  fi
  
  # Get the question from arguments
  prompt="$*"
  
  # Combine piped input with prompt if both exist
  if [ -n "$piped_input" ]; then
    if [ -n "$prompt" ]; then
      prompt="$prompt\n\n\`\`\`\n$piped_input\n\`\`\`"
    else
      prompt="$piped_input"
    fi
  fi
  
  # Ensure we have something to ask
  if [ -z "$prompt" ]; then
    echo "Usage: ask 'your question' or command | ask 'analyze this'" >&2
    return 1
  fi
  
  # Check for jq
  if ! command -v jq &> /dev/null; then
    echo "Error: jq is required but not installed." >&2
    echo "Install it with: brew install jq" >&2
    return 1
  fi
  
  # Get current date and time
  local current_datetime=$(date "+%A, %B %d, %Y at %I:%M %p %Z")
  
  # Create system prompt with current date
  local system_prompt="You are a helpful DevOps assistant. The current date and time is: $current_datetime"
  
  # Escape prompts for JSON
  local escaped_system=$(echo -n "$system_prompt" | jq -Rs .)
  local escaped_prompt=$(echo -n "$prompt" | jq -Rs .)
  
  # Call Claude API with system prompt
  local response=$(curl -s https://api.anthropic.com/v1/messages \
    -H "x-api-key: ${ANTHROPIC_API_KEY}" \
    -H "anthropic-version: 2023-06-01" \
    -H "content-type: application/json" \
    -d "{
      \"model\": \"claude-sonnet-4-5-20250929\",
      \"max_tokens\": 4096,
      \"system\": $escaped_system,
      \"messages\": [{
        \"role\": \"user\",
        \"content\": $escaped_prompt
      }]
    }")
  
  # Check for API errors
  local error=$(echo "$response" | jq -r '.error.message // empty')
  if [ -n "$error" ]; then
    echo "Error: $error" >&2
    return 1
  fi
  
  # Extract and display the response
  echo "$response" | jq -r '.content[0].text'
}

# If script is executed directly (not sourced), run the function
if [ "${BASH_SOURCE[0]}" == "${0}" ]; then
  ask "$@"
fi
