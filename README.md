# alcedo-skills

Agent skills for [Alcedo Studio](https://github.com/zidage/AlcedoStudio), the RAW photo editor.

The skill `alcedo` lets an AI agent (for example Claude Code) edit, rate, search, and export
photos through `alcedo-cli`. The agent renders a preview of each photo, looks at it, and changes
the editor values until the photo looks right. It can work headless on a project or a folder,
or in your open Alcedo Studio window, where you can take control back at any time.

What it does by default:

- **"Fix these photos":** a light, natural correction: exposure, white balance, a tilted
  horizon, and an obvious crop. No creative look.
- **Your own instructions:** "warmer and more contrast", "a moody look", "straighten the
  buildings". The agent edits, looks, and repeats until it is satisfied, and you can ask for
  more changes.
- **All photos:** the same work for every photo of a project, a folder, or your selection, with
  a short report at the end.

## Requirements

- Alcedo Studio 0.3.2 or later with `alcedo-cli` (automation protocol 1). The installers do not
  contain `alcedo-cli` yet; build it from source (see
  [Build from source](https://github.com/zidage/AlcedoStudio/blob/main/docs/build_from_source.md),
  target `alcedo-cli`) and put it on the PATH.
- An agent that can read images, so that it can look at the previews.
- Optional: Python 3.9+ with numpy and Pillow, for `scripts/analyze_preview.py`. The agent runs
  it only when you ask for measurements.

## Install

### Claude Code

```text
/plugin marketplace add zidage/alcedo-skills
/plugin install alcedo@alcedo-skills
```

To update later: `/plugin marketplace update alcedo-skills`.

### Other agents, or without the plugin system

Copy the folder `skills/alcedo` into the skills folder of your agent, for example
`~/.claude/skills/alcedo` for Claude Code:

```bash
git clone https://github.com/zidage/alcedo-skills.git
cp -r alcedo-skills/skills/alcedo ~/.claude/skills/alcedo
```

## Check it

Ask the agent: "Use the alcedo skill to check that alcedo-cli works." It runs
`alcedo-cli session list` and reports the sessions it finds. With the Alcedo Studio window open,
a session named `gui` is listed.

## Contents

| Path | Contents |
| --- | --- |
| `skills/alcedo/SKILL.md` | The instructions of the agent. |
| `skills/alcedo/references/` | The alcedo-cli documentation, copied from `docs/automation` of Alcedo Studio. |
| `skills/alcedo/scripts/analyze_preview.py` | Optional measurements of a preview PNG. |
| `scripts/sync_references.py` | Copies the documentation from an Alcedo Studio checkout and sets the version. |

## Versions

The plugin version is the Alcedo Studio version that the skill was checked with. At each Alcedo
Studio release:

```bash
python scripts/sync_references.py <AlcedoStudio checkout> --version <x.y.z>
git commit -am "Sync the references with Alcedo Studio <x.y.z>"
git tag v<x.y.z>
git push --follow-tags
```

`python scripts/sync_references.py <checkout> --check` fails when the references differ from the
checkout.
