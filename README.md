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

- Alcedo Studio 0.3.3 or later. Its Windows installer and macOS app contain `alcedo-cli` beside
  the Alcedo Studio program: `<install folder>\bin\alcedo-cli.exe` on Windows and
  `AlcedoStudio.app/Contents/MacOS/alcedo-cli` on macOS. The installers do not change `PATH`; the
  agent finds the program itself (also in an install folder that you chose) and calls it by its
  full path. An installed 0.3.2 gets `alcedo-cli` with the in-app update to 0.3.3
  (the update check in Settings).
- An agent that can read images and run shell commands, for example Claude Code or Codex.
- Optional: Python 3.9+ with numpy and Pillow, for `scripts/analyze_preview.py`. The agent runs
  it only when you ask for measurements.
- Optional: Python 3.9+ with Pillow, for `scripts/contact_sheet.py` (contact sheets).

## Install

The simplest way: open your agent and ask it, "Install the skill zidage/alcedo-skills". The
agent follows the steps below.

### Claude Code

```text
/plugin marketplace add zidage/alcedo-skills
/plugin install alcedo@alcedo-skills
```

To update later: `/plugin marketplace update alcedo-skills`.

### Codex

Ask Codex: `$skill-installer install https://github.com/zidage/alcedo-skills/tree/main/skills/alcedo`.
Or copy the folder `skills/alcedo` into `~/.agents/skills/alcedo`:

```bash
git clone https://github.com/zidage/alcedo-skills.git
mkdir -p ~/.agents/skills
cp -r alcedo-skills/skills/alcedo ~/.agents/skills/alcedo
```

Codex finds a new skill without a restart; if `alcedo` does not show, restart Codex.

### Other agents, or without the plugin system

Copy the folder `skills/alcedo` into the skills folder of your agent, for example
`~/.claude/skills/alcedo` for Claude Code:

```bash
git clone https://github.com/zidage/alcedo-skills.git
cp -r alcedo-skills/skills/alcedo ~/.claude/skills/alcedo
```

On Windows, `~` is your user folder (`%USERPROFILE%`). In PowerShell, use
`Copy-Item -Recurse alcedo-skills\skills\alcedo $HOME\.claude\skills\alcedo`.

### For the agent that installs this skill

When a user asks you to install this skill:

1. Install the folder `skills/alcedo` of this repository as the skill `alcedo`, in the user
   skills folder of your agent: `~/.claude/skills/alcedo` for Claude Code (or the plugin
   commands above), `~/.agents/skills/alcedo` for Codex. Copy the whole folder: `SKILL.md`,
   `references/`, and `scripts/`.
2. Find `alcedo-cli` as `skills/alcedo/references/installation.md` (Find alcedo-cli) says, and
   run `alcedo-cli --version`. It must print 0.3.3 or later. If Alcedo Studio is missing or
   older, tell the user to install or update it.
3. Tell the user that the skill is ready, and that they can ask for edits in plain words, for
   example "fix the exposure of the selected photos in Alcedo".

## Check it

Ask the agent: "Use the alcedo skill to check that alcedo-cli works." It finds `alcedo-cli`,
prints its version, runs `alcedo-cli session list`, and reports the sessions it finds. With the
Alcedo Studio window open, a session named `gui` is listed.

## Contents

| Path | Contents |
| --- | --- |
| `skills/alcedo/SKILL.md` | The instructions of the agent. |
| `skills/alcedo/references/` | The alcedo-cli documentation. |
| `skills/alcedo/scripts/analyze_preview.py` | Optional measurements of a preview PNG. |
| `skills/alcedo/scripts/contact_sheet.py` | Contact sheets of many photos for culling. |
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
