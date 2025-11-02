https://github.com/Maciek-roboblog/Claude-Code-Usage-Monitor


First-time uv users
# On Linux/macOS:
curl -LsSf https://astral.sh/uv/install.sh | sh
# On Windows:
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"


# Install directly from PyPI with uv (easiest)
uv tool install claude-monitor

# Run from anywhere
claude-monitor  --help

claude-monitor --view realtime
claude-monitor --view monthly

claude-monitor --plan pro --view realtime