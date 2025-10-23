# server.py
#
# Universal Python MCP Server for Gemini Skills.
# This single file provides the "List & Retrieve" toolchain for any skill.
# It makes all files within the skill's directory accessible, with standard exclusions.

from pathlib import Path
from fastmcp import FastMCP

# The root directory of the extension where this script lives.
EXT_DIR = Path(__file__).parent

# Standard files and directories to exclude from the resource list.
# The AI does not need to see its own source code or config files.
EXCLUSIONS = {
    ".git",
    ".gitignore",
    "__pycache__",
    "node_modules",
    "dist",
    "server.py",
    "requirements.txt",
    "gemini-extension.json",
    "SKILL.md",
}

mcp = FastMCP(name="SkillFileManager")

@mcp.tool
def list_skill_resources() -> list[str]:
    """
    Use this function FIRST to discover what resource files are available.
    Returns a list of all relevant file paths within the skill's directory.
    """
    resource_files = []
    # Recursively find all paths in the extension's directory.
    for path in EXT_DIR.glob('**/*'):
        # Skip if it's not a file (i.e., it's a directory).
        if not path.is_file():
            continue
        
        # Check if any part of the path is in the exclusion set.
        # This correctly handles files like 'server.py' and folders like '.git'.
        if any(part in EXCLUSIONS for part in path.parts):
            continue
            
        # Add the clean, relative path to our list.
        resource_files.append(str(path.relative_to(EXT_DIR)))
    
    return sorted(resource_files)

@mcp.tool
def get_skill_resource(resource_name: str) -> str:
    """
    Retrieves the content of a specific resource file AFTER you have discovered its name.
    
    Args:
        resource_name: The full path of the resource to retrieve, exactly as
                       provided by 'list_skill_resources'.
    """
    # --- CRITICAL SECURITY CHECK ---
    # Construct the full path and resolve it to its absolute, canonical form.
    # This prevents any directory traversal shenanigans.
    target_file = EXT_DIR.joinpath(resource_name).resolve()

    # Ensure the resolved path is safely inside the extension's root directory.
    # This is the security boundary.
    if not str(target_file).startswith(str(EXT_DIR.resolve())):
        raise PermissionError(f"Security violation: Access to '{resource_name}' is denied.")

    if not target_file.is_file():
        raise FileNotFoundError(f"Resource not found: '{resource_name}'")

    # Return the file's content, decoded as UTF-8.
    return target_file.read_text(encoding='utf-8')

if __name__ == "__main__":
    mcp.run()