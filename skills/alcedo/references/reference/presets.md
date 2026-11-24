# Preset commands

A preset is a `.alcpreset` file in the preset folder of Alcedo Studio (Settings > LUTs and Color
Management > Presets). It holds adjustments, like the package of `adjustments.copy`, and has no
crop, rotation, or lens correction. The preset browser of the Versions panel and the
`Apply Preset...` dialog of the library show the same presets.

## `presets.list`

<!-- BEGIN GENERATED: presets.list -->
Changes state: no.

Lists the presets of the preset folder, like the preset browser: the presets directly in the folder first, then each subfolder (its 'group'). 'preset_id' is the path below the folder. A preset with 'available' false cannot be applied; 'reason' says why. With 'details' each available preset also lists its items by node. Scans the folder first, like the preset browser when it opens, so a file copied into the folder is listed. Needs no open project.

**Parameters**

| Name | Type | Required | Default | Notes |
| --- | --- | --- | --- | --- |
| `details` | boolean | no |  | List the items of each preset; reads each file. |

**Result**

| Field | Type | Always | Notes |
| --- | --- | --- | --- |
| `error` | string | no |  |
| `folder` | string | yes |  |
| `presets` | array of object | yes |  |
| `presets[].available` | boolean | yes |  |
| `presets[].group` | string | yes |  |
| `presets[].name` | string | yes |  |
| `presets[].nodes` | array of object | no |  |
| `presets[].nodes[].items` | array of string | yes |  |
| `presets[].nodes[].name` | string | yes |  |
| `presets[].preset_id` | string | yes |  |
| `presets[].reason` | string | no |  |
<!-- END GENERATED: presets.list -->

Each preset has these fields:

| Field | Notes |
| --- | --- |
| `preset_id` | The path of the file below `folder`, with `/`, for example `Film/Amber.alcpreset`. Give it to `presets.apply`. |
| `name` | The file name without `.alcpreset`. The preset browser shows this name. |
| `group` | The subfolder of the preset. Empty for a preset directly in the folder. |
| `available` | The preset can be applied. |
| `reason` | Only when `available` is false: why, for example a file that is not a preset or a LUT outside the LUT library. |
| `nodes` | Only with `details` and for an available preset: each node of the preset with the names of its items. |

The presets directly in the folder come first, then each group. `error` is set when the scan
could not read the complete folder.

**Errors**

- `-32001`: the preset library is not available.

**Example**

```bash
alcedo-cli --json call presets.list '{}'
```

```json
{"folder":"C:\\Users\\me\\.alcedo\\presets","presets":[{"available":true,"group":"","name":"Evening","preset_id":"Evening.alcpreset"}]}
```

With `details`, each available preset also has `nodes`:

```bash
alcedo-cli --json call presets.list '{"details":true}'
```

```json
{"folder":"C:\\Users\\me\\.alcedo\\presets","presets":[{"available":true,"group":"","name":"Evening","nodes":[{"items":["RAW Decode","White Balance"],"name":"RAW and Geometry"},{"items":["Enabled","Mix","Grade White Balance","Exposure","Contrast","Whites","Blacks","Shadows","Highlights","Tone Curve","HLS","Saturation","Vibrance","Color Wheels","Look LUT"],"name":"Color Grade 1"},{"items":["Display Transform","Clarity","Sharpen","Halation","Film Grain"],"name":"DRT and Post Processing"}],"preset_id":"Evening.alcpreset"}]}
```

## `presets.save`

<!-- BEGIN GENERATED: presets.save -->
Changes state: yes. In a GUI session it needs agent control (`control.acquire`).

Saves a Version of a photo (the active Version without 'version_id') as a preset in the preset folder, like a drag of the Version onto the preset part of the Versions panel: every transferable item except crop_rotate and lens_calib. The name is 'name', or the Version name made a valid file name; a name that exists gets a number. Answers when the file is written.

**Parameters**

| Name | Type | Required | Default | Notes |
| --- | --- | --- | --- | --- |
| `element_id` | integer | yes |  | 1 to 4294967295. The photo (library.list). |
| `name` | string | no |  | Preset name: no path separator, control character, or one of <>:"\|?*, at most 120 characters. |
| `version_id` | string | no |  | Hex id of a Version (adjustments.items). |

**Result**

| Field | Type | Always | Notes |
| --- | --- | --- | --- |
| `name` | string | yes |  |
| `nodes` | array of object | yes |  |
| `nodes[].items` | array of string | yes |  |
| `nodes[].name` | string | yes |  |
| `preset_id` | string | yes |  |
<!-- END GENERATED: presets.save -->

The preset gets every item of the Version that a preset can hold. A save leaves out
`crop_rotate` and `lens_calib`, because they suit only the photo. The new file is in the folder
itself, not in a group. A name that the folder has gets a number, for example `Warm 2`; the
answer has the name of the file that the save wrote. A LUT of the Version is stored as its
reference in the LUT library, so the preset works after the user moves the LUT library.

Save a preset only when the user asks for one: it adds a file to the user's preset folder.

**Errors**

- `-32001`: no project is entered.
- `-32602` `/element_id`: no photo id, or not a positive integer.
- `-32602` with `data.unknown_ids`: the photo is not in the project.
- `-32602` `/version_id`: the photo has no Version with this id.
- `-32602` `/name`: the name is empty, too long, or has a path separator, a control character,
  or one of `<>:"|?*`.
- `-32002`: the Version has no item that a preset can hold, or a LUT of the Version is not in
  the LUT library.
- `-32007`: the history of the photo cannot be read, or the file cannot be written.
- `-32003`: GUI session without agent control.

**Example**

Save the active Version of photo 1, after `editor.batch_set` changed its exposure, contrast,
and saturation:

```bash
alcedo-cli --json call presets.save '{"element_id":1,"name":"Evening"}'
```

```json
{"name":"Evening","nodes":[{"items":["RAW Decode","White Balance"],"name":"RAW and Geometry"},{"items":["Enabled","Mix","Grade White Balance","Exposure","Contrast","Whites","Blacks","Shadows","Highlights","Tone Curve","HLS","Saturation","Vibrance","Color Wheels","Look LUT"],"name":"Color Grade 1"},{"items":["Display Transform","Clarity","Sharpen","Halation","Film Grain"],"name":"DRT and Post Processing"}],"preset_id":"Evening.alcpreset"}
```

`nodes` lists every item that the preset holds, also the items that the Version left at their
defaults: an apply sets each of them on the photo.

## `presets.apply`

<!-- BEGIN GENERATED: presets.apply -->
Changes state: yes. In a GUI session it needs agent control (`control.acquire`).

Applies a preset onto photos, like Apply Preset...: each photo gets one new Version, named 'version_name' or after the preset, with one commit by the agent. Give 'preset_id' (presets.list) or 'file', a preset file that is applied one time and does not enter the preset folder. Without 'element_ids' the photos selected in the library (GUI host only). The photo open in the editor applies first through the editor; 'editor' reports it. The other photos apply in a background Paste task: wait for 'task_id' with tasks.wait; its 'result' lists the applied photos and each failed photo with the reason. Busy while another Paste or an editor save runs.

**Parameters**

| Name | Type | Required | Default | Notes |
| --- | --- | --- | --- | --- |
| `element_ids` | array of integer | no |  | at least 1 item(s); each item at least 1. The photos; the library selection without it. |
| `file` | string | no |  | Path of a .alcpreset file to apply one time, instead of preset_id. |
| `note` | string | no |  | Why the agent pastes; stored with each commit. |
| `preset_id` | string | no |  | A preset id from presets.list. |
| `version_name` | string | no |  | Name of the new Versions. A name that a photo already has gets a number. |

**Result**

| Field | Type | Always | Notes |
| --- | --- | --- | --- |
| `editor` | object | no |  |
| `editor.element_id` | integer | yes |  |
| `editor.message` | string | no |  |
| `editor.pasted` | boolean | yes |  |
| `editor.version_id` | string | no |  |
| `target_count` | integer | yes |  |
| `task_id` | string or null | yes | The background Paste task; null when only the editor photo was a target. |
<!-- END GENERATED: presets.apply -->

`presets.apply` is `adjustments.paste` of the preset: each photo gets one new Version with one
commit by the agent, and the Version starts at the photo as imported. The Version name is the
preset name, or `version_name`. The result and the errors of the background task are the ones of
`adjustments.paste` ([adjustments.md](adjustments.md#adjustmentspaste)).

`preset_id` names a preset of the last scan of the folder. Call `presets.list` first when the
user copied files into the folder during the session. `file` applies a preset file from
anywhere one time. That file does not enter the preset folder; the Version name is its file
name without `.alcpreset`.

**Errors**

- `-32001`: no project is entered, or no `element_ids` in the headless host (it has no library
  selection).
- `-32602`: both `preset_id` and `file`, or neither.
- `-32602` `/preset_id`: the preset folder has no preset with this id.
- `-32602` `/element_ids`: no `element_ids` and no photo selected in the library.
- `-32602` with `data.unknown_ids`: a photo is not in the project.
- `-32602` `/version_name`: the name is empty after trimming.
- `-32002`: the preset is not available (the message has the reason), the file is not a valid
  preset, or the editor refused the apply to the open photo and no other photo was a target.
- `-32005`: another Paste or an editor save runs. Wait (`tasks.wait {"idle": true}`) and call
  again.
- `-32003`: GUI session without agent control.

**Example**

```bash
alcedo-cli --json call presets.apply '{"preset_id":"Evening.alcpreset","element_ids":[2],"note":"agent: evening look"}'
alcedo-cli --json call tasks.wait '{"task_id":"bgtask-4"}'
```

```json
{"target_count":1,"task_id":"bgtask-4"}
{"kind":"adjustmentPaste","message":"Adjustments pasted.","progress":-1,"result":{"applied_count":1,"applied_ids":[2],"failure_count":0,"failures":[]},"state":"succeeded","task_id":"bgtask-4","title":"Pasting adjustments"}
```

A preset id is the file path with `.alcpreset`, not the name:

```bash
alcedo-cli --json call presets.apply '{"preset_id":"Evening","element_ids":[2]}'
```

```json
{"error":{"code":-32602,"data":{"pointer":"/preset_id","reason":"unknown preset id; presets.list lists them"},"message":"unknown preset id; presets.list lists them"}}
```
