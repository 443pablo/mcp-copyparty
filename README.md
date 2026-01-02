# MCP Server for copyparty

A [FastMCP](https://github.com/jlowin/fastmcp) server for interacting with [copyparty](https://github.com/9001/copyparty) file servers via the Model Context Protocol. This server enables AI assistants and other MCP clients to manage files on copyparty servers.

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/443pablo/mcp-copyparty)

## Features

This MCP server provides the following tools for interacting with copyparty:

### File Management
- **list_files** - List files and folders in a directory (with optional metadata/tags)
- **get_file_metadata** - Get file metadata and tags (audio metadata, etc.)
- **download_file** - Download files from the server
- **upload_file** - Upload files to the server
- **create_directory** - Create new directories
- **delete_file** - Delete files or directories
- **delete_multiple_files** - Delete multiple files at once
- **move_file** - Move or rename files/directories
- **copy_file** - Copy files or directories

### Search & Discovery
- **search_files** - Server-wide search with advanced query syntax
- **get_recent_uploads** - View recent uploads from your IP
- **get_all_recent_uploads** - View all recent uploads (admin only)

### File Sharing
- **create_share** - Create temporary shareable URLs for files/folders
- **list_shares** - List all your shared files/folders
- **update_share_expiration** - Update share expiration time
- **delete_share** - Stop sharing a file/folder

### Archive Downloads
- **download_as_tar** - Download folders as tar/tar.gz/tar.xz archives
- **download_as_zip** - Download folders as zip archives

### Advanced File Operations
- **tail_file** - Stream growing files (logs, etc.)
- **get_thumbnail** - Get thumbnails or transcode audio
- **download_file_as_text** - Download with specific charset encoding
- **render_markdown** - Render markdown files or open media viewer

### Monitoring
- **get_active_downloads** - Show active downloads (admin only)
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
- "Get the metadata for the file /music/song.mp3 on copyparty"
- "Show me all audio files with their tags in /music"
- "Upload this text file to copyparty in the /documents folder"
- "Download the file /data/report.pdf from copyparty"
- "Create a directory called 'backups' in the root folder"
- "Search for all .mp3 files containing 'blues' in the server"
- "Move /old/file.txt to /new/file.txt"
- "Show me recent uploads to the server"
- "Create a shareable link for /documents/report.pdf that expires in 60 minutes"
- "Download the /music folder as a tar.gz archive"
- "Get a thumbnail for /photos/sunset.jpg"
- "Show me the last 100 lines of /logs/server.log"

## Tool Reference

### File Management Tools

#### list_files
List files and folders in a directory.

**Parameters:**
- `path` (str, default: "/"): Directory path to list
- `include_dotfiles` (bool, default: False): Include hidden files
- `include_tags` (bool, default: False): Include file metadata/tags (requires copyparty server with `-e2ts` flag)

#### get_file_metadata
Get file metadata and tags (audio metadata like artist, album, title, etc.).

**Parameters:**
- `path` (str): File path to get metadata for

**Returns:**
- Dictionary with file metadata including tags like artist, album, title, duration, and more

**Note:** Requires the copyparty server to have metadata indexing enabled with the `-e2ts` flag. See [copyparty documentation](https://github.com/9001/copyparty#metadata-from-audio-files) for details.

#### download_file
Download a file from the server.

**Parameters:**
- `path` (str): File path to download
- `as_base64` (bool, default: False): Return as base64 for binary files

#### upload_file
Upload a file to the server.

**Parameters:**
- `path` (str): Target directory path
- `content` (str): File content (text or base64)
- `filename` (str): Name for the file
- `is_base64` (bool, default: False): Whether content is base64-encoded
- `replace` (bool, default: False): Replace if file exists

#### create_directory
Create a new directory.

**Parameters:**
- `path` (str): Parent directory path
- `name` (str): Name of new directory

#### delete_file
Delete a file or directory recursively.

**Parameters:**
- `path` (str): Path to delete

#### delete_multiple_files
Delete multiple files or folders at once.

**Parameters:**
- `paths` (List[str]): List of paths to delete

#### move_file
Move or rename a file/directory.

**Parameters:**
- `source_path` (str): Current path
- `destination_path` (str): New path

#### copy_file
Copy a file or directory.

**Parameters:**
- `source_path` (str): Source path
- `destination_path` (str): Destination path

### Search & Discovery Tools

#### search_files
Server-wide search with advanced query syntax.

**Parameters:**
- `query` (str): Search query with operators:
  - Simple text: searches filenames and content
  - `"quoted text"`: exact phrase match
  - `-word`: exclude files containing word
  - `tag:value`: search by metadata tag
  - `ext:mp3`: search by file extension
  - `size>1M`: files larger than 1MB
  - `date>2023-01-01`: files modified after date
- `path` (str, default: "/"): Optional path to limit search scope

#### get_recent_uploads
View recent uploads from your IP.

**Parameters:**
- `filter_path` (str, optional): Filter by path pattern

#### get_all_recent_uploads
View all recent uploads (admin only).

**Parameters:**
- `filter_path` (str, optional): Filter by path pattern
- `as_json` (bool, default: False): Return as JSON format

### File Sharing Tools

#### create_share
Create a temporary shareable URL for a file or folder.

**Parameters:**
- `path` (str): Path to share
- `expiration_minutes` (int, optional): Minutes until expiration
- `read_only` (bool, default: True): Whether share is read-only

#### list_shares
List all your shared files and folders.

**No parameters**

#### update_share_expiration
Update the expiration time of an existing share.

**Parameters:**
- `path` (str): Path to the shared file/folder
- `expiration_minutes` (int): New expiration time in minutes

#### delete_share
Stop sharing a file or folder.

**Parameters:**
- `path` (str): Path to stop sharing

### Archive Download Tools

#### download_as_tar
Download folder contents as a tar archive.

**Parameters:**
- `path` (str): Path to the folder
- `compression` (str, optional): Compression type: None, 'gz' (gzip), 'xz'
- `level` (int, default: 1): Compression level 1-9

#### download_as_zip
Download folder contents as a zip archive.

**Parameters:**
- `path` (str): Path to the folder
- `compatibility` (str, optional): Compatibility mode: None, 'dos' (WinXP), 'crc' (MSDOS)

### Advanced File Operations

#### tail_file
Stream a growing file (like tail -f).

**Parameters:**
- `path` (str): Path to the file
- `start_byte` (int, optional): Starting byte position (negative for bytes from end)

#### get_thumbnail
Get thumbnail for media or transcode audio.

**Parameters:**
- `path` (str): Path to the media file
- `format` (str, optional): For audio: 'opus' (128kbps), 'caf' (iOS), or None for image/video thumbnail

#### download_file_as_text
Download file with specific character encoding.

**Parameters:**
- `path` (str): Path to the file
- `charset` (str, default: "utf-8"): Character encoding (e.g., 'iso-8859-1')

#### render_markdown
Render markdown file or open media viewer.

**Parameters:**
- `path` (str): Path to markdown or media file

### Monitoring Tools

#### get_active_downloads
Show active downloads (admin only).

**No parameters**

#### get_server_info
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
