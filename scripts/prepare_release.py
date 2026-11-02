#!/usr/bin/env python3
"""Check release versions and extract the matching CHANGELOG section."""
import argparse
import ast
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]


def source_version(path):
    for statement in ast.parse(path.read_text(encoding="utf-8")).body:
        if isinstance(statement, ast.Assign) and any(
                isinstance(target, ast.Name) and target.id == "VERSION" for target in statement.targets):
            return ast.literal_eval(statement.value)
    raise ValueError("Missing VERSION: " + str(path))


def prepare_notes(root, tag):
    if not re.fullmatch(r"v\d+\.\d+\.\d+", tag):
        raise ValueError("Expected a version tag such as v0.2.0.")
    version = tag[1:]
    versions = [source_version(root / "scripts/xcoze_search.py"),
                source_version(root / "scripts/build_release.py")]
    frontmatter = (root / "SKILL.md").read_text(encoding="utf-8").split("---", 2)[1]
    match = re.search(r'^\s+version:\s*[\"\']?([0-9]+\.[0-9]+\.[0-9]+)[\"\']?\s*$', frontmatter, re.MULTILINE)
    if not match:
        raise ValueError("Missing Skill metadata version.")
    versions.append(match[1])
    if any(value != version for value in versions):
        raise ValueError("Tag, runtime, Skill metadata and package versions must match.")
    changelog = (root / "CHANGELOG.md").read_text(encoding="utf-8")
    heading = re.search(r"^## " + re.escape(tag) + r" — \d{4}-\d{2}-\d{2}\s*$", changelog, re.MULTILINE)
    if not heading:
        raise ValueError("Missing dated CHANGELOG section for " + tag)
    remainder = changelog[heading.end():]
    section = re.split(r"^## ", remainder, maxsplit=1, flags=re.MULTILINE)[0].strip()
    if not section:
        raise ValueError("Release notes must not be empty.")
    return "# xcoze search " + tag + "\n\n" + section + "\n"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tag", help="Expected Git tag; defaults to the runtime version for local checks")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    try:
        tag = args.tag or "v" + source_version(ROOT / "scripts/xcoze_search.py")
        notes = prepare_notes(ROOT, tag)
    except (ValueError, IndexError, OSError, SyntaxError) as error:
        parser.exit(1, "Release check failed: " + str(error) + "\n")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(notes, encoding="utf-8")
    print("Release versions and CHANGELOG verified: " + tag)


if __name__ == "__main__":
    main()
