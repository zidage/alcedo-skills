# Adjustment commands

Copy Adjustments and Paste Adjustments, like the commands of the library and the editor. Use
them to give a set of photos the look of one photo: tune one photo, copy its adjustments, and
paste them onto the set with one call. See [Workflows](../workflows.md#apply-one-look-to-many-photos).

A paste gives each photo one new Version with one commit, by the author `agent`. The Version
starts at the photo as imported, so the edits that the photo had before stay in its earlier
Version and are not combined with the pasted values. Fields that the package does not contain
keep the values of the photo as imported.

## `adjustments.items`

<!-- BEGIN GENERATED: adjustments.items -->
Changes state: no.

Lists the Versions of a photo and the items of one Version that adjustments.copy can copy, like the Copy Adjustments dialog: the Develop node (raw_decode, color_temp, lens_calib, crop_rotate), each Color Grade (enabled, mix, each adjustment, masks), and the DRT/Post node (drt and each post adjustment). An item with 'available' false has nothing to copy (a Color Grade without Masks).

**Parameters**

| Name | Type | Required | Default | Notes |
| --- | --- | --- | --- | --- |
| `element_id` | integer | yes |  | at least 1. The photo (library.list). |
| `version_id` | string | no |  | Hex id of a Version (adjustments.items); the active Version without it. |

**Result**

| Field | Type | Always | Notes |
| --- | --- | --- | --- |
| `element_id` | integer | yes |  |
| `nodes` | array of object | yes |  |
| `nodes[].default_grade` | boolean | no |  |
| `nodes[].items` | array of object | yes |  |
| `nodes[].items[].adjustment_id` | string | no |  |
| `nodes[].items[].available` | boolean | yes |  |
| `nodes[].items[].item` | string | yes |  |
| `nodes[].items[].name` | string | yes |  |
| `nodes[].items[].section` | string | yes |  |
| `nodes[].items[].type` | string | no |  |
| `nodes[].items[].value` | string | yes |  |
| `nodes[].kind` | string | yes |  |
| `nodes[].name` | string | yes |  |
| `nodes[].node_id` | string | yes |  |
| `version_id` | string | yes |  |
| `version_name` | string | yes |  |
| `versions` | array of object | yes |  |
| `versions[].active` | boolean | yes |  |
| `versions[].name` | string | yes |  |
| `versions[].version_id` | string | yes |  |
<!-- END GENERATED: adjustments.items -->

The nodes are in document order: the Develop node `develop`, each Color Grade (for example
`grade.primary`), and the DRT/Post node `drt`. `value` is the text that the Copy Adjustments
dialog shows; it is for reading, not for writing. The photo can be open in the editor or not;
the open photo is read with its edits that are not saved yet.

**Errors**

- `-32001`: no project is entered.
- `-32602` with `data.unknown_ids`: the photo is not in the project.
- `-32602` `/version_id`: the photo has no Version with this id.

**Example**

```bash
alcedo-cli --json call adjustments.items '{"element_id":1}'
```

```json
{"element_id":1,"nodes":[{"default_grade":false,"items":[{"available":true,"item":"raw_decode","name":"RAW Decode","section":"raw","value":"default, highlights On"},{"available":true,"item":"color_temp","name":"White Balance","section":"raw","value":"As Shot"},{"available":true,"item":"lens_calib","name":"Lens Correction","section":"raw","value":"Off"},{"available":true,"item":"crop_rotate","name":"Crop and Rotate","section":"geometry","value":"0.0 deg"}],"kind":"develop","name":"RAW and Geometry","node_id":"develop"},{"default_grade":true,"items":[{"available":true,"item":"enabled","name":"Enabled","section":"node","value":"On"},{"available":true,"item":"mix","name":"Mix","section":"node","value":"1.00"},{"adjustment_id":"grade.primary.exposure","available":true,"item":"adjustment","name":"Exposure","section":"tone","type":"alcedo.adjustment.exposure","value":"0.80"},{"adjustment_id":"grade.primary.contrast","available":true,"item":"adjustment","name":"Contrast","section":"tone","type":"alcedo.adjustment.contrast","value":"14.00"},{"adjustment_id":"grade.primary.saturation","available":true,"item":"adjustment","name":"Saturation","section":"look","type":"alcedo.adjustment.saturation","value":"1.30"},{"available":false,"item":"masks","name":"Masks","section":"masks","value":""}],"kind":"color_grade","name":"Color Grade 1","node_id":"grade.primary"},{"default_grade":false,"items":[{"available":true,"item":"drt","name":"Display Transform","section":"display_transform","value":"OpenDRT"},{"adjustment_id":"drt.film_grain","available":true,"item":"adjustment","name":"Film Grain","section":"look","type":"alcedo.adjustment.film_grain","value":"0.00"}],"kind":"drt_post","name":"DRT and Post Processing","node_id":"drt"}],"version_id":"a1ebc1faf50c6a99480f50479f44c617","version_name":"Default","versions":[{"active":true,"name":"Default","version_id":"a1ebc1faf50c6a99480f50479f44c617"}]}
```

The example output is shortened: a Color Grade lists every adjustment of the image (White
Balance, Exposure, Contrast, Whites, Blacks, Shadows, Highlights, Tone Curve, HLS, Saturation,
Vibrance, Color Wheels, Look LUT), and the DRT/Post node lists Clarity, Sharpen, Halation, and
Film Grain.

## `adjustments.copy`

<!-- BEGIN GENERATED: adjustments.copy -->
Changes state: no.

Copies adjustments of a photo, like Copy Adjustments: builds a package from the chosen items of a Version (the active Version without 'version_id') and returns its 'package_id' for adjustments.paste. Without 'items' every available item is copied, also crop_rotate and color_temp. An entry of 'items' names a node (adjustments.items) and one 'item' of it; an entry without 'item' copies every available item of the node. The package keeps the copied values for the session; later edits of the photo do not change it.

**Parameters**

| Name | Type | Required | Default | Notes |
| --- | --- | --- | --- | --- |
| `element_id` | integer | yes |  | at least 1. The photo (library.list). |
| `items` | array of object | no |  | at least 1 item(s). |
| `items[].adjustment_id` | string | no |  |  |
| `items[].item` | `enabled` \| `mix` \| `adjustment` \| `masks` \| `drt` \| `raw_decode` \| `color_temp` \| `lens_calib` \| `crop_rotate` | no |  | enabled and mix: node values of a Color Grade. adjustment: one adjustment, with adjustment_id. masks: all Masks of a Color Grade. drt: the display transform. raw_decode, color_temp, lens_calib, crop_rotate: the Develop fields. |
| `items[].node_id` | string | yes |  |  |
| `version_id` | string | no |  | Hex id of a Version (adjustments.items); the active Version without it. |

**Result**

| Field | Type | Always | Notes |
| --- | --- | --- | --- |
| `element_id` | integer | yes |  |
| `items` | array of object | yes |  |
| `items[].adjustment_id` | string | no |  |
| `items[].item` | string | yes |  |
| `items[].name` | string | yes |  |
| `items[].node_id` | string | yes |  |
| `items[].node_name` | string | yes |  |
| `items[].value` | string | yes |  |
| `package_id` | string | yes |  |
| `version_id` | string | yes |  |
| `version_name` | string | yes |  |
<!-- END GENERATED: adjustments.copy -->

Choose the items with care. Without `items`, the package also holds `crop_rotate` and
`color_temp` of the source, which suit the source photo but seldom the other photos. To copy a
look, name the Color Grade node (all its adjustments) and, when you changed it, `drt` or the
post adjustments of the DRT/Post node. `items` is reported in document order, whatever the order
of the request.

The package keeps the copied values: later edits of the source do not change it. A package is
kept until the session ends; copy again after a new `session start`.

**Errors**

- `-32001`: no project is entered.
- `-32602` with `data.unknown_ids`: the photo is not in the project.
- `-32602` `/version_id`: the photo has no Version with this id.
- `-32602` `/items/<n>/node_id`: the Version has no such node.
- `-32602` `/items/<n>`: the node has no such item, the item has nothing to copy (`available`
  is false), or the item is named twice.
- `-32602` `/items/<n>/adjustment_id`: an `adjustment` item without its `adjustment_id`, or
  another item with one.

**Example**

```bash
alcedo-cli --json call adjustments.copy '{"element_id":1,"items":[{"node_id":"grade.primary"}]}'
```

```json
{"element_id":1,"items":[{"item":"enabled","name":"Enabled","node_id":"grade.primary","node_name":"Color Grade 1","value":"On"},{"item":"mix","name":"Mix","node_id":"grade.primary","node_name":"Color Grade 1","value":"1.00"},{"adjustment_id":"grade.primary.exposure","item":"adjustment","name":"Exposure","node_id":"grade.primary","node_name":"Color Grade 1","value":"0.80"},{"adjustment_id":"grade.primary.contrast","item":"adjustment","name":"Contrast","node_id":"grade.primary","node_name":"Color Grade 1","value":"14.00"}],"package_id":"package-1","version_id":"a1ebc1faf50c6a99480f50479f44c617","version_name":"Default"}
```

The example output is shortened to four of the copied items.

```bash
alcedo-cli --json call adjustments.copy '{"element_id":1,"items":[{"node_id":"grade.nope"}]}'
```

```json
{"error":{"code":-32602,"data":{"pointer":"/items/0/node_id","reason":"unknown node id: grade.nope; adjustments.items lists the nodes"},"message":"unknown node id: grade.nope; adjustments.items lists the nodes"}}
```

## `adjustments.paste`

<!-- BEGIN GENERATED: adjustments.paste -->
Changes state: yes. In a GUI session it needs agent control (`control.acquire`).

Pastes a package of adjustments.copy onto photos, like Paste Adjustments: each photo gets one new Version (named 'version_name', or Pasted Adjustments) with one commit by the agent. Without 'element_ids' the photos selected in the library (GUI host only). The photo open in the editor pastes first through the editor; 'editor' reports it. The other photos paste in a background task: wait for 'task_id' with tasks.wait; its 'result' lists the pasted photos and each failed photo with the reason. Busy while another Paste or an editor save runs.

**Parameters**

| Name | Type | Required | Default | Notes |
| --- | --- | --- | --- | --- |
| `element_ids` | array of integer | no |  | at least 1 item(s); each item at least 1. The photos; the library selection without it. |
| `note` | string | no |  | Why the agent pastes; stored with each commit. |
| `package_id` | string | yes |  | A package id from adjustments.copy. |
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
<!-- END GENERATED: adjustments.paste -->

The command answers when the photo open in the editor has its new Version and the background
task of the other photos runs. `tasks.wait` with the `task_id` answers with the result of each
photo in `result`:

| Field | Meaning |
| --- | --- |
| `applied_count`, `applied_ids` | The photos that have the new Version. |
| `failure_count`, `failures[]` | The photos that failed, each with `element_id` and `message`. A failed photo keeps its history unchanged. |

The task state is `succeeded` when at least one photo was pasted, and `failed` when every photo
failed. A photo fails, for example, when the package changes nothing on it ("transfer package
produces no changes on the target document"). A name that a photo already has gets a number,
for example `Pasted Adjustments (2)`.

**Errors**

- `-32001`: no project is entered, or no `element_ids` in the headless host (it has no library
  selection).
- `-32602` `/package_id`: no package with this id in the session.
- `-32602` `/element_ids`: no `element_ids` and no photo selected in the library.
- `-32602` with `data.unknown_ids`: a photo is not in the project.
- `-32602` `/version_name`: the name is empty after trimming.
- `-32005`: another Paste or an editor save runs. Wait (`tasks.wait {"idle": true}`) and call
  again.
- `-32002`: the editor refused the paste into the open photo and no other photo was a target.
  When there are other targets, the paste continues and `editor.pasted` is false with `message`.
- `-32003`: GUI session without agent control.

**Example**

```bash
alcedo-cli --json call adjustments.paste '{"package_id":"package-1","element_ids":[1,2],"note":"share the look"}'
```

```json
{"editor":{"element_id":1,"pasted":true,"version_id":"602d373d346c21dc297b277266c2bf4f"},"target_count":2,"task_id":"bgtask-2"}
```

```bash
alcedo-cli --json call tasks.wait '{"task_id":"bgtask-2"}'
```

```json
{"kind":"adjustmentPaste","message":"Adjustments pasted.","progress":-1,"result":{"applied_count":1,"applied_ids":[2],"failure_count":0,"failures":[]},"state":"succeeded","task_id":"bgtask-2","title":"Pasting adjustments"}
```
