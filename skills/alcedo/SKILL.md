---
name: alcedo
description: Edit, rate, search, and export RAW photos in Alcedo Studio through alcedo-cli. Use when the user asks to retouch, fix, adjust, grade, straighten, crop, rate, find, or export photos in Alcedo Studio or an .alcd project, to work in their open Alcedo Studio window, or to batch-process a folder of RAW files with Alcedo.
---

# Alcedo Studio with alcedo-cli

`alcedo-cli` sends JSON-RPC commands to Alcedo Studio. You look at the photos yourself: render a
preview, open the PNG, judge it, and change the editor values until it looks right.

The full documentation is in `references/` (Alcedo Studio checks out the same pages at
`docs/alcedo-skills`). Read the page before you use a command group for the first time:

| Need | Page |
| --- | --- |
| Find `alcedo-cli`, check the setup, shell quoting | `references/installation.md` |
| Sessions, agent control, tasks, history, Versions | `references/concepts.md` |
| Global options, exit codes, error codes | `references/cli.md` |
| Complete examples (import, edit loop, Versions, export, search, GUI) | `references/workflows.md` |
| Parameters, result, and errors of a command | `references/reference/<group>.md` |
| What each editor field does, its range, its direction | `references/reference/editor_fields.md` |
| Find a LUT of the user's LUT library and apply it | `references/reference/lut.md` |
| Known limits | `references/limits.md` |

## Before you start

1. Find the program: `alcedo-cli --help` on the PATH. If it is not there, see
   `references/installation.md` (the packages do not contain it yet; it is built from source),
   and ask the user where it is.
2. Run `alcedo-cli session list`. A live session named `gui` is the user's open Alcedo Studio
   window.
3. Choose the session:
   - The user talks about their open window, the selected photo, or "in Alcedo": use `--session
     gui` and take agent control (below).
   - Batch work on a folder or a project file without the window: start a headless session with
     `alcedo-cli --session <name> session start --headless --project <file.alcd>` (or
     `--create <folder>,<name>`). Without `--session` the session is named `default`.
   - Not clear: ask the user.
4. Run `alcedo-cli --json call session.describe` once if you need the exact schema of a command.
   It lists `protocol_version` (this skill is for protocol 1).

## Serve the user's request

Your goal is the result that the user asked for. Meet the request as fully as you can:

- You may use every command and every editor field that alcedo-cli gives: the tone and color
  fields, the color grade, curves, HLS, color wheels, LUTs, the display transform, crop and
  rotation, grain, halation, diffusion, clarity, and sharpening.
- Any LUT of the library is allowed, with or without a print stock. Ignore the
  `display_requirement` of a LUT and its print or display transform: choose a LUT by how the
  photo looks with it in the current display transform.
- When the user asks for a creative, stylized, striking, or "impressive" result, give a
  strong, finished look. Do not hold back to a safe, natural correction. Combine a LUT with
  per-photo tone work, color grading, and finishing (grain, halation, diffusion, clarity) until
  the photos look intentional and distinctive.
- Adjust each photo to its own content and light. A shared look is a starting point, not one
  set of values for every photo.
- When a request is not clear, make the strongest reasonable choice, show the result, and offer
  the alternatives that you tried.

The rules below protect the user's data. They do not limit the look.

## Rules

- Give `--json` to every command and read the exit code: 0 success, 1 command error (read
  `error.code` and `error.data.reason`), 2 no such session, 3 connection lost, 4 usage error.
- Long commands return a task id (`import-1`, `export-1`, `bgtask-1`). Wait with `tasks.wait`
  before you read their results.
- Edit the active Version of the photo. Do not create or branch Versions unless the user asks.
- Read the current values with `editor.get` before you change a field. Values are UI values;
  out-of-range values are rejected, not clamped.
- Do not delete photos, remove Versions, or close a project without saving unless the user asked
  for it in this conversation.
- Ask before an export when the user did not name the folder and the format.
- The JSON parameters are one argument. Quote them for your shell as
  `references/installation.md` (Shell quoting) shows; Windows PowerShell 5.1 needs `\"`.

## The GUI session (the user's window)

- Call `control.acquire` with `{"holder_name":"<your name>"}` before any command that changes
  state, and `control.release` when you are done, also after an error.
- `-32004` means the user clicked **Stop**. Stop at once, tell the user, and wait until they tell
  you to continue. Only then call `control.acquire` again. Never acquire or retry on your own.
- `-32005` from `control.acquire` means another agent holds control: tell the user.
- Work on the photo the user selected: `library.selection.get`, or the photo that the editor has
  open (`editor.get` returns its `element_id`).
- Never run `session stop` or `session.shutdown` on `gui`: it closes the application.
- In a headless session you started, run `tasks.wait '{"idle":true}'` and `session stop` at the
  end.

## Look at a photo

```bash
alcedo-cli --json call render.preview '{"out_dir":"<tmp dir>","compare":"none","long_edge":1024,"file_stem":"p<element_id>-<step>"}'
```

Open the `current.path` file of the result with your image reading tool and look at it. Use
`"compare":"root"` to also get the photo as imported, and `region` (`x`, `y`, `w`, `h` in 0 to 1)
to look at a detail. Write previews to a temporary folder, not next to the user's photos.

## Default retouch: a light, natural correction

When the user asks to "fix", "retouch", or "improve" photos without saying how, make a light
correction that keeps the photo's character:

- **Exposure:** the subject is too dark or too bright, or the highlights are blown. Change
  `exposure` in steps of about 0.3 to 0.5 EV; a change under 0.2 EV is hard to see in a
  preview. Use `highlights`, `shadows`, `white`, and
  `black` only when exposure alone cannot fix it.
- **White balance:** whites and greys have a visible color cast that the light of the scene does
  not explain. Change `color_temp` (`kelvin` about 200 to 400 K at a time, `tint` about 3 to 5).
  Keep the warmth of a sunset, the blue of dusk, and the mood of fog.
- **Level and composition:** a horizon or building lines are visibly tilted. Set
  `crop_rotate.angle_degrees` (positive turns the image clockwise). Crop only to remove an
  obvious distraction at the edge, or when the composition is clearly off; keep the original
  aspect ratio.

This light correction is only for a request that names no look. Do not add a creative look
(strong contrast, saturation, grading, LUTs, film grain, vignettes) in a default retouch. When
the photo already looks good, leave it and say so. When the user asks for a style, a mood, a
film look, or something creative, follow "Serve the user's request" instead. The default look of
a photo without edits is exposure +1.5, contrast 15, saturation 30: change from those values.

## Edit loop

1. `editor.open` the photo, `editor.get` the fields you may change, render a preview, and look.
2. Decide the next change. For a user request ("warmer", "more contrast", "a moody look"), find
   the fields in `references/reference/editor_fields.md` or with `editor.catalog`.
3. Apply it with `editor.set` or `editor.batch_set`. Give a `note` that says what and why, for
   example `"note":"agent: lift exposure, subject underexposed"`. The note shows in the history
   and, in the GUI session, in the activity of the agent task.
4. Render a new preview and look again. Compare it with the previous preview. When you cannot
   see a difference, the change was small: do not test with an extreme value; take a larger
   step or render with `"compare":"root"`.
5. Repeat until the photo looks right to you. When a change made it worse, `editor.undo`.
   After about six rounds on one photo, stop and show the user what you have.
6. `editor.close` (or open the next photo) saves the edits.

Tell the user what you changed in plain words (for example "exposure +0.3 EV, 300 K warmer,
leveled by 1.5 degrees"). When the user wants a different result, continue the loop from the
current state.

## LUTs

When the user asks for a LUT or a film look, list the LUT library with `lut.list` (`query`,
`category` `film_simulation`, `package`). Give the `editor_value` of the LUT to `editor.set` on
`lut` as is, and add `strength` (0 to 1) for a weaker look. To change only the strength of the
current LUT, write the `lut` value from `editor.get` back with a new `strength`. Do not search
the disk for `.cube` files or read `lut-inventory.json`.

Every LUT is allowed: negative-only LUTs and LUTs with a print stock (`print_option`). Ignore
`display_requirement`; judge each LUT by how the photo looks in the current display transform.
Print LUTs usually give denser skies and more finished color than negative-only LUTs. To choose a
look, apply several candidates to a few different photos of the set, render each with a
different `file_stem`, and compare them side by side. Then fit exposure, highlights, and shadows
to each photo under the chosen LUT.

## All photos

When the user asks to process every photo (of a project, a folder, or a selection):

1. List them with `library.list` (pages of 100; use `offset`) or `library.selection.get`.
2. Do the edit loop for each photo. Photos of the same scene usually need similar changes: start
   from the values of the previous photo, then check the preview.
3. Report a short list: photo, what changed, and the photos you left unchanged or could not fix.
4. Export only when the user asked for it (`export.run`, then `tasks.wait`, then
   `export.status`).

## Measurements (only on request)

Do not measure photos by default; judge them by looking. When the user asks for numbers (for
example the brightness or the color cast of a series), run:

```bash
python "${CLAUDE_SKILL_DIR}/scripts/analyze_preview.py" <preview.png> [--json]
```

It needs Python 3.9+ with numpy and Pillow. It reports L* percentiles and clipping, the color of
the most neutral pixels with a reliability, and the tilt of the strongest straight lines
(counterclockwise positive; add it to `angle_degrees` to level). The numbers describe the image,
not whether it looks good.

## Errors you will meet

| Code | Meaning | What to do |
| --- | --- | --- |
| -32602 | A parameter is wrong; `data.pointer` names it | Fix the value (see the reference page). |
| -32001 | Not ready: no project or no photo open | Open the project or the photo first. |
| -32002 | Rejected now, for example `Adjustments require an interactive image` | Read `state` from `editor.get`; open the photo or wait for loading. |
| -32003 | GUI: no agent control | `control.acquire`. |
| -32004 | GUI: the user stopped the agent | Stop and wait until the user tells you to continue. |
| -32005 | Busy (an import, export, or render runs) | `tasks.wait`, then try again. |
| -32007 | Failed | Read `data.reason`; after a failed editor save, see `references/limits.md`. |
