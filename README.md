# alcedo-skills

Agent skills for [Alcedo Studio](https://github.com/zidage/AlcedoStudio), the RAW photo editor.

The skill `alcedo` lets an AI agent (for example Claude Code) edit, rate, search, and export
photos through `alcedo-cli`. The agent renders a preview of each photo, looks at it, and changes
the editor values until the photo looks right. It can work headless on a project or a folder,
or in your open Alcedo Studio window, where you can stop it at any time. To let it continue,
tell the agent; there is nothing to select in the window.

What it does by default:

- **"Fix these photos":** a light, natural correction: exposure, white balance, a tilted
  horizon, and an obvious crop. No creative look.
- **Your own instructions:** "warmer and more contrast", "a moody look", "straighten the
  buildings". The agent edits, looks, and repeats until it is satisfied, and you can ask for
  more changes.
- **All photos:** the same work for every photo of a project, a folder, or your selection, with
  a short report at the end.
- **Cull a shoot:** contact sheets of hundreds of photos with the file name, capture time, and
  exposure of each, and optional detail crops for a sharpness check, so the agent can pick and
  rate the best frames.

## Requirements

- Alcedo Studio 0.3.2 or later with `alcedo-cli` (automation protocol 1). The installers do not
  contain `alcedo-cli` yet; build it from source (see
  [Build from source](https://github.com/zidage/AlcedoStudio/blob/main/docs/build_from_source.md),
  target `alcedo-cli`) and put it on the PATH.
- An agent that can read images, so that it can look at the previews.
- Optional: Python 3.9+ with numpy and Pillow, for `scripts/analyze_preview.py`. The agent runs
  it only when you ask for measurements.
- Optional: Python 3.9+ with Pillow, for `scripts/contact_sheet.py` (contact sheets), and an
  `alcedo-cli` with the `batch` command and `library.info` and `library.thumbnails`.

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
| `skills/alcedo/references/` | The alcedo-cli documentation. |
| `skills/alcedo/scripts/analyze_preview.py` | Optional measurements of a preview PNG. |
| `scripts/set_version.py` | Sets the plugin version. |

## The alcedo-cli documentation

`skills/alcedo/references/` is the only copy of the alcedo-cli documentation. Alcedo Studio
links this repository from its README and does not pin a commit of it. To check the reference
against an Alcedo Studio build, give the build a local checkout of this repository:

- Configure Alcedo Studio with `-DALCEDO_SKILLS_DIR=<this checkout>`. Then
  `AutomationReferenceDocsTest` compares `references/reference/commands.json` and
  `editor_catalog.json` with the command schemas of the build.
- `scripts/automation/generate_cli_reference.py --skills-dir <this checkout>` of Alcedo Studio
  writes the generated parts of the pages in `references/reference/`.

A change to the automation commands therefore has two pull requests: one in this repository
(the documentation), and one in Alcedo Studio (the code). Links to other files of Alcedo Studio
are full GitHub links, because the skill does not contain those files.

## Versions

The plugin version is the Alcedo Studio version that the skill was checked with. At each Alcedo
Studio release, check the reference against the release build (see above), then:

```bash
python scripts/set_version.py <x.y.z>
git commit -am "Set the version to Alcedo Studio <x.y.z>"
git tag v<x.y.z>
git push --follow-tags
```

The `main` branch can describe commands that are newer than the last release. They are in the
next release, and `alcedo-cli` built from the `main` branch of Alcedo Studio has them.

## License

MIT. See [LICENSE](LICENSE).
