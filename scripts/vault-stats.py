#!/usr/bin/env python3
"""Vault stats: note count, wikilink count, broken targets, orphans, date-prefix files."""
import re
import sys
from pathlib import Path

VAULT = Path("/Users/charuwatnaranong/Desktop/SmartEnPlus/smartenplus project")
WIKILINK_RE = re.compile(r"\[\[([^\]\n]+?)\]\]")
DATE_RE = re.compile(r"\d{4}-\d{2}-\d{2}")

def main():
    md_files = sorted(VAULT.rglob("*.md"))
    md_files = [p for p in md_files if ".git" not in p.parts and ".obsidian" not in p.parts]

    basenames = {p.stem for p in md_files}
    # account for `.original.md` files - their stem is "foo.original"
    all_stems = set()
    for p in md_files:
        if p.name.endswith(".original.md"):
            all_stems.add(p.name[:-len(".original.md")])
        else:
            all_stems.add(p.stem)

    all_targets = set()
    for p in md_files:
        text = p.read_text(encoding="utf-8", errors="ignore")
        for m in WIKILINK_RE.findall(text):
            target = m.split("|", 1)[0].split("#", 1)[0].strip().split("/", 1)[-1]
            if target:
                all_targets.add(target)

    broken = sorted(t for t in all_targets if t not in basenames and t not in all_stems)

    # orphans: basenames with 0 inbound links
    inbound = {}
    for t in all_targets:
        if t in basenames or t in all_stems:
            inbound[t] = inbound.get(t, 0) + 1
    orphans = sorted(b for b in basenames if inbound.get(b, 0) == 0)

    date_files = sorted(str(p.relative_to(VAULT)) for p in md_files if DATE_RE.search(p.name))

    print(f"notes_total: {len(md_files)}")
    print(f"unique_targets: {len(all_targets)}")
    print(f"broken_unique: {len(broken)}")
    print(f"orphans: {len(orphans)}")
    print(f"date_prefix_files: {len(date_files)}")
    if "--show-broken" in sys.argv:
        for b in broken: print(f"  BROKEN: [[{b}]]")
    if "--show-orphans" in sys.argv:
        for o in orphans: print(f"  ORPHAN: {o}")

if __name__ == "__main__":
    main()
