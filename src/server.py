#!/usr/bin/env python3
import os
import json
from typing import Optional, List, Dict, Any
from fastmcp import FastMCP
import requests
from urllib.parse import urljoin, quote

mcp = FastMCP("copyparty MCP Server")

# Environment variable for the copyparty server URL
# Users should set this to their copyparty server address
COPYPARTY_URL = os.environ.get("COPYPARTY_URL", "http://localhost:3923")
COPYPARTY_USERNAME = os.environ.get("COPYPARTY_USERNAME", "")
COPYPARTY_PASSWORD = os.environ.get("COPYPARTY_PASSWORD", "")


def _get_auth():
    """Get authentication credentials if configured."""
    if COPYPARTY_USERNAME and COPYPARTY_PASSWORD:
        return (COPYPARTY_USERNAME, COPYPARTY_PASSWORD)
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


@mcp.tool(description="List files and folders in a directory on the copyparty server. Returns JSON with file information including names, sizes, and timestamps.")
def list_files(path: str = "/", include_dotfiles: bool = False) -> Dict[str, Any]:
    """
    List files and folders at the specified path.
    
    Args:
        path: Directory path to list (default: "/")
        include_dotfiles: Include hidden files starting with dot (default: False)
    
    Returns:
        Dictionary containing file and folder information
    """
    params = {"ls": ""}
    if include_dotfiles:
        params["dots"] = ""
    
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
        import base64
        result["content"] = base64.b64encode(response.content).decode('utf-8')
        result["encoding"] = "base64"
    else:
        try:
            result["content"] = response.text
            result["encoding"] = "text"
        except UnicodeDecodeError:
            import base64
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
        import base64
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


@mcp.tool(description="Search for files on the copyparty server by listing directory contents and filtering. Useful for finding specific files or directories.")
def search_files(path: str = "/", pattern: Optional[str] = None) -> Dict[str, Any]:
    """
    Search for files matching a pattern in the given path.
    
    Args:
        path: Directory path to search in
        pattern: Optional pattern to filter files (substring match on filename)
    
    Returns:
        Dictionary with matching files
    """
    params = {"ls": ""}
    response = _make_request("GET", path, params=params)
    data = response.json()
    
    if pattern and "files" in data:
        # Filter files by pattern
        filtered_files = [f for f in data["files"] if pattern.lower() in f["name"].lower()]
        data["files"] = filtered_files
        data["filtered"] = True
        data["pattern"] = pattern
    
    return data


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
        "python_version": os.sys.version.split()[0],
        "copyparty_url": COPYPARTY_URL,
        "copyparty_status": copyparty_status,
        "copyparty_accessible": copyparty_accessible,
        "authentication_configured": bool(COPYPARTY_USERNAME and COPYPARTY_PASSWORD)
    }


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    host = "0.0.0.0"
    
    print(f"Starting copyparty FastMCP server on {host}:{port}")
    print(f"Connecting to copyparty server at: {COPYPARTY_URL}")
    if COPYPARTY_USERNAME:
        print(f"Authentication: Configured for user '{COPYPARTY_USERNAME}'")
    else:
        print("Authentication: Not configured (using anonymous access)")
    
    mcp.run(
        transport="http",
        host=host,
        port=port,
        stateless_http=True
    )
