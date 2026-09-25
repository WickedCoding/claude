#!/usr/bin/env python3
"""Validate a HammerAI .character file: section format, lorebook syntax, and length limits.

Usage:
    validate_character.py <path/to/Name.character>
    validate_character.py --stdin --name "Name" < draft.character

Exit code 0 when valid (warnings allowed), 1 on errors, 2 on usage problems.
"""

import argparse
import re
import sys
from pathlib import Path

# Max characters per section (inclusive). None = no enforced limit.
LIMITS = {
    "Introduction": 80,
    "Personality": 4000,
    "Scenario": 1800,
    "Example dialogs": 2200,
    "First message": 1800,
    "System Prompt": None,
    "Lorebook": 10000,
    "Author Note": 2000,
    "Display Name": 200,
    "Alternate First Messages": 10000,
}
NAME_LIMIT = 100
REQUIRED = ["Introduction", "Personality", "Scenario", "Example dialogs", "First message"]
RECOMMENDED = ["System Prompt"]

HEADER_RE = re.compile(r"^--- // (.+?)\s*$")
LOOSE_HEADER_RE = re.compile(r"^-{2,}\s*/{1,2}")
DIALOG_RE = re.compile(r"^#\{\{(char|user)\}\}:")
TEMPLATE_RE = re.compile(r"\{\{\s*([^}]*?)\s*\}\}")
MAX_TERMS = 10
MIN_TERM_LEN = 4


def parse_sections(text):
    """Return (sections, errors). sections is a list of (name, content, header_line)."""
    sections, errors = [], []
    current, buf, header_line = None, [], 0
    for lineno, line in enumerate(text.splitlines(), start=1):
        m = HEADER_RE.match(line)
        if m:
            if current is not None:
                sections.append((current, "\n".join(buf).strip("\n"), header_line))
            current, buf, header_line = m.group(1), [], lineno
            continue
        if LOOSE_HEADER_RE.match(line):
            errors.append(f"Line {lineno}: malformed section header {line!r} (expected '--- // <Section Name>')")
            continue
        if current is None:
            if line.strip():
                errors.append(f"Line {lineno}: content before the first section header")
            continue
        buf.append(line)
    if current is not None:
        sections.append((current, "\n".join(buf).strip("\n"), header_line))
    return sections, errors


def check_lorebook(content):
    errors, warnings, seen = [], [], {}
    for i, line in enumerate(content.splitlines(), start=1):
        if not line.strip():
            continue
        if " | " not in line:
            if "|" not in line:
                errors.append(f"Lorebook entry {i}: missing ' | ' delimiter: {line[:60]!r}")
            elif not line.split("|", 1)[1].strip():
                errors.append(f"Lorebook entry {i}: empty description")
            else:
                errors.append(f"Lorebook entry {i}: delimiter needs spaces around the pipe (' | '): {line[:60]!r}")
            continue
        terms_part, description = line.split(" | ", 1)
        terms = [t.strip() for t in terms_part.split(",") if t.strip()]
        if not terms:
            errors.append(f"Lorebook entry {i}: no trigger terms")
        if not description.strip():
            errors.append(f"Lorebook entry {i}: empty description")
        if len(terms) > MAX_TERMS:
            warnings.append(f"Lorebook entry {i}: {len(terms)} terms (recommend max {MAX_TERMS})")
        for t in terms:
            if t != t.lower():
                warnings.append(f"Lorebook entry {i}: uppercase in term {t!r} (recommend lowercase)")
            if len(t) < MIN_TERM_LEN:
                warnings.append(
                    f"Lorebook entry {i}: short term {t!r} partial-matches inside other words (false-positive risk)"
                )
            seen.setdefault(t.lower(), []).append(i)
        if terms and description.strip() and not any(t.lower() in description.lower() for t in terms):
            warnings.append(f"Lorebook entry {i}: description echoes none of its trigger terms")
    for term, entries in seen.items():
        if len(entries) > 1:
            warnings.append(f"Lorebook term {term!r} appears in entries {entries} (verify intentional)")
    return errors, warnings


def check_dialogs(content):
    warnings = []
    for i, line in enumerate(content.splitlines(), start=1):
        if line.strip() and not DIALOG_RE.match(line):
            warnings.append(f"Example dialogs line {i}: does not start with '#{{{{user}}}}:' or '#{{{{char}}}}:'")
    return warnings


def validate(text, name):
    errors, warnings, limit_lines = [], [], []
    sections, parse_errors = parse_sections(text)
    errors.extend(parse_errors)

    name_len = len(name)
    mark = "✓" if name_len <= NAME_LIMIT else "✗"
    limit_lines.append(f"{mark} Character name (filename) {name!r}: {name_len}/{NAME_LIMIT}")
    if name_len > NAME_LIMIT:
        errors.append(f"Character name is {name_len} chars (max {NAME_LIMIT})")

    names = [s[0] for s in sections]
    for sec in set(names):
        if names.count(sec) > 1:
            errors.append(f"Section '{sec}' appears {names.count(sec)} times")

    for sec, content, line in sections:
        if sec not in LIMITS:
            warnings.append(f"Line {line}: unknown section '{sec}' (HammerAI may ignore it)")
            continue
        limit = LIMITS[sec]
        count = len(content)
        if limit is None:
            limit_lines.append(f"· {sec}: {count:,} chars (no limit)")
        elif count > limit:
            limit_lines.append(f"✗ {sec}: {count:,}/{limit:,} — over by {count - limit:,}")
            errors.append(f"{sec} exceeds limit ({count:,}/{limit:,})")
        else:
            limit_lines.append(f"✓ {sec}: {count:,}/{limit:,}")
        if not content.strip():
            warnings.append(f"Section '{sec}' is empty")
        if sec == "Lorebook":
            e, w = check_lorebook(content)
            errors.extend(e)
            warnings.extend(w)
        elif sec == "Example dialogs":
            warnings.extend(check_dialogs(content))
        for var in TEMPLATE_RE.findall(content):
            if var not in ("char", "user"):
                warnings.append(f"Section '{sec}': unknown template variable '{{{{{var}}}}}'")

    for sec in REQUIRED:
        if sec not in names:
            errors.append(f"Missing required section '{sec}'")
    for sec in RECOMMENDED:
        if sec not in names:
            warnings.append(f"Missing section '{sec}' (optional but recommended)")

    return sections, errors, warnings, limit_lines


def main():
    p = argparse.ArgumentParser(description="Validate a HammerAI .character file")
    p.add_argument("path", nargs="?", help="path to the .character file")
    p.add_argument("--stdin", action="store_true", help="read content from stdin (draft not yet written)")
    p.add_argument("--name", help="character name; required with --stdin, defaults to the filename stem")
    args = p.parse_args()

    if args.stdin:
        if not args.name:
            p.error("--name is required with --stdin")
        text, label, name = sys.stdin.read(), "<stdin>", args.name
    elif args.path:
        path = Path(args.path)
        if not path.is_file():
            print(f"Error: character file not found at {path}", file=sys.stderr)
            return 2
        text, label, name = path.read_text(encoding="utf-8"), path.name, args.name or path.stem
        if path.suffix != ".character":
            print(f"Warning: {path.name} does not have the .character extension", file=sys.stderr)
    else:
        p.error("give a path or --stdin")

    sections, errors, warnings, limit_lines = validate(text, name)

    print(f"Validation Results for {label}:")
    print(f"Sections: {', '.join(s[0] for s in sections) or '(none)'}")
    print()
    print("Character Limits:")
    for line in limit_lines:
        print(f"  {line}")
    if errors:
        print()
        for e in errors:
            print(f"✗ Error: {e}")
    if warnings:
        print()
        for w in warnings:
            print(f"⚠ Warning: {w}")
    print()
    status = "INVALID" if errors else "VALID"
    print(f"Status: {status} ({len(errors)} errors, {len(warnings)} warnings)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
