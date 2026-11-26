# AI Denoise commands

AI Denoise runs a neural network on the RAW mosaic of a photo in place of the demosaic. It
removes the sensor noise of the full-size render: the editor, `render.preview`, and the export.
Library thumbnails and contact sheets render from a reduced mosaic and show the photo without
it. Alcedo Studio 0.3.7 and later have these commands.

Read the AI Denoise section of `SKILL.md` before you turn it on: the agent uses it when the user
asks for noise reduction, and by itself only for a high ISO photo whose noise is clearly visible.

## `denoise.status`

<!-- BEGIN GENERATED: denoise.status -->
Changes state: no.

Returns whether this computer can run AI Denoise ('available': a supported device), the installed model ('installed', 'version', or 'problem' model_not_installed or model_unreadable with 'reason'), and for the photo that the editor has open ('photo', null without one): its sensor, whether AI Denoise is on, the model version that the switch recorded, and the AI Denoise error of its last frame. AI Denoise runs a neural network on the RAW mosaic in place of the demosaic of the full-size render (editor, render.preview, export); thumbnails do not show it.

**Parameters**

No parameters other than `timeout_ms`.

**Result**

| Field | Type | Always | Notes |
| --- | --- | --- | --- |
| `available` | boolean | yes |  |
| `model` | object | yes |  |
| `model.installed` | boolean | yes |  |
| `model.problem` | string or null | yes | model_not_installed or model_unreadable; null when the model is installed. |
| `model.reason` | string or null | yes |  |
| `model.version` | string or null | yes |  |
| `photo` | object or null | yes |  |
<!-- END GENERATED: denoise.status -->

`available` is true when this computer has a device for the model: a Direct3D 12 GPU on
Windows, the Neural Engine of Apple silicon on macOS. `model` describes the installed model of
Settings > AI Models: `installed` with its `version`, or `problem` `model_not_installed` or
`model_unreadable` with the `reason`.

`photo` is the photo that the editor has open (null without one):

| Field | Notes |
| --- | --- |
| `sensor` | `bayer`, `xtrans`, `other` (for example monochrome), or `unknown` while the RAW file is read or when it cannot be read. AI Denoise supports `bayer`. |
| `enabled` | True while AI Denoise is on for the photo. |
| `model_version` | The model version that the switch recorded when it was turned on; null while it is off. |
| `error` | The AI Denoise error of the last frame, `{"kind", "text"}`; null after a frame without one. |

The `kind` of an AI Denoise error:

| Kind | Meaning |
| --- | --- |
| `model_not_installed` | The model folder holds no AI Denoise model. |
| `device_too_slow` | The projected model time of the photo is above the slow-device limit (0.05 s for each megapixel). The device stays marked as slow until Alcedo Studio restarts. |
| `sensor_not_supported` | The photo is an X-Trans or monochrome RAW file, or a raster image. |
| `run_failed` | The runtime reported an error, for example of the GPU or of its memory. |

**Example**

```bash
alcedo-cli --json call denoise.status
```

## `denoise.set`

<!-- BEGIN GENERATED: denoise.set -->
Changes state: yes. In a GUI session it needs agent control (`control.acquire`).

Turns AI Denoise on or off for the photo that the editor has open, as the switch of the RAW Decode panel does: one history commit of 'raw_decode' with the author agent and the optional 'note'; on records the installed model version. Answers after the commit and its rendered frame. The frame of a full-size render runs the model, so it takes longer. Turning on is refused (-32002, data.refusal platform_unavailable, model_not_installed, model_unreadable, or sensor_not_supported) before any change. When the frame fails, the commit stays and the error data has 'head_commit', 'enabled', and 'ai_denoise_error' (kind, text); turn AI Denoise off again with enabled false. For several photos, copy the raw_decode item with adjustments.copy and paste it.

**Parameters**

| Name | Type | Required | Default | Notes |
| --- | --- | --- | --- | --- |
| `enabled` | boolean | yes |  | true turns AI Denoise on. |
| `note` | string | no |  | Note of the history commit. |

**Result**

| Field | Type | Always | Notes |
| --- | --- | --- | --- |
| `head_commit` | string or null | yes |  |
| `photo` | object | yes |  |
| `photo.element_id` | integer | yes |  |
| `photo.enabled` | boolean | yes |  |
| `photo.error` | object or null | yes | The AI Denoise error of the last frame (kind, text); null after a frame without one. |
| `photo.image_id` | integer | yes |  |
| `photo.model_version` | string or null | yes | The model version that the switch recorded when it was turned on; null while it is off. |
| `photo.sensor` | `bayer` \| `xtrans` \| `other` \| `unknown` | yes | The sensor of the RAW file. AI Denoise supports bayer only; unknown while the file is read or when it cannot be read. |
<!-- END GENERATED: denoise.set -->

`denoise.set` is the **AI Denoise** switch of the RAW Decode panel. `enabled: true` records the
installed model version in the photo and renders it with the model; the answer comes after the
rendered frame, so it takes longer than other edits (the model takes about 0.6 to 0.7 s for a
45 MP photo on a fast device, more for the first photo of a size). `enabled: false` returns the
photo to its demosaic method. Each change is one history commit of `raw_decode` with the author
`agent` and the `note`; `editor.undo` reverts it. A write of the current state makes no commit.

`editor.set` on `raw_decode` keeps the switch as it is.

**Several photos**

Turn AI Denoise on in one photo, then copy the `raw_decode` item and paste it onto the other
photos (see [Adjustments](adjustments.md)):

```bash
alcedo-cli --json call adjustments.copy '{"element_id":12,"items":[{"node_id":"develop","item":"raw_decode"}]}'
alcedo-cli --json call adjustments.paste '{"package_id":"<package_id>","element_ids":[13,14],"note":"agent: AI Denoise, ISO 6400"}'
alcedo-cli --json call tasks.wait '{"task_id":"<task_id>"}'
```

The `raw_decode` item also carries the demosaic method and the highlight reconstruction of the
source photo. Each pasted photo runs the model when it renders at full size; a photo that is not
a Bayer RAW file reports `sensor_not_supported` then.

**Errors**

- `-32001`: `No editor image is open.`
- `-32002` with `data.refusal`, before any change:
  - `platform_unavailable`: this computer has no device for the model.
  - `model_not_installed`: download the model on Settings > AI Models (the user does it).
  - `model_unreadable`: the installed graph file cannot be read; `data.reason` has the cause.
  - `sensor_not_supported`: the photo is not a Bayer RAW file.
- `-32002`: the editor cannot edit now (`data.reason`).
- `-32007` with `data.ai_denoise_error`: the frame of the commit failed with an AI Denoise error.
  The commit stays (`data.enabled` true, `data.head_commit`). Turn AI Denoise off again with
  `{"enabled":false}` and tell the user the `kind`.

Every command that renders the photo (`editor.set`, `editor.batch_set`, `render.preview`) also
reports a failed AI Denoise run with `data.ai_denoise_error` while the switch is on.

**Example**

```bash
alcedo-cli --json call denoise.set '{"enabled":true,"note":"agent: AI Denoise, ISO 6400 shadow noise"}'
```
