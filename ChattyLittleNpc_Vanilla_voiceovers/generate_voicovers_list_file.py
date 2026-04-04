import os

try:
    from mutagen.oggvorbis import OggVorbis
    from mutagen.mp3 import MP3
except ImportError:
    print("Error: mutagen library is required. Install it with: pip install mutagen")
    exit(1)


def get_audio_duration(file_path):
    """Get the duration of an audio file in seconds."""
    try:
        if file_path.lower().endswith('.ogg'):
            audio = OggVorbis(file_path)
        elif file_path.lower().endswith('.mp3'):
            audio = MP3(file_path)
        else:
            return None
        return round(audio.info.length, 2)
    except Exception as e:
        print(f"Warning: Could not read duration for {file_path}: {e}")
        return None


def generate_voiceovers_lua_file(folder_path, output_file):
    """Scan the specified folder for audio files and generate a Lua file with paths and durations."""
    addon_name = os.path.basename(os.path.dirname(os.path.abspath(folder_path)))
    
    voiceovers = []
    durations = {}
    
    for root, _, files in os.walk(folder_path):
        for file in files:
            if file.endswith('.ogg') or file.endswith('.mp3'):
                file_path = os.path.join(root, file)
                relative_path = os.path.relpath(file_path, folder_path)
                # Use forward slashes for Lua compatibility
                lua_path = relative_path.replace(os.sep, '/')
                voiceovers.append(lua_path)
                
                duration = get_audio_duration(file_path)
                if duration is not None:
                    durations[lua_path] = duration
    
    # Sort for consistent output
    voiceovers.sort()
    
    with open(output_file, 'w') as lua_file:
        lua_file.write(f"---@class {addon_name}\n")
        lua_file.write(f"local {addon_name} = _G[\"{addon_name}\"]\n\n")
        
        # Write Voiceovers list
        lua_file.write(f"{addon_name}.Voiceovers = {{\n")
        for path in voiceovers:
            lua_file.write(f"    '{path}',\n")
        lua_file.write("}\n\n")
        
        # Write VoiceoverDurations dictionary
        lua_file.write(f"{addon_name}.VoiceoverDurations = {{\n")
        for path in sorted(durations.keys()):
            lua_file.write(f'    ["{path}"] = {durations[path]},\n')
        lua_file.write("}\n")
    
    print(f"Generated {output_file} with {len(voiceovers)} voiceovers and {len(durations)} durations")


# Specify the folder path and output Lua file path
folder_path = "voiceovers"
output_file = "VoiceoversList.lua"

generate_voiceovers_lua_file(folder_path, output_file)