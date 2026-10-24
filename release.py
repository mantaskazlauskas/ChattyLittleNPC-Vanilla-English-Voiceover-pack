#!/usr/bin/env python3
"""
Release script for ChattyLittleNpc projects.
Reads version from .toc file, creates git tag, and creates GitHub release.

Usage:
    python release.py                          # Dry run - shows what would happen
    python release.py --create                 # Create a release tag (default: release)
    python release.py --create --type beta     # Create a beta tag (e.g. v1.0.0-beta)
    python release.py --create --type alpha    # Create an alpha tag (e.g. v1.0.0-alpha)
"""

import os
import re
import subprocess
import sys
import argparse


# Locale packs are named <Addon>_<locale>_voiceovers (e.g. _enUS_, _deDE_); a pack without
# a suffix is also English (legacy naming).
LOCALE_PACK_RE = re.compile(r'_([a-z]{2}[A-Z]{2})_voiceovers$')


def find_toc_files():
    """Find .toc files in the current directory or its immediate subdirectories."""
    # First check current directory
    tocs = [file for file in sorted(os.listdir('.')) if file.endswith('.toc')]
    if tocs:
        return tocs

    # Check immediate subdirectories (for repo root)
    for item in sorted(os.listdir('.')):
        if os.path.isdir(item) and not item.startswith('.'):
            for file in sorted(os.listdir(item)):
                if file.endswith('.toc'):
                    tocs.append(os.path.join(item, file))

    return tocs


def pick_primary_toc(toc_paths):
    """The release version comes from the English pack; fall back to the first .toc."""
    for toc_path in toc_paths:
        match = LOCALE_PACK_RE.search(get_addon_name_from_toc(toc_path))
        if not match or match.group(1) == 'enUS':
            return toc_path
    return toc_paths[0] if toc_paths else None


def get_version_from_toc(toc_path):
    """Extract version from .toc file."""
    with open(toc_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    match = re.search(r'^## Version:\s*(.+)$', content, re.MULTILINE)
    if match:
        return match.group(1).strip()
    return None


def get_addon_name_from_toc(toc_path):
    """Extract addon name from .toc filename."""
    return os.path.splitext(os.path.basename(toc_path))[0]


def run_command(cmd, check=True, capture=False):
    """Run a shell command."""
    print(f"  Running: {' '.join(cmd)}")
    if capture:
        result = subprocess.run(cmd, check=check, capture_output=True, text=True)
        return result.stdout.strip()
    else:
        subprocess.run(cmd, check=check)
        return None


def check_gh_cli():
    """Check if GitHub CLI is installed and authenticated."""
    try:
        subprocess.run(['gh', '--version'], capture_output=True, check=True)
        subprocess.run(['gh', 'auth', 'status'], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def tag_exists(tag_name):
    """Check if a tag already exists."""
    result = subprocess.run(['git', 'tag', '-l', tag_name], capture_output=True, text=True)
    return tag_name in result.stdout


def main():
    parser = argparse.ArgumentParser(description='Create release from .toc version')
    parser.add_argument('--create', action='store_true', help='Actually create tag and release (default is dry run)')
    parser.add_argument('--force', action='store_true', help='Delete existing tag if it exists')
    parser.add_argument('--tag-prefix', default='v', help='Prefix for tag name (default: v)')
    parser.add_argument('--type', dest='release_type', choices=['release', 'beta', 'alpha'], default='release',
                        help='Release type: release (default), beta, or alpha. Appends -beta/-alpha suffix to tag.')
    args = parser.parse_args()

    # Find .toc files (one per locale pack)
    toc_paths = find_toc_files()
    toc_path = pick_primary_toc(toc_paths)
    if not toc_path:
        print("Error: No .toc file found in current directory or subdirectories")
        sys.exit(1)

    for path in toc_paths:
        print(f"Found .toc file: {path} (version {get_version_from_toc(path)})")
    print(f"Release version taken from: {toc_path}")

    # Get version
    version = get_version_from_toc(toc_path)
    if not version:
        print("Error: Could not find ## Version in .toc file")
        sys.exit(1)
    
    addon_name = get_addon_name_from_toc(toc_path)
    tag_suffix = f"-{args.release_type}" if args.release_type != 'release' else ''
    tag_name = f"{args.tag_prefix}{version}{tag_suffix}"
    
    print(f"Addon: {addon_name}")
    print(f"Version: {version}")
    print(f"Tag: {tag_name}")
    print(f"Release type: {args.release_type}")
    print()

    mismatched = [path for path in toc_paths if get_version_from_toc(path) != version]
    if mismatched:
        print("Warning: these packs have a different ## Version and will still be built under this tag:")
        for path in mismatched:
            print(f"  {path}: {get_version_from_toc(path)}")
        print()

    # Check prerequisites
    if not check_gh_cli():
        print("Error: GitHub CLI (gh) is not installed or not authenticated")
        print("Install: https://cli.github.com/")
        print("Authenticate: gh auth login")
        sys.exit(1)

    # Check if tag exists
    if tag_exists(tag_name):
        if args.force:
            print(f"Tag {tag_name} exists - will delete and recreate")
            if args.create:
                run_command(['git', 'tag', '-d', tag_name])
                run_command(['git', 'push', 'origin', '--delete', tag_name], check=False)
        else:
            print(f"Error: Tag {tag_name} already exists. Use --force to delete and recreate.")
            sys.exit(1)

    if not args.create:
        print("DRY RUN - use --create to actually create tag and release")
        print()
        print("Would run:")
        print(f"  git tag {tag_name}")
        print(f"  git push origin {tag_name}")
        prerelease_flag = " --prerelease" if args.release_type != 'release' else ""
        print(f"  gh release create {tag_name} --title \"{addon_name} {version}\" --generate-notes{prerelease_flag}")
        return

    # Create and push tag
    print()
    print("Creating tag...")
    run_command(['git', 'tag', tag_name])
    
    print("Pushing tag...")
    run_command(['git', 'push', 'origin', tag_name])
    
    print("Creating GitHub release...")
    gh_cmd = [
        'gh', 'release', 'create', tag_name,
        '--title', f"{addon_name} {version}",
        '--generate-notes'
    ]
    if args.release_type != 'release':
        gh_cmd.append('--prerelease')
    run_command(gh_cmd)
    
    print()
    print(f"Done! Release {tag_name} created.")
    print("The GitHub Actions workflow will now build and attach one addon ZIP per locale.")


if __name__ == '__main__':
    main()
