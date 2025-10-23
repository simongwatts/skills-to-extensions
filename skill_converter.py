# skill_converter.py
import os
import json
import shutil
import argparse
import sys
from pathlib import Path

def convert_skills(source_path, output_dir, version, suffix, universal_files):
    """
    Converts Claude skills to self-contained Gemini extensions using a Python MCP server.
    """
    if not os.path.exists(source_path):
        print(f"Error: Source path does not exist: {source_path}")
        return

    output_dir_abs = Path(output_dir).resolve()
    if not output_dir_abs.exists():
        output_dir_abs.mkdir(parents=True)

    skill_found = False
    # Use topdown=True to allow modifying the `dirs` list to prune the search.
    for root, dirs, files in os.walk(source_path, topdown=True):
        root_abs = Path(root).resolve()
        # Prune the search tree: do not descend into the output directory.
        if str(root_abs).startswith(str(output_dir_abs)):
            dirs[:] = []
            continue

        if "SKILL.md" in files:
            skill_found = True
            skill_name = os.path.basename(root)
            extension_name = f"{skill_name}{suffix}"
            extension_dir = output_dir_abs / extension_name

            if extension_dir.exists():
                print(f"Warning: Extension directory already exists, skipping: {extension_dir}")
                # Prune: Don't look for nested skills if we skipped this one.
                dirs[:] = []
                continue

            print(f"Converting skill: {skill_name} -> {extension_name}")

            # 1. Copy the entire original skill directory, preserving its structure.
            shutil.copytree(root, extension_dir)

            # 2. Add the universal server files to the new extension's root.
            for file_path in universal_files:
                shutil.copy(file_path, extension_dir)

            # 3. Create the gemini-extension.json manifest with the dynamic server name.
            server_name = f"{extension_name}-skill-server"
            manifest = {
                "name": extension_name,
                "version": version,
                "contextFileName": "SKILL.md",
                "mcpServers": {
                    server_name: {
                        "command": "python",
                        "args": ["${extensionPath}${/}server.py"],
                        "cwd": "${extensionPath}"
                    }
                }
            }
            
            manifest_path = extension_dir / "gemini-extension.json"
            with open(manifest_path, "w") as f:
                json.dump(manifest, f, indent=2)
                
            # We found and converted a skill, so don't look for skills nested inside it.
            dirs[:] = []

    if not skill_found:
        print("No valid skills (directories containing SKILL.md) found in the source directory.")

def main():
    parser = argparse.ArgumentParser(description="Convert Claude skills to Gemini extensions.")
    parser.add_argument("source_path", help="Path to the directory containing Claude skills or a single skill directory.")
    parser.add_argument("-o", "--output", default="./converted_skills", help="Directory where the generated extensions will be saved.")
    parser.add_argument("--version", default="1.0.0", help="Version to use in the gemini-extension.json files.")
    parser.add_argument("--suffix", default="-ext", help="Suffix to append to the original skill name for the new extension name.")
    args = parser.parse_args()

    # --- Setup Universal Files ---
    try:
        # Find the directory where this converter script lives.
        script_dir = Path(__file__).parent
    except NameError:
        # Fallback for interactive environments where __file__ is not defined.
        script_dir = Path.cwd()
    
    # Define the required universal files.
    server_py_path = script_dir / "server.py"
    requirements_txt_content = "fastmcp\n"
    requirements_txt_path = script_dir / "requirements.txt"

    # Create a temporary requirements.txt file for the conversion process.
    with open(requirements_txt_path, "w") as f:
        f.write(requirements_txt_content)

    universal_files = [server_py_path, requirements_txt_path]

    # Verify that all required universal files exist.
    for file_path in universal_files:
        if not file_path.exists():
            print(f"Error: Required universal file not found: {file_path}")
            print("Please ensure 'server.py' is in the same folder as this converter script.")
            # Clean up the temporary file before exiting.
            if requirements_txt_path.exists():
                os.remove(requirements_txt_path)
            sys.exit(1)

    convert_skills(args.source_path, args.output, args.version, args.suffix, universal_files)
    
    # Clean up the temporary requirements.txt file.
    if requirements_txt_path.exists():
        os.remove(requirements_txt_path)

    print(f"\nConversion complete. Extensions are in: {Path(args.output).resolve()}")
    print("NOTE: Users of these extensions will need Python and the 'fastmcp' library installed.")

if __name__ == "__main__":
    main()