# Task commands

See [Concepts](../concepts.md#tasks) for the task ids and the task object.

## `tasks.list`

<!-- BEGIN GENERATED: tasks.list -->
Changes state: no.

Returns the tasks that have not finished (imports, an export, and background tasks) and whether all application work is idle.

**Parameters**

No parameters other than `timeout_ms`.

**Result**

| Field | Type | Always | Notes |
| --- | --- | --- | --- |
| `idle` | boolean | yes |  |
| `tasks` | array of object | yes |  |
| `tasks[].counts` | object | no |  |
| `tasks[].kind` | string | yes |  |
| `tasks[].message` | string | no |  |
| `tasks[].progress` | integer | no |  |
| `tasks[].result` | object | no |  |
| `tasks[].state` | string | yes |  |
| `tasks[].task_id` | string | yes |  |
<!-- END GENERATED: tasks.list -->

**Errors:** none.

**Example**

```bash
alcedo-cli --json call tasks.list
```

```json
{"idle":true,"tasks":[]}
```

## `tasks.wait`

<!-- BEGIN GENERATED: tasks.wait -->
Changes state: no.

Waits until the task 'task_id' finishes and returns its final state, or with 'idle': true until no import, export, or background task runs.

**Parameters**

| Name | Type | Required | Default | Notes |
| --- | --- | --- | --- | --- |
| `idle` | boolean | no |  | Wait for all application work instead. |
| `task_id` | string | no |  | A task id from a command. |

**Result**

The schema lists no fields; see the description and the example.
<!-- END GENERATED: tasks.wait -->

A task that finished before the call answers at once with its final state. A finished task can
end as `failed`; check `state` and `counts`, not only the exit code. A finished `adjustmentPaste`
task has `result` with the pasted photos and each failed photo
([adjustments.paste](adjustments.md#adjustmentspaste)).

**Errors**

- `-32602`: neither or both of `task_id` and `idle`; or an unknown task id.
- `-32006`: the task did not finish within `timeout_ms`. It still runs. Call `tasks.wait`
  again, with a larger `--timeout` for a large import or export.

**Example**

```bash
alcedo-cli --json call tasks.wait '{"task_id":"export-1"}'
alcedo-cli --json call tasks.wait '{"idle":true}'
```

```json
{"counts":{"completed":2,"failed":0,"skipped":0,"succeeded":2,"total":2},"kind":"export","message":"Export complete. Written 2/2 image(s), failed 0.","progress":100,"state":"succeeded","task_id":"export-1"}
{"idle":true}
```

## `tasks.cancel`

<!-- BEGIN GENERATED: tasks.cancel -->
Changes state: yes. In a GUI session it needs agent control (`control.acquire`).

Cancels the task 'task_id' as its cancel button in the task list does, and returns the task after the cancel: the state 'canceling' while its work stops, or 'canceled' for a task whose work had not started (a queued scan). tasks.wait returns the final state. A finished task is returned unchanged. An export, or another task that has no cancel, answers -32002 (rejected) with data.error 'not_cancelable'.

**Parameters**

| Name | Type | Required | Default | Notes |
| --- | --- | --- | --- | --- |
| `task_id` | string | yes |  | A task id from a command. |

**Result**

| Field | Type | Always | Notes |
| --- | --- | --- | --- |
| `counts` | object | no |  |
| `kind` | string | yes |  |
| `message` | string | no |  |
| `progress` | integer | no |  |
| `result` | object | no |  |
| `state` | string | yes |  |
| `task_id` | string | yes |  |
<!-- END GENERATED: tasks.cancel -->

It is the cancel button of the task in the task list. A running task is `canceling` until its
work stops; a scan of a mounted folder completes the batch that it imports first, and that batch
stays. A queued scan ends at once as `canceled`. Call `tasks.wait` for the final state.

**Errors**

- `-32602` `/task_id`: an unknown task id.
- `-32002` with `data.error` `not_cancelable`: an export, or a task that has no cancel.

**Example**

```bash
alcedo-cli --json call tasks.cancel '{"task_id":"bgtask-4"}'
```

```json
{"kind":"mountScan","message":"Waiting","progress":-1,"state":"canceled","task_id":"bgtask-4","title":"2026 Japan"}
```
