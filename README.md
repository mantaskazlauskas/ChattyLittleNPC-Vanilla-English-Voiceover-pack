# ChattyLittleNPC - Vanilla English AI Voiceover Pack  
This is an AI-generated English voiceover pack designed for the ChattyLittleNPC addon, specifically tailored for World of Warcraft: Classic (Vanilla). Enhance your in-game experience with immersive AI voiceovers for NPC dialogues and interactions throughout Azeroth and beyond. Simply install this pack alongside the ChattyLittleNPC addon to bring your Classic adventures to life.
## Upgrading from 3.3.4 or earlier
The English pack folder was renamed from `ChattyLittleNpc_Vanilla_voiceovers` to `ChattyLittleNpc_Vanilla_enUS_voiceovers`. Delete the old folder from `Interface/AddOns`, otherwise both load and the old one stops getting updates.

## Locales
Each language is its own addon folder, named the way ChattyLittleNPC expects:

| Folder | Language |
|---|---|
| `ChattyLittleNpc_Vanilla_enUS_voiceovers/` | English |
| `ChattyLittleNpc_Vanilla_<locale>_voiceovers/` | that locale, e.g. `ChattyLittleNpc_Vanilla_deDE_voiceovers/` |

To add a locale, copy the English folder's `.toc` and `Main.lua` into a new folder, rename the `.toc` to match the folder, change its `## Title` (e.g. `Chatty Little NPC: Vanilla voiceovers (deDE)`) so the packs can be told apart, replace `ChattyLittleNpc_Vanilla_enUS_voiceovers` with the new folder name in `Main.lua`, and put the audio files in `voiceovers/`.

Publishing a GitHub release builds one ZIP per addon folder, e.g. `ChattyLittleNpc_Vanilla_enUS_voiceovers-v3.3.4.zip` and `ChattyLittleNpc_Vanilla_deDE_voiceovers-v3.3.4.zip`. To regenerate `VoiceoversList.lua` locally, run `python generate_voiceovers_list.py` (all folders) or pass one folder.
