#!/usr/bin/env python3
"""Sync skill folders from the root /skills source of truth into plugin directories.

Config file (default: skills-sync.json at repo root) shape:

    {
      "source": "skills",
      "targets": [
        { "path": "claude/skills", "skills": ["lucid"],
          "manifest": "claude/.claude-plugin/plugin.json" },
        { "path": "cursor/skills", "skills": ["lucid"],
          "manifest": "cursor/.cursor-plugin/plugin.json" }
      ]
    }

Usage:
    python scripts/sync_skills.py sync [--dry-run] [--prune] [--bump-version] [--target PATH] [--skill NAME] [-v]
    python scripts/sync_skills.py check [--target PATH] [--skill NAME] [-v]
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import sys
from dataclasses import dataclass, field
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


@dataclass
class Target:
    path: Path
    skills: list[str]
    manifest: Path | None = None


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


@dataclass
class PlannedSkill:
    name: str
    diff: SkillDiff


@dataclass
class TargetPlan:
    target: Target
    skills: list[PlannedSkill]
    stale: list[str]
    version_before: str | None = None
    version_after: str | None = None
    manifest_content: bytes | None = None


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
        targets.append(
            Target(
                path=REPO_ROOT / entry["path"],
                skills=list(entry["skills"]),
                manifest=REPO_ROOT / entry["manifest"] if entry.get("manifest") else None,
            )
        )
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


def prepare_version_update(manifest: Path, level: str) -> tuple[str, str, bytes]:
    try:
        content = manifest.read_bytes().decode("utf-8")
        data = json.loads(content)
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ConfigError(f"cannot read valid JSON manifest '{manifest}': {exc}") from exc

    old = data.get("version") if isinstance(data, dict) else None
    if not isinstance(old, str) or not re.fullmatch(r"[0-9]+\.[0-9]+\.[0-9]+", old):
        raise ConfigError(f"manifest '{manifest}' needs a numeric MAJOR.MINOR.PATCH version")

    matches = list(re.finditer(r'^[ \t]*"version"[ \t]*:[ \t]*"([^"\n]+)"', content, re.MULTILINE))
    if len(matches) != 1 or matches[0].group(1) != old:
        raise ConfigError(f"cannot safely update version field in '{manifest}'")

    major, minor, patch = map(int, old.split("."))
    new = f"{major}.{minor + 1}.0" if level == "minor" else f"{major}.{minor}.{patch + 1}"
    match = matches[0]
    updated = content[: match.start(1)] + new + content[match.end(1) :]
    return old, new, updated.encode("utf-8")


def run(
    config: Config,
    *,
    check: bool,
    dry_run: bool,
    prune: bool,
    bump_version: bool,
    only_targets: list[str] | None,
    only_skills: list[str] | None,
    verbose: bool,
) -> int:
    drift_found = False
    error_found = False
    plans: list[TargetPlan] = []

    for target in config.targets:
        target_rel = str(target.path.relative_to(REPO_ROOT))
        if only_targets and target_rel not in only_targets:
            continue

        skill_names = [s for s in target.skills if not only_skills or s in only_skills]
        plan = TargetPlan(target=target, skills=[], stale=[])
        bump_level: str | None = None

        if bump_version and target.manifest is None:
            print(f"ERROR: target '{target_rel}' has no manifest in the config", file=sys.stderr)
            error_found = True

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

            is_new_to_target = not _relative_files(dest_dir)
            diff = diff_skill(source_dir, dest_dir)
            plan.skills.append(PlannedSkill(skill_name, diff))
            if not diff.is_empty:
                drift_found = True
                if is_new_to_target:
                    bump_level = "minor"
                elif bump_level is None:
                    bump_level = "patch"

        # A --skill filter must not make other configured skills appear stale.
        plan.stale = [
            name
            for name in find_stale_skill_dirs(target.path, target.skills)
            if not only_skills or name in only_skills
        ]
        if plan.stale:
            drift_found = True
            if prune and bump_level is None:
                bump_level = "patch"

        if bump_version and target.manifest is not None:
            try:
                before, after, content = prepare_version_update(target.manifest, bump_level or "patch")
                if bump_level:
                    plan.version_before, plan.version_after, plan.manifest_content = before, after, content
            except ConfigError as exc:
                print(f"ERROR: {exc}", file=sys.stderr)
                error_found = True

        plans.append(plan)

    if error_found:
        return 2

    for plan in plans:
        target = plan.target
        target_rel = str(target.path.relative_to(REPO_ROOT))
        for skill in plan.skills:
            diff = skill.diff
            if diff.is_empty:
                if verbose:
                    print(f"[ok] {target_rel}/{skill.name}")
                continue

            print(
                f"[{'drift' if check or dry_run else 'sync'}] {target_rel}/{skill.name}: "
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
                apply_diff(diff, config.source / skill.name, target.path / skill.name, verbose)

        for stale_name in plan.stale:
            if prune and not check:
                if dry_run:
                    print(f"[prune] would remove stale skill '{stale_name}' from {target_rel}")
                else:
                    shutil.rmtree(target.path / stale_name)
                    print(f"[prune] removed stale skill '{stale_name}' from {target_rel}")
            else:
                print(
                    f"WARNING: stale skill folder '{stale_name}' in {target_rel} is not "
                    f"in its configured skills list. Re-run with --prune to remove it."
                )

        if plan.version_after is not None:
            assert target.manifest is not None and plan.manifest_content is not None
            print(
                f"[version] {target.manifest.relative_to(REPO_ROOT)}: "
                f"{plan.version_before} -> {plan.version_after}"
                + (" (dry run)" if dry_run else "")
            )
            if not dry_run:
                target.manifest.write_bytes(plan.manifest_content)

    if check and drift_found:
        return 1
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("mode", choices=["sync", "check"], help="sync: write updates. check: verify only, no writes")
    parser.add_argument("--config", type=Path, default=REPO_ROOT / "skills-sync.json")
    parser.add_argument("--dry-run", action="store_true", help="print planned actions without writing (sync mode only)")
    parser.add_argument("--prune", action="store_true", help="delete stale skill folders no longer in a target's config")
    parser.add_argument("--bump-version", action="store_true", help="bump versions of plugins whose skills change (sync mode only)")
    parser.add_argument("--target", action="append", dest="targets", help="restrict to this target path (repeatable)")
    parser.add_argument("--skill", action="append", dest="skills", help="restrict to this skill name (repeatable)")
    parser.add_argument("-v", "--verbose", action="store_true")
    args = parser.parse_args(argv)

    if args.mode == "check" and args.bump_version:
        parser.error("--bump-version is only valid with sync")

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
        bump_version=args.bump_version,
        only_targets=args.targets,
        only_skills=args.skills,
        verbose=args.verbose,
    )


if __name__ == "__main__":
    sys.exit(main())
