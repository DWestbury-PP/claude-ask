# ask - Claude AI Command-Line Tool

A simple, fast command-line tool to interact with Claude AI directly from your terminal.

## Features

- 🚀 Quick one-shot questions to Claude
- 📋 Pipe command output for analysis
- ⚡ Shows a spinner during API calls (like docker-compose)
- 🔧 Works on macOS (Apple Silicon), Intel-based RHEL, and AMD-based Ubuntu
- 🔐 Secure API key management via `.env` files

## Requirements

- Python 3.10 or higher
- Anthropic API key ([get one here](https://console.anthropic.com/settings/keys))

## Installation

### 1. Clone or download this repository

```bash
cd /path/to/ask-claude
```

### 2. Install the package

```bash
pip install .
```

This will install the `ask` command to your Python environment's bin directory, which should be in your PATH.

### 3. Set up your API key

Create a `.env` file in one of these locations:

**Option A: Global configuration (recommended)**
```bash
mkdir -p ~/.config/ask
echo "ANTHROPIC_API_KEY=your-key-here" > ~/.config/ask/.env
```

**Option B: Project-specific configuration**
```bash
echo "ANTHROPIC_API_KEY=your-key-here" > .env
```

Replace `your-key-here` with your actual Anthropic API key from https://console.anthropic.com/settings/keys

### 4. (Optional) Install to /usr/local/bin

If you want the command available system-wide without activating a Python environment:

```bash
# After pip install, find where the script was installed
which ask

# Create a symlink (adjust the source path based on your system)
sudo ln -sf $(which ask) /usr/local/bin/ask
```

## Usage

### Direct questions

```bash
ask "what day of the week is it today?"
```

### Pipe input for analysis

```bash
cat docker-compose.yml | ask "How many containers are in this application and what do you think it does?"
```

```bash
ls -la | ask "what files are taking up the most space?"
```

```bash
git diff | ask "summarize these changes"
```

### Combine piped input with a question

```bash
docker ps | ask "are any of these containers unhealthy?"
```

## How It Works

The tool:
1. Reads your Anthropic API key from a `.env` file
2. Accepts input from command-line arguments and/or stdin (pipes)
3. Sends your question to Claude AI (using the `claude-sonnet-4-20250514` model)
4. Displays a spinner while waiting for the response
5. Prints Claude's answer to stdout

## Platform Compatibility

Tested and working on:
- ✅ macOS (Apple Silicon)
- ✅ Intel-based RHEL
- ✅ AMD-based Ubuntu

## Troubleshooting

### "ANTHROPIC_API_KEY environment variable is not set"

Make sure you've created a `.env` file in either:
- `~/.config/ask/.env` (global)
- Current directory (project-specific)

### "command not found: ask"

Make sure the Python bin directory is in your PATH, or follow the optional step to symlink to `/usr/local/bin`.

### Dependencies not installing

Make sure you have Python 3.10 or higher:
```bash
python3 --version
```

## Example .env File

See `example.env` for a template:

```
ANTHROPIC_API_KEY=sk-ant-api03-xxx
```

## Dependencies

- `anthropic` - Official Anthropic Python SDK
- `python-dotenv` - Load environment variables from .env files
- `yaspin` - Terminal spinner for better UX

## License

This tool is provided as-is for personal and commercial use.

