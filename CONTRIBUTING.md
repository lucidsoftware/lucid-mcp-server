# Contributing skills

Run the commands below from the repository root. Edit skills in `skills/`, which is the source for the plugin copies. The mappings in `skills-sync.json` decide which skills are copied to `claude/skills`, `lucid/skills`, and `cursor/skills`. Do not edit those copies directly. `awesome-copilot/` is derived from `lucid/` afterward; see the last section.

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

Create a directory such as `skills/new-skill/` with a `SKILL.md`. When using the default `skills-sync.json`, the sync script detects skills absent from every target list, adds them to all three targets in the config, and copies them. `check` and `sync --dry-run` report the pending config update without writing it. If a skill should go to only some plugins, add it manually to those target lists before syncing. A custom `--config` remains explicit and is not updated automatically.

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

## Awesome-copilot plugin (`awesome-copilot/`)

`awesome-copilot/` is generated from `lucid/` for submission to awesome-copilot, which allows at most 10 keywords per plugin. Do not edit it directly. It is a full copy of `lucid/` whose `plugin.json` keeps only the **first 10** `keywords`, so list the most important tags first in `lucid/plugin.json`. Each kept keyword must be lowercase letters, numbers, and hyphens, at most 30 characters.

After changing anything in `lucid/` (including after `sync_skills.py` updates `lucid/skills`), regenerate and commit the result:

```bash
python3 scripts/sync_awesome_copilot_plugin.py sync
python3 scripts/sync_awesome_copilot_plugin.py check
```

The `Check plugin sync` GitHub workflow runs `check` on every branch and pull request and fails if `awesome-copilot/` is stale. To submit, set **Plugin path inside the repository** to `awesome-copilot` and give a release tag or full commit SHA that contains the up-to-date `awesome-copilot/` directory (awesome-copilot rejects branches).
