#!/usr/bin/env python3
"""Sync skill folders from the root /skills source of truth into plugin directories.

Config file (default: skills-sync.json at repo root) shape:

    {
      "source": "skills",
      "targets": [
        { "path": "claude/skills", "skills": ["lucid"] },
        { "path": "cursor/skills", "skills": ["lucid"] }
      ]
    }

Usage:
    python scripts/sync_skills.py sync [--dry-run] [--prune] [--target PATH] [--skill NAME] [-v]
    python scripts/sync_skills.py check [--target PATH] [--skill NAME] [-v]
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from dataclasses import dataclass, field
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


@dataclass
class Target:
    path: Path
    skills: list[str]


@dataclass
class Config:
    source: Path
    targets: list[Target]


@dataclass
class SkillDiff:
    add: list[str] = field(default_factory=list)
    modify: list[str] = field(default_factory=list)
    delete: list[str] = field(default_factory=list)

    @property
    def is_empty(self) -> bool:
        return not (self.add or self.modify or self.delete)


class ConfigError(Exception):
    pass


def load_config(config_path: Path) -> Config:
    try:
        raw = json.loads(config_path.read_text())
    except FileNotFoundError as exc:
        raise ConfigError(f"config file not found: {config_path}") from exc
    except json.JSONDecodeError as exc:
        raise ConfigError(f"invalid JSON in {config_path}: {exc}") from exc

    if "source" not in raw or "targets" not in raw:
        raise ConfigError(f"{config_path} must define 'source' and 'targets'")

    source = REPO_ROOT / raw["source"]
    targets = []
    for entry in raw["targets"]:
        if "path" not in entry or "skills" not in entry:
            raise ConfigError(f"each target must define 'path' and 'skills': {entry}")
        targets.append(Target(path=REPO_ROOT / entry["path"], skills=list(entry["skills"])))
    return Config(source=source, targets=targets)


def _file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _relative_files(root: Path) -> set[str]:
    if not root.exists():
        return set()
    return {str(p.relative_to(root)) for p in root.rglob("*") if p.is_file()}


def diff_skill(source_dir: Path, dest_dir: Path) -> SkillDiff:
    source_files = _relative_files(source_dir)
    dest_files = _relative_files(dest_dir)

    diff = SkillDiff()
    for rel in sorted(source_files - dest_files):
        diff.add.append(rel)
    for rel in sorted(dest_files - source_files):
        diff.delete.append(rel)
    for rel in sorted(source_files & dest_files):
        if _file_hash(source_dir / rel) != _file_hash(dest_dir / rel):
            diff.modify.append(rel)
    return diff


def apply_diff(diff: SkillDiff, source_dir: Path, dest_dir: Path, verbose: bool) -> None:
    for rel in diff.add + diff.modify:
        src_file = source_dir / rel
        dst_file = dest_dir / rel
        dst_file.parent.mkdir(parents=True, exist_ok=True)
        dst_file.write_bytes(src_file.read_bytes())
        if verbose:
            action = "add" if rel in diff.add else "modify"
            print(f"    {action}: {dst_file.relative_to(REPO_ROOT)}")

    for rel in diff.delete:
        dst_file = dest_dir / rel
        dst_file.unlink(missing_ok=True)
        if verbose:
            print(f"    delete: {dst_file.relative_to(REPO_ROOT)}")

    # Clean up now-empty directories left behind by deletions.
    if dest_dir.exists():
        for d in sorted(dest_dir.rglob("*"), key=lambda p: len(p.parts), reverse=True):
            if d.is_dir() and not any(d.iterdir()):
                d.rmdir()


def find_stale_skill_dirs(target_path: Path, configured_skill_names: list[str]) -> list[str]:
    if not target_path.exists():
        return []
    configured = set(configured_skill_names)
    return sorted(
        p.name for p in target_path.iterdir() if p.is_dir() and p.name not in configured
    )


def run(
    config: Config,
    *,
    check: bool,
    dry_run: bool,
    prune: bool,
    only_targets: list[str] | None,
    only_skills: list[str] | None,
    verbose: bool,
) -> int:
    drift_found = False
    error_found = False

    for target in config.targets:
        target_rel = str(target.path.relative_to(REPO_ROOT))
        if only_targets and target_rel not in only_targets:
            continue

        skill_names = [s for s in target.skills if not only_skills or s in only_skills]

        for skill_name in skill_names:
            source_dir = config.source / skill_name
            dest_dir = target.path / skill_name

            if not source_dir.exists():
                print(
                    f"ERROR: skill '{skill_name}' referenced by target '{target_rel}' "
                    f"not found in source '{config.source.relative_to(REPO_ROOT)}'",
                    file=sys.stderr,
                )
                error_found = True
                continue

            diff = diff_skill(source_dir, dest_dir)
            if diff.is_empty:
                if verbose:
                    print(f"[ok] {target_rel}/{skill_name}")
                continue

            drift_found = True
            print(
                f"[{'drift' if check or dry_run else 'sync'}] {target_rel}/{skill_name}: "
                f"+{len(diff.add)} ~{len(diff.modify)} -{len(diff.delete)}"
            )
            if verbose:
                for rel in diff.add:
                    print(f"    add: {rel}")
                for rel in diff.modify:
                    print(f"    modify: {rel}")
                for rel in diff.delete:
                    print(f"    delete: {rel}")

            if not check and not dry_run:
                apply_diff(diff, source_dir, dest_dir, verbose)

        stale = find_stale_skill_dirs(target.path, skill_names)
        for stale_name in stale:
            drift_found = True
            stale_dir = target.path / stale_name
            if prune and not check and not dry_run:
                import shutil

                shutil.rmtree(stale_dir)
                print(f"[prune] removed stale skill '{stale_name}' from {target_rel}")
            else:
                print(
                    f"WARNING: stale skill folder '{stale_name}' in {target_rel} is not "
                    f"in its configured skills list. Re-run with --prune to remove it."
                )

    if error_found:
        return 2
    if check and drift_found:
        return 1
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("mode", choices=["sync", "check"], help="sync: write updates. check: verify only, no writes")
    parser.add_argument("--config", type=Path, default=REPO_ROOT / "skills-sync.json")
    parser.add_argument("--dry-run", action="store_true", help="print planned actions without writing (sync mode only)")
    parser.add_argument("--prune", action="store_true", help="delete stale skill folders no longer in a target's config")
    parser.add_argument("--target", action="append", dest="targets", help="restrict to this target path (repeatable)")
    parser.add_argument("--skill", action="append", dest="skills", help="restrict to this skill name (repeatable)")
    parser.add_argument("-v", "--verbose", action="store_true")
    args = parser.parse_args(argv)

    try:
        config = load_config(args.config)
    except ConfigError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    return run(
        config,
        check=args.mode == "check",
        dry_run=args.dry_run,
        prune=args.prune,
        only_targets=args.targets,
        only_skills=args.skills,
        verbose=args.verbose,
    )


if __name__ == "__main__":
    sys.exit(main())
