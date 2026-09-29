# Contributing skills

Run the commands below from the repository root. Edit skills in `skills/`, which is the source for the plugin copies. The mappings in `skills-sync.json` decide which skills are copied to `claude/skills`, `lucid/skills`, and `cursor/skills`. Do not edit those copies directly.

## Update an existing skill

For example, after editing `skills/lucid/SKILL.md`:

```bash
python3 scripts/sync_skills.py sync --dry-run --bump-version -v
python3 scripts/sync_skills.py sync --bump-version
python3 scripts/sync_skills.py check
```

`sync --dry-run` previews added, changed, and deleted files without writing them. With `--bump-version`, it also previews version changes. `sync` copies the source skill to its configured targets. `check` verifies that the copies match; it exits with status 1 if it finds drift.

With `--bump-version`, the script increases the **patch** version of every plugin that receives an existing skill update. For example, it changes `1.0.0` to `1.0.1`. The current plugin manifests are:

| Plugin | Version file |
| --- | --- |
| Claude | `claude/.claude-plugin/plugin.json` |
| Agent-Plugin | `lucid/plugin.json` |
| Cursor | `cursor/.cursor-plugin/plugin.json` |

## Add a new skill

Create a directory such as `skills/new-skill/` with a `SKILL.md`, then add `"new-skill"` to the `skills` list for each intended target in `skills-sync.json`. For example, to distribute it to Claude and Cursor, add it to the entries for `claude/skills` and `cursor/skills`.

```bash
python3 scripts/sync_skills.py sync --dry-run --bump-version --skill new-skill -v
python3 scripts/sync_skills.py sync --bump-version --skill new-skill
python3 scripts/sync_skills.py check
```

With `--bump-version`, the script increases the **minor** version of each plugin that receives the new skill and resets its patch number. For example, it changes `1.0.1` to `1.1.0` in the Claude and Cursor manifests for the example above. It updates the Agent-Plugin manifest too if `lucid/skills` is also a target. A skill added to a plugin for the first time counts as new for that plugin.

## Useful options

Use `--target` with a path from `skills-sync.json` to preview or sync one target. You can repeat `--target` or `--skill` to select several.

```bash
python3 scripts/sync_skills.py sync --dry-run --bump-version --target cursor/skills -v
python3 scripts/sync_skills.py sync --bump-version --target cursor/skills
python3 scripts/sync_skills.py check --target cursor/skills
```

If you intentionally remove a skill from a target's configuration, `sync` warns about its leftover directory. Review the removal, then run `python3 scripts/sync_skills.py sync --prune --bump-version` to delete stale skill directories and bump the affected plugin's patch version. The flag bumps each affected plugin once per sync, even if several skills change; a new skill takes precedence over existing skill edits. It does not bump versions when nothing changes, and it cannot recover a bump for files already synced without the flag. Run `python3 scripts/sync_skills.py check` after syncing and include the updated source skill, copied skills, configuration (if changed), and affected plugin manifests in your change.
