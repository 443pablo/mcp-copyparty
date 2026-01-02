#!/usr/bin/env python3
import os
import sys
import base64
import json
from typing import Optional, Dict, Any, List
from fastmcp import FastMCP
import requests
from urllib.parse import urljoin

mcp = FastMCP("copyparty MCP Server")

# Environment variable for the copyparty server URL
# Users should set this to their copyparty server address
COPYPARTY_URL = os.environ.get("COPYPARTY_URL", "http://localhost:3923")
COPYPARTY_PASSWORD = os.environ.get("COPYPARTY_PASSWORD", "")


def _get_auth():
    """Get authentication credentials if configured.
    
    Note: copyparty ignores usernames by default and only uses passwords.
    We send an empty username with the password for basic auth.
    """
    if COPYPARTY_PASSWORD:
        return ("", COPYPARTY_PASSWORD)
    return None


def _make_request(method: str, path: str, **kwargs) -> requests.Response:
    """Make a request to the copyparty server."""
    url = urljoin(COPYPARTY_URL, path)
    auth = _get_auth()
    if auth:
        kwargs['auth'] = auth
    
    response = requests.request(method, url, **kwargs)
    response.raise_for_status()
    return response


@mcp.tool(description="List files and folders in a directory on the copyparty server. Returns JSON with file information including names, sizes, timestamps, and metadata/tags if available.")
def list_files(path: str = "/", include_dotfiles: bool = False, include_tags: bool = False) -> Dict[str, Any]:
    """
    List files and folders at the specified path.
    
    Args:
        path: Directory path to list (default: "/")
        include_dotfiles: Include hidden files starting with dot (default: False)
        include_tags: Include file metadata/tags in the response (default: False)
    
    Returns:
        Dictionary containing file and folder information, with tags if requested
    """
    params = {"ls": ""}
    if include_dotfiles:
        params["dots"] = ""
    if include_tags:
        params["tags"] = ""
    
    response = _make_request("GET", path, params=params)
    return response.json()


@mcp.tool(description="Download a file from the copyparty server. Returns the file content as base64-encoded string for binary files or as text for text files.")
def download_file(path: str, as_base64: bool = False) -> Dict[str, Any]:
    """
    Download a file from the copyparty server.
    
    Args:
        path: File path to download
        as_base64: Return content as base64-encoded string (useful for binary files)
    
    Returns:
        Dictionary with file content and metadata
    """
    response = _make_request("GET", path)
    
    result = {
        "path": path,
        "content_type": response.headers.get("Content-Type", "application/octet-stream"),
        "size": len(response.content)
    }
    
    if as_base64:
        result["content"] = base64.b64encode(response.content).decode('utf-8')
        result["encoding"] = "base64"
    else:
        try:
            result["content"] = response.text
            result["encoding"] = "text"
        except UnicodeDecodeError:
            result["content"] = base64.b64encode(response.content).decode('utf-8')
            result["encoding"] = "base64"
    
    return result


@mcp.tool(description="Upload a file to the copyparty server. Supports uploading text content or base64-encoded binary data to a specified path.")
def upload_file(path: str, content: str, filename: str, is_base64: bool = False, replace: bool = False) -> Dict[str, Any]:
    """
    Upload a file to the copyparty server.
    
    Args:
        path: Directory path where the file should be uploaded
        content: File content (text or base64-encoded)
        filename: Name of the file to create
        is_base64: Whether content is base64-encoded
        replace: Whether to replace the file if it exists
    
    Returns:
        Dictionary with upload result information
    """
    if is_base64:
        file_data = base64.b64decode(content)
    else:
        file_data = content.encode('utf-8')
    
    params = {"j": ""}  # Return JSON response
    if replace:
        params["replace"] = ""
    
    files = {"f": (filename, file_data)}
    response = _make_request("POST", path, params=params, files=files)
    
    return response.json()


@mcp.tool(description="Create a new directory on the copyparty server at the specified path.")
def create_directory(path: str, name: str) -> Dict[str, Any]:
    """
    Create a new directory on the copyparty server.
    
    Args:
        path: Parent directory path
        name: Name of the new directory
    
    Returns:
        Dictionary with creation result
    """
    data = {"act": "mkdir", "name": name}
    response = _make_request("POST", path, data=data)
    
    return {
        "success": True,
        "path": path,
        "directory": name,
        "message": f"Directory '{name}' created successfully at {path}"
    }


@mcp.tool(description="Delete a file or directory recursively from the copyparty server. Use with caution as this operation cannot be undone.")
def delete_file(path: str) -> Dict[str, Any]:
    """
    Delete a file or directory from the copyparty server.
    
    Args:
        path: Path to the file or directory to delete
    
    Returns:
        Dictionary with deletion result
    """
    params = {"delete": ""}
    response = _make_request("POST", path, params=params)
    
    return {
        "success": True,
        "path": path,
        "message": f"Successfully deleted {path}"
    }


@mcp.tool(description="Move or rename a file or directory on the copyparty server from one path to another.")
def move_file(source_path: str, destination_path: str) -> Dict[str, Any]:
    """
    Move or rename a file or directory.
    
    Args:
        source_path: Current path of the file/directory
        destination_path: New path for the file/directory
    
    Returns:
        Dictionary with move result
    """
    params = {"move": destination_path}
    response = _make_request("POST", source_path, params=params)
    
    return {
        "success": True,
        "source": source_path,
        "destination": destination_path,
        "message": f"Successfully moved {source_path} to {destination_path}"
    }


@mcp.tool(description="Copy a file or directory on the copyparty server from one path to another, creating a duplicate.")
def copy_file(source_path: str, destination_path: str) -> Dict[str, Any]:
    """
    Copy a file or directory.
    
    Args:
        source_path: Path of the file/directory to copy
        destination_path: Destination path for the copy
    
    Returns:
        Dictionary with copy result
    """
    params = {"copy": destination_path}
    response = _make_request("POST", source_path, params=params)
    
    return {
        "success": True,
        "source": source_path,
        "destination": destination_path,
        "message": f"Successfully copied {source_path} to {destination_path}"
    }


@mcp.tool(description="Get information about recent uploads to the copyparty server, optionally filtered by path pattern.")
def get_recent_uploads(filter_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Get recent uploads from your IP or all recent uploads (if admin).
    
    Args:
        filter_path: Optional path filter to only show uploads matching this pattern
    
    Returns:
        Dictionary with recent upload information
    """
    params = {"ups": ""}
    if filter_path:
        params["filter"] = filter_path
    
    response = _make_request("GET", "/", params=params)
    
    return {
        "success": True,
        "uploads": response.text
    }


@mcp.tool(description="Search for files on the copyparty server using server-wide search. Supports advanced search syntax including file content search, metadata queries, and more. Much more powerful than simple pattern matching.")
def search_files(query: str, path: str = "/") -> Dict[str, Any]:
    """
    Search for files server-wide using advanced search syntax.
    
    Args:
        query: Search query. Supports various operators:
            - Simple text: searches filenames and content
            - "quoted text": exact phrase match
            - -word: exclude files containing word
            - tag:value: search by metadata tag
            - ext:mp3: search by file extension
            - size>1M: files larger than 1MB
            - date>2023-01-01: files modified after date
        path: Optional path to limit search scope (default: "/")
    
    Returns:
        Dictionary with search results
    """
    # Use JSON POST for server-wide search
    search_data = {"q": query}
    if path != "/":
        search_data["v"] = path
    
    response = _make_request("POST", "/", params={"j": ""}, json=search_data)
    return response.json()


@mcp.tool(description="Get file metadata and tags (audio metadata like artist, album, title, etc.) for a specific file on the copyparty server. Requires the copyparty server to have metadata indexing enabled with -e2ts flag.")
def get_file_metadata(path: str) -> Dict[str, Any]:
    """
    Get metadata/tags for a file (especially useful for audio files with ID3 tags, etc.).
    
    Args:
        path: File path to get metadata for
    
    Returns:
        Dictionary with file metadata including tags like artist, album, title, duration, etc.
    """
    # Request file listing with metadata by adding ?tags parameter
    # The parent directory is needed to get the file info from the listing
    dir_path = os.path.dirname(path) or "/"
    filename = os.path.basename(path)
    
    # Get directory listing with tags
    params = {"ls": "", "tags": ""}
    response = _make_request("GET", dir_path, params=params)
    data = response.json()
    
    # Find the specific file in the listing
    if "files" in data:
        for file_info in data["files"]:
            if file_info.get("name") == filename:
                result = {
                    "success": True,
                    "path": path,
                    "name": filename,
                    "size": file_info.get("sz"),
                    "modified": file_info.get("ts"),
                }
                
                # Include all tags if present
                if "tags" in file_info:
                    result["tags"] = file_info["tags"]
                
                # Also include raw file info for any additional metadata
                result["raw_metadata"] = file_info
                
                return result
    
    # If file not found or no metadata available
    return {
        "success": False,
        "path": path,
        "error": "File not found or metadata not available",
        "note": "Ensure the copyparty server has metadata indexing enabled with -e2ts flag"
    }


@mcp.tool(description="Create a temporary shareable URL for a file or folder on the copyparty server. The share can have an expiration time and custom permissions.")
def create_share(path: str, expiration_minutes: Optional[int] = None, read_only: bool = True) -> Dict[str, Any]:
    """
    Create a temporary share URL for a file or folder.
    
    Args:
        path: Path to the file or folder to share
        expiration_minutes: Minutes until share expires (None for no expiration)
        read_only: Whether the share is read-only (default: True)
    
    Returns:
        Dictionary with share URL and information
    """
    share_data = {
        "v": path,
        "rd": 1 if read_only else 0
    }
    
    if expiration_minutes:
        share_data["life"] = expiration_minutes
    
    response = _make_request("POST", path, params={"share": ""}, json=share_data)
    result = response.json()
    
    # Construct full share URL
    if "url" in result:
        share_url = urljoin(COPYPARTY_URL, result["url"])
        result["full_url"] = share_url
    
    return result


@mcp.tool(description="List all shared files and folders on the copyparty server that you have access to.")
def list_shares() -> Dict[str, Any]:
    """
    List all your shared files and folders.
    
    Returns:
        Dictionary with list of active shares
    """
    response = _make_request("GET", "/", params={"shares": ""})
    
    # Try to parse as JSON, fallback to text
    try:
        return response.json()
    except (ValueError, json.JSONDecodeError):
        return {
            "success": True,
            "shares": response.text
        }


@mcp.tool(description="Update the expiration time of an existing share on the copyparty server.")
def update_share_expiration(path: str, expiration_minutes: int) -> Dict[str, Any]:
    """
    Update the expiration time of a shared file or folder.
    
    Args:
        path: Path to the shared file or folder
        expiration_minutes: New expiration time in minutes
    
    Returns:
        Dictionary with update result
    """
    params = {"eshare": str(expiration_minutes)}
    response = _make_request("POST", path, params=params)
    
    return {
        "success": True,
        "path": path,
        "expiration_minutes": expiration_minutes,
        "message": f"Share expiration updated to {expiration_minutes} minutes"
    }


@mcp.tool(description="Delete/stop sharing a file or folder on the copyparty server.")
def delete_share(path: str) -> Dict[str, Any]:
    """
    Stop sharing a file or folder.
    
    Args:
        path: Path to the shared file or folder
    
    Returns:
        Dictionary with deletion result
    """
    params = {"eshare": "rm"}
    response = _make_request("POST", path, params=params)
    
    return {
        "success": True,
        "path": path,
        "message": f"Share removed for {path}"
    }


@mcp.tool(description="Download a folder and its contents as a tar archive from the copyparty server. Supports various compression formats.")
def download_as_tar(path: str, compression: Optional[str] = None, level: int = 1) -> Dict[str, Any]:
    """
    Download folder contents as a tar archive.
    
    Args:
        path: Path to the folder to download
        compression: Compression type: None (no compression), 'gz' (gzip), 'xz' (xz)
        level: Compression level 1-9 (default: 1)
    
    Returns:
        Dictionary with download information and base64-encoded tar file
    """
    params = {}
    if compression:
        params["tar"] = f"{compression}:{level}"
    else:
        params["tar"] = ""
    
    response = _make_request("GET", path, params=params)
    
    return {
        "success": True,
        "path": path,
        "compression": compression or "none",
        "content": base64.b64encode(response.content).decode('utf-8'),
        "encoding": "base64",
        "size": len(response.content),
        "content_type": response.headers.get("Content-Type", "application/x-tar")
    }


@mcp.tool(description="Download a folder and its contents as a zip archive from the copyparty server. Supports compatibility modes for older systems.")
def download_as_zip(path: str, compatibility: Optional[str] = None) -> Dict[str, Any]:
    """
    Download folder contents as a zip archive.
    
    Args:
        path: Path to the folder to download
        compatibility: Compatibility mode: None (modern), 'dos' (WinXP), 'crc' (MSDOS)
    
    Returns:
        Dictionary with download information and base64-encoded zip file
    """
    params = {}
    if compatibility:
        params["zip"] = compatibility
    else:
        params["zip"] = ""
    
    response = _make_request("GET", path, params=params)
    
    return {
        "success": True,
        "path": path,
        "compatibility": compatibility or "modern",
        "content": base64.b64encode(response.content).decode('utf-8'),
        "encoding": "base64",
        "size": len(response.content),
        "content_type": response.headers.get("Content-Type", "application/zip")
    }


@mcp.tool(description="Stream a growing file from the copyparty server, useful for log files or files being written. Supports starting from a specific position.")
def tail_file(path: str, start_byte: Optional[int] = None) -> Dict[str, Any]:
    """
    Continuously stream a growing file (like tail -f).
    
    Args:
        path: Path to the file to tail
        start_byte: Starting byte position (None for beginning, negative for bytes from end)
    
    Returns:
        Dictionary with file content from the specified position
    """
    params = {}
    if start_byte is not None:
        params["tail"] = str(start_byte)
    else:
        params["tail"] = ""
    
    response = _make_request("GET", path, params=params)
    
    return {
        "success": True,
        "path": path,
        "start_byte": start_byte,
        "content": response.text,
        "size": len(response.content),
        "note": "This is a snapshot. For continuous streaming, call again or use WebSocket"
    }


@mcp.tool(description="Get a thumbnail for an image/video or transcode audio file on the copyparty server.")
def get_thumbnail(path: str, format: Optional[str] = None) -> Dict[str, Any]:
    """
    Get a thumbnail for media files or transcode audio.
    
    Args:
        path: Path to the media file
        format: Format for audio transcoding: 'opus' (128kbps opus), 'caf' (iOS format), or None for image/video thumbnail
    
    Returns:
        Dictionary with thumbnail/transcoded content as base64
    """
    params = {}
    if format:
        params["th"] = format
    else:
        params["th"] = ""
    
    response = _make_request("GET", path, params=params)
    
    return {
        "success": True,
        "path": path,
        "format": format or "thumbnail",
        "content": base64.b64encode(response.content).decode('utf-8'),
        "encoding": "base64",
        "size": len(response.content),
        "content_type": response.headers.get("Content-Type", "image/jpeg")
    }


@mcp.tool(description="Download a file as text with specific character encoding from the copyparty server.")
def download_file_as_text(path: str, charset: str = "utf-8") -> Dict[str, Any]:
    """
    Get file content as text with specific character encoding.
    
    Args:
        path: Path to the file
        charset: Character encoding (default: utf-8, can be iso-8859-1, etc.)
    
    Returns:
        Dictionary with file content as text
    """
    params = {}
    if charset != "utf-8":
        params["txt"] = charset
    else:
        params["txt"] = ""
    
    response = _make_request("GET", path, params=params)
    
    return {
        "success": True,
        "path": path,
        "charset": charset,
        "content": response.text,
        "size": len(response.content)
    }


@mcp.tool(description="Render a markdown file as HTML or open media files in the viewer on the copyparty server.")
def render_markdown(path: str) -> Dict[str, Any]:
    """
    Render a markdown file or open media in viewer.
    
    Args:
        path: Path to the markdown file or media file
    
    Returns:
        Dictionary with rendered content or viewer URL
    """
    params = {"v": ""}
    response = _make_request("GET", path, params=params)
    
    return {
        "success": True,
        "path": path,
        "content": response.text,
        "content_type": response.headers.get("Content-Type", "text/html")
    }


@mcp.tool(description="Delete multiple files or folders at once on the copyparty server using a single request.")
def delete_multiple_files(paths: List[str]) -> Dict[str, Any]:
    """
    Delete multiple files or folders in a single operation.
    
    Args:
        paths: List of paths to delete
    
    Returns:
        Dictionary with deletion results
    """
    response = _make_request("POST", "/", params={"delete": ""}, json=paths)
    
    return {
        "success": True,
        "deleted_paths": paths,
        "count": len(paths),
        "message": f"Successfully deleted {len(paths)} items"
    }


@mcp.tool(description="Show active downloads on the copyparty server (admin only). Useful for monitoring server activity.")
def get_active_downloads() -> Dict[str, Any]:
    """
    Get list of active downloads (requires admin permissions).
    
    Returns:
        Dictionary with active download information
    """
    response = _make_request("GET", "/", params={"dls": ""})
    
    try:
        return response.json()
    except (ValueError, json.JSONDecodeError):
        return {
            "success": True,
            "downloads": response.text
        }


@mcp.tool(description="Show all recent uploads on the copyparty server (admin only), optionally filtered by path pattern.")
def get_all_recent_uploads(filter_path: Optional[str] = None, as_json: bool = False) -> Dict[str, Any]:
    """
    Get all recent uploads from all users (requires admin permissions).
    
    Args:
        filter_path: Optional path filter to only show uploads matching this pattern
        as_json: Return as JSON format (default: False)
    
    Returns:
        Dictionary with recent upload information
    """
    params = {"ru": ""}
    if filter_path:
        params["filter"] = filter_path
    if as_json:
        params["j"] = ""
    
    response = _make_request("GET", "/", params=params)
    
    try:
        return response.json()
    except (ValueError, json.JSONDecodeError):
        return {
            "success": True,
            "uploads": response.text
        }


@mcp.tool(description="Get information about the copyparty MCP server configuration including the copyparty URL and connection status.")
def get_server_info() -> Dict[str, Any]:
    """
    Get information about the MCP server and copyparty connection.
    
    Returns:
        Dictionary with server information
    """
    # Try to check if copyparty server is accessible
    try:
        response = requests.get(COPYPARTY_URL, timeout=5)
        copyparty_status = "connected"
        copyparty_accessible = True
    except Exception as e:
        copyparty_status = f"error: {str(e)}"
        copyparty_accessible = False
    
    return {
        "mcp_server_name": "copyparty MCP Server",
        "version": "1.0.0",
        "environment": os.environ.get("ENVIRONMENT", "development"),
        "python_version": sys.version.split()[0],
        "copyparty_url": COPYPARTY_URL,
        "copyparty_status": copyparty_status,
        "copyparty_accessible": copyparty_accessible,
        "authentication_configured": bool(COPYPARTY_PASSWORD)
    }


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    host = "0.0.0.0"
    
    print(f"Starting copyparty FastMCP server on {host}:{port}")
    print(f"Connecting to copyparty server at: {COPYPARTY_URL}")
    if COPYPARTY_PASSWORD:
        print("Authentication: Password configured")
    else:
        print("Authentication: Not configured (using anonymous access)")
    
    mcp.run(
        transport="http",
        host=host,
        port=port,
        stateless_http=True
    )
