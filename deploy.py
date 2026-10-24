#!/usr/bin/env python3
"""
Deploy script for WoW addon repos.
Copies the addon folder into the selected WoW version's Interface/AddOns directory.

Adapted from the ChattyLittleNpc deploy.py. The only change is that the addon
folder is discovered by looking for a directory whose name matches a .toc file
inside it, rather than being hardcoded -- so this file is now identical across
repos and can be copied without edits.

Usage:
    python deploy.py
"""

import os
import stat
import sys
import shutil

# Maintainer's install path -- change this to wherever World of Warcraft is installed on your machine.
WOW_ROOT = r"D:\Games\World of Warcraft"

# Human-readable labels for known WoW version folders
VERSION_LABELS = {
    "_retail_":      "Retail (The War Within / Midnight)",
    "_classic_":     "Classic (Cataclysm / Mists)",
    "_classic_era_": "Classic Era (Season of Discovery)",
    "_anniversary_": "Classic Anniversary",
    "_ptr_":         "PTR (Public Test Realm)",
    "_xptr_":        "xPTR",
    "_beta_":        "Beta",
}

ADDONS_RELATIVE = os.path.join("Interface", "AddOns")


def find_addon_sources():
    """
    Return the absolute paths to the addon folders next to this script.

    An addon folder is a subdirectory containing <same-name>.toc, which is the
    layout WoW itself requires, so this cannot pick the wrong directory.
    Voiceover repos may hold one addon folder per locale.
    """
    script_dir = os.path.dirname(os.path.abspath(__file__))

    matches = []
    for entry in sorted(os.listdir(script_dir)):
        candidate = os.path.join(script_dir, entry)
        if not os.path.isdir(candidate) or entry.startswith('.'):
            continue
        if os.path.isfile(os.path.join(candidate, f"{entry}.toc")):
            matches.append(candidate)

    if not matches:
        print("ERROR: No addon folder found next to this script.")
        print("       Expected a subdirectory containing a matching .toc file,")
        print("       e.g. ChattyLittleGossipTracker/ChattyLittleGossipTracker.toc")
        sys.exit(1)

    return matches


def prompt_addons(sources):
    """When there is more than one addon folder, ask which to deploy. Returns a list."""
    if len(sources) == 1:
        return sources

    print()
    print("Available addon folders:")
    print()
    for i, source in enumerate(sources, start=1):
        print(f"  [{i}] {os.path.basename(source)}")
    print("  [a] All of the above")
    print()

    while True:
        raw = input(f"Select addon [1-{len(sources)}, a]: ").strip().lower()
        if raw == "a":
            return sources
        if raw.isdigit():
            choice = int(raw)
            if 1 <= choice <= len(sources):
                return [sources[choice - 1]]
        print(f"  Please enter a number between 1 and {len(sources)}, or 'a'.")


def discover_versions(wow_root):
    """
    Scan wow_root for version folders that contain Interface/AddOns.
    Returns a list of (folder_name, addons_path, label) sorted by folder name.
    """
    versions = []
    if not os.path.isdir(wow_root):
        print(f"ERROR: WoW root not found at: {wow_root}")
        sys.exit(1)

    for entry in sorted(os.listdir(wow_root)):
        full_path = os.path.join(wow_root, entry)
        if not os.path.isdir(full_path):
            continue
        addons_path = os.path.join(full_path, ADDONS_RELATIVE)
        if os.path.isdir(addons_path):
            label = VERSION_LABELS.get(entry, entry)
            versions.append((entry, addons_path, label))

    return versions


def prompt_version(versions):
    """Print a numbered menu and return the chosen (folder_name, addons_path, label)."""
    print()
    print("Available WoW versions:")
    print()
    for i, (folder, addons_path, label) in enumerate(versions, start=1):
        print(f"  [{i}] {label}")
        print(f"       {addons_path}")
    print()

    while True:
        raw = input(f"Select version [1-{len(versions)}]: ").strip()
        if raw.isdigit():
            choice = int(raw)
            if 1 <= choice <= len(versions):
                return versions[choice - 1]
        print(f"  Please enter a number between 1 and {len(versions)}.")


def _clear_readonly_and_retry(func, path, _exc):
    """rmtree error handler: Windows refuses to delete read-only files (e.g. .git objects)."""
    os.chmod(path, stat.S_IWRITE)
    func(path)


def remove_tree(path):
    if sys.version_info >= (3, 12):
        shutil.rmtree(path, onexc=_clear_readonly_and_retry)
    else:
        shutil.rmtree(path, onerror=_clear_readonly_and_retry)


def deploy(source_dir, addons_dir, addon_name):
    """Copy source_dir into addons_dir/<addon_name>, replacing any existing copy."""
    dest = os.path.join(addons_dir, addon_name)

    if os.path.exists(dest):
        print(f"\nRemoving existing: {dest}")
        remove_tree(dest)

    print(f"Copying: {source_dir}")
    print(f"     to: {dest}")
    shutil.copytree(source_dir, dest)
    print("\nDone.")


def main():
    source_dirs = prompt_addons(find_addon_sources())

    for source_dir in source_dirs:
        print(f"Addon source : {source_dir}")
    print(f"WoW root     : {WOW_ROOT}")

    versions = discover_versions(WOW_ROOT)
    if not versions:
        print("ERROR: No WoW version folders with Interface/AddOns found.")
        sys.exit(1)

    folder, addons_dir, label = prompt_version(versions)

    print(f"\nDeploying to: {label}  ({addons_dir})")
    confirm = input("Confirm? [y/N]: ").strip().lower()
    if confirm != "y":
        print("Aborted.")
        sys.exit(0)

    for source_dir in source_dirs:
        deploy(source_dir, addons_dir, os.path.basename(source_dir))


if __name__ == "__main__":
    main()
