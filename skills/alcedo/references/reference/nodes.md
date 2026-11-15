# Node commands

See [Concepts](../concepts.md#color-grades). Both node commands work on the open photo and on
its Color Grades: the nodes that hold the color adjustments and the Masks of one Mask Group.

## `nodes.list`

<!-- BEGIN GENERATED: nodes.list -->
Changes state: no.

Returns the Color Grades of the open image with their visibility: first the Color Grades on the image path from Develop to the display transform, in that order, then the detached Color Grades in document order.

**Parameters**

No parameters other than `timeout_ms`.

**Result**

| Field | Type | Always | Notes |
| --- | --- | --- | --- |
| `color_grades` | array of object | yes |  |
| `color_grades[].backbone_index` | integer or null | yes | Position among the Color Grades on the image path from Develop to the display transform, from 0 at the Develop side; null for a Color Grade off that path. |
| `color_grades[].deletion_protected` | boolean | yes | True when the Color Grade is locked against deletion. |
| `color_grades[].detached` | boolean | yes | True when the Color Grade has no scene-image edge: it stays in the document outside the render. |
| `color_grades[].hidden` | boolean | yes | True when the Color Grade is hidden: the render skips it, and its parameters and Masks stay in the document. |
| `color_grades[].mask_count` | integer | yes | at least 0. Number of Masks of the Color Grade. |
| `color_grades[].name` | string | yes | Name of the Color Grade, as the editor shows it. |
| `color_grades[].node_id` | string | yes | Id of the Color Grade node. |
<!-- END GENERATED: nodes.list -->

The list starts with the Color Grades on the image path, from the Develop side to the display
transform; `backbone_index` counts them from 0. The detached Color Grades follow in document
order with `backbone_index` null.

**Errors**

- `-32001`: no photo is open.

**Example**

```bash
alcedo-cli --json call nodes.list
```

```json
{"color_grades":[{"backbone_index":0,"deletion_protected":false,"detached":false,"hidden":false,"mask_count":1,"name":"Color Grade 1","node_id":"grade.primary"},{"backbone_index":1,"deletion_protected":false,"detached":false,"hidden":true,"mask_count":0,"name":"Color Grade 2","node_id":"grade.3f9c2a7e-41d6-4b0e-9a55-0c8e2f6b1d47"},{"backbone_index":null,"deletion_protected":false,"detached":true,"hidden":false,"mask_count":2,"name":"Color Grade 3","node_id":"grade.81d04b5c-7a2e-4f19-b3c8-5e6d9f0a2c13"}]}
```

## `nodes.set_visibility`

<!-- BEGIN GENERATED: nodes.set_visibility -->
Changes state: yes. In a GUI session it needs agent control (`control.acquire`).

Shows or hides one Color Grade, like the visibility button of its Mask Group: one history commit (Show Color Grade or Hide Color Grade). A hidden Color Grade keeps its parameters and Masks, and the render skips it in the preview and the export. A value equal to the current one makes no commit and succeeds. Answers after the commit and its rendered frame with the new state of the Color Grade. When the frame of the commit fails to render, the commit stays and the error data has 'reason' and 'head_commit'; editor.undo reverts it.

**Parameters**

| Name | Type | Required | Default | Notes |
| --- | --- | --- | --- | --- |
| `node_id` | string | yes |  | Id of a Color Grade (nodes.list). |
| `visible` | boolean | yes |  | true shows the Color Grade; false hides it. |

**Result**

| Field | Type | Always | Notes |
| --- | --- | --- | --- |
| `backbone_index` | integer or null | yes | Position among the Color Grades on the image path from Develop to the display transform, from 0 at the Develop side; null for a Color Grade off that path. |
| `deletion_protected` | boolean | yes | True when the Color Grade is locked against deletion. |
| `detached` | boolean | yes | True when the Color Grade has no scene-image edge: it stays in the document outside the render. |
| `hidden` | boolean | yes | True when the Color Grade is hidden: the render skips it, and its parameters and Masks stay in the document. |
| `mask_count` | integer | yes | at least 0. Number of Masks of the Color Grade. |
| `name` | string | yes | Name of the Color Grade, as the editor shows it. |
| `node_id` | string | yes | Id of the Color Grade node. |
<!-- END GENERATED: nodes.set_visibility -->

The commit appears in `editor.history` and can be undone with `editor.undo`. The parameters and
Masks of a hidden Color Grade stay editable, and they show again when the Color Grade is shown.

**Errors**

- `-32001`: no photo is open.
- `-32602` `/node_id`: the id names no node of the photo, or it names a node other than a Color
  Grade (for example the Develop node).
- `-32002`: the editor refused the change, with the reason in the message.

**Example**

```bash
alcedo-cli --json call nodes.set_visibility '{"node_id":"grade.3f9c2a7e-41d6-4b0e-9a55-0c8e2f6b1d47","visible":false}'
```

```json
{"backbone_index":1,"deletion_protected":false,"detached":false,"hidden":true,"mask_count":0,"name":"Color Grade 2","node_id":"grade.3f9c2a7e-41d6-4b0e-9a55-0c8e2f6b1d47"}
```

## Parameters

| Name | Meaning |
| --- | --- |
| Color Grade | A node with color adjustments and the Masks of one Mask Group. |
| image path | The path of the image from the Develop node through the Color Grades to the display transform. |
| `node_id` | Id of a Color Grade, as `nodes.list` gives it. |
| `visible` | `true` shows the Color Grade; `false` hides it. |
| `hidden` | The render skips the Color Grade; its parameters and Masks stay in the document. |
| `detached` | The Color Grade has no scene-image edge; it stays in the document outside the render. |
| `backbone_index` | Position of the Color Grade on the image path, from 0 at the Develop side; null for a detached Color Grade. |
| `deletion_protected` | The Color Grade is locked against deletion. |
| `mask_count` | Number of Masks of the Color Grade. |
