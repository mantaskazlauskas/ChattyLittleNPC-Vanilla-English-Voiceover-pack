import os

def generate_lua_file(folder_path, output_file):
    """This method scans the specified folder for .ogg and .mp3 files and generates a Lua file with the paths to these files."""
    addon_name = os.path.basename(os.path.dirname(os.path.abspath(folder_path)))
    with open(output_file, 'w') as lua_file:
        lua_file.write(f"---@class {addon_name}\n")
        lua_file.write(f"local {addon_name} = LibStub(\"AceAddon-3.0\"):GetAddon(\"{addon_name}\")\n\n")
        lua_file.write(f"{addon_name}.Voiceovers = {{\n")
        for root, _, files in os.walk(folder_path):
            for file in files:
                if file.endswith('.ogg') or file.endswith('.mp3'):
                    relative_path = os.path.relpath(os.path.join(root, file), folder_path)
                    lua_file.write(f"    '{relative_path.replace(os.sep, '/')}',\n")
        lua_file.write("}\n")

# Specify the folder path and output Lua file path
folder_path = "voiceovers"
output_file = "VoiceoversList.lua"

generate_lua_file(folder_path, output_file)