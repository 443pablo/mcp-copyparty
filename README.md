# MCP Server for copyparty

A [FastMCP](https://github.com/jlowin/fastmcp) server for interacting with [copyparty](https://github.com/9001/copyparty) file servers via the Model Context Protocol. This server enables AI assistants and other MCP clients to manage files on copyparty servers.

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/443pablo/mcp-copyparty)

## Features

This MCP server provides the following tools for interacting with copyparty:

- **list_files** - List files and folders in a directory
- **download_file** - Download files from the server
- **upload_file** - Upload files to the server
- **create_directory** - Create new directories
- **delete_file** - Delete files or directories
- **move_file** - Move or rename files/directories
- **copy_file** - Copy files or directories
- **search_files** - Search for files by pattern
- **get_recent_uploads** - View recent uploads
- **get_server_info** - Get server connection information

## Prerequisites

- Python 3.13 or higher
- A running copyparty server (see [copyparty documentation](https://github.com/9001/copyparty))

## Local Development

### Setup

Fork the repo, then run:

```bash
git clone <your-repo-url>
cd mcp-copyparty
conda create -n mcp-copyparty python=3.13
conda activate mcp-copyparty
pip install -r requirements.txt
```

### Configuration

Set environment variables to connect to your copyparty server:

```bash
export COPYPARTY_URL="http://localhost:3923"  # Your copyparty server URL
export COPYPARTY_PASSWORD="your_password"     # Optional: password for authentication
```

> **Note:** copyparty uses passwords only (no usernames by default). The username field is ignored unless the server has `--usernames` enabled.

Or create a `.env` file (not committed to git):

```
COPYPARTY_URL=http://localhost:3923
COPYPARTY_PASSWORD=your_password
```

### Test

Start the MCP server:

```bash
python src/server.py
```

Then in another terminal, test with the MCP inspector:

```bash
npx @modelcontextprotocol/inspector
```

Open http://localhost:3000 and connect to `http://localhost:8000/mcp` using "Streamable HTTP" transport (NOTE THE `/mcp`!).

## Deployment

### Environment Variables

Configure these environment variables in your deployment:

- `COPYPARTY_URL` (required) - URL of your copyparty server (e.g., `http://your-copyparty-server.com`)
- `COPYPARTY_PASSWORD` (optional) - Password for authentication (copyparty uses passwords only, no usernames)
- `ENVIRONMENT` (optional) - Set to `production` for production deployments

### Option 1: One-Click Deploy to Render

1. Click the "Deploy to Render" button above
2. Set the required environment variables in Render's dashboard
3. Deploy!

### Option 2: Manual Deployment

1. Fork this repository
2. Connect your GitHub account to Render
3. Create a new Web Service on Render
4. Connect your forked repository
5. Add the environment variables (COPYPARTY_URL, etc.)
6. Render will automatically detect the `render.yaml` configuration

Your server will be available at `https://your-service-name.onrender.com/mcp` (NOTE THE `/mcp`!)

## Usage with AI Assistants

### Connecting to Poke

You can connect your MCP server to Poke at [poke.com/settings/connections](https://poke.com/settings/connections).

To test the connection explicitly, ask poke something like: `Tell the subagent to use the "{connection name}" integration's "{tool name}" tool`.

If you run into persistent issues of poke not calling the right MCP (e.g. after you've renamed the connection) you may send `clearhistory` to poke to delete all message history and start fresh.

### Example Commands

Once connected, you can ask your AI assistant to:

- "List all files in the /music directory on copyparty"
- "Upload this text file to copyparty in the /documents folder"
- "Download the file /data/report.pdf from copyparty"
- "Create a directory called 'backups' in the root folder"
- "Search for all .mp3 files in /music"
- "Move /old/file.txt to /new/file.txt"
- "Show me recent uploads to the server"

## Tool Reference

### list_files
List files and folders in a directory.

**Parameters:**
- `path` (str, default: "/"): Directory path to list
- `include_dotfiles` (bool, default: False): Include hidden files

### download_file
Download a file from the server.

**Parameters:**
- `path` (str): File path to download
- `as_base64` (bool, default: False): Return as base64 for binary files

### upload_file
Upload a file to the server.

**Parameters:**
- `path` (str): Target directory path
- `content` (str): File content (text or base64)
- `filename` (str): Name for the file
- `is_base64` (bool, default: False): Whether content is base64-encoded
- `replace` (bool, default: False): Replace if file exists

### create_directory
Create a new directory.

**Parameters:**
- `path` (str): Parent directory path
- `name` (str): Name of new directory

### delete_file
Delete a file or directory recursively.

**Parameters:**
- `path` (str): Path to delete

### move_file
Move or rename a file/directory.

**Parameters:**
- `source_path` (str): Current path
- `destination_path` (str): New path

### copy_file
Copy a file or directory.

**Parameters:**
- `source_path` (str): Source path
- `destination_path` (str): Destination path

### search_files
Search for files by pattern.

**Parameters:**
- `path` (str, default: "/"): Directory to search
- `pattern` (str, optional): Pattern to match

### get_recent_uploads
View recent uploads.

**Parameters:**
- `filter_path` (str, optional): Filter by path pattern

### get_server_info
Get server configuration and status.

**No parameters**

## Development

### Adding More Tools

You can add more tools by decorating functions with `@mcp.tool`:

```python
@mcp.tool(description="Your tool description")
def your_tool(param: str) -> dict:
    """Tool implementation"""
    # Your code here
    return {"result": "success"}
```

### Testing Locally

Make sure you have a copyparty server running locally:

```bash
# Install copyparty
pip install copyparty

# Run a simple copyparty server
copyparty
```

This will start copyparty on http://localhost:3923 by default.

## About copyparty

[copyparty](https://github.com/9001/copyparty) is a portable file server with accelerated resumable uploads, file deduplication, WebDAV, FTP, zeroconf, media indexer, video thumbnails, audio transcoding, and plenty of other features.

## License

MIT

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
