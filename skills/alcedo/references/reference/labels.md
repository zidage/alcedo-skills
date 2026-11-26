# AI label commands

Use these commands to check or generate AI labels with a running Alcedo session.
The project keeps labels generated for its photos. In a GUI session, acquire agent
control before a command that changes state.

## `labels.status`

<!-- BEGIN GENERATED: labels.status -->
Changes state: no.

Returns the active AI label model of the project, the photo counts with and without labels, and the progress of a running label generation. 'remaining_seconds' is present when the running generation has a time estimate.

**Parameters**

No parameters other than `timeout_ms`.

**Result**

| Field | Type | Always | Notes |
| --- | --- | --- | --- |
| `active_model_key` | string | no |  |
| `active_model_profile_id` | string | yes |  |
| `album_labeled` | integer | no |  |
| `album_total` | integer | no |  |
| `album_unlabeled` | integer | no |  |
| `canceled` | integer | no |  |
| `embedded` | integer | no |  |
| `failed` | integer | no |  |
| `model_activation_running` | boolean | no |  |
| `remaining_seconds` | integer | no |  |
| `running` | boolean | yes |  |
| `skipped` | integer | no |  |
| `status_text` | string | yes |  |
| `total` | integer | no |  |
<!-- END GENERATED: labels.status -->

**Errors**

- Open a project before you request its label status.

**Example**

```bash
alcedo-cli --json call labels.status
```

## `labels.install_model`

<!-- BEGIN GENERATED: labels.install_model -->
Changes state: yes. In a GUI session it needs agent control (`control.acquire`).

Downloads the AI label model 'profile_id' into the model folder of the AI Models settings page, as its Install button does, and answers with the download's task id (use tasks.wait). The download statement of the AI Models page must be accepted. A model that is installed answers with 'task_id' null.

**Parameters**

| Name | Type | Required | Default | Notes |
| --- | --- | --- | --- | --- |
| `profile_id` | string | yes |  | The model profile. |

**Result**

| Field | Type | Always | Notes |
| --- | --- | --- | --- |
| `task_id` | string or null | yes |  |
<!-- END GENERATED: labels.install_model -->

**Errors**

- `-32602` at `/profile_id` means the model profile is unknown.
- `-32002` means the download did not start. The AI Models settings page shows the reason.

**Example**

```bash
alcedo-cli --json call labels.install_model '{"profile_id":"siglip2-b32-256-multilingual"}'
```

If the response includes a task ID, pass it to `tasks.wait` before activating the model.

## `labels.activate_model`

<!-- BEGIN GENERATED: labels.activate_model -->
Changes state: yes. In a GUI session it needs agent control (`control.acquire`).

Activates the installed AI label model 'profile_id' for the project, as the AI Models settings page does, and answers when the activation finished. The answer is the result of labels.status.

**Parameters**

| Name | Type | Required | Default | Notes |
| --- | --- | --- | --- | --- |
| `profile_id` | string | yes |  | The model profile, for example siglip2-b32-256-multilingual. |

**Result**

| Field | Type | Always | Notes |
| --- | --- | --- | --- |
| `active_model_key` | string | no |  |
| `active_model_profile_id` | string | yes |  |
| `album_labeled` | integer | no |  |
| `album_total` | integer | no |  |
| `album_unlabeled` | integer | no |  |
| `canceled` | integer | no |  |
| `embedded` | integer | no |  |
| `failed` | integer | no |  |
| `model_activation_running` | boolean | no |  |
| `remaining_seconds` | integer | no |  |
| `running` | boolean | yes |  |
| `skipped` | integer | no |  |
| `status_text` | string | yes |  |
| `total` | integer | no |  |
<!-- END GENERATED: labels.activate_model -->

**Errors**

- `-32602` at `/profile_id` means the model is not installed.
- `-32002` means activation did not start. The AI Models settings page shows the reason.
- `-32007` means activation started but failed.

**Example**

```bash
alcedo-cli --json call labels.activate_model '{"profile_id":"siglip2-b32-256-multilingual"}'
```

## `labels.generate`

<!-- BEGIN GENERATED: labels.generate -->
Changes state: yes. In a GUI session it needs agent control (`control.acquire`).

Generates AI labels for the photos of the project that have none, as the Generate button of the AI label settings does. With 'force' true every photo gets new labels. Answers with the background task id when the generation runs (use tasks.wait), or with 'task_id' null and the status text when nothing runs.

**Parameters**

| Name | Type | Required | Default | Notes |
| --- | --- | --- | --- | --- |
| `force` | boolean | no |  | Generate labels for every photo. Default false. |

**Result**

| Field | Type | Always | Notes |
| --- | --- | --- | --- |
| `status_text` | string | yes |  |
| `task_id` | string or null | yes |  |
<!-- END GENERATED: labels.generate -->

**Errors**

- Wait for any current label generation or model activation before starting another one.

**Example**

```bash
alcedo-cli --json call labels.generate '{"force":false}'
```

Use `tasks.wait` when the response includes a task ID. Use `labels.status` to read progress.

## `labels.cancel`

<!-- BEGIN GENERATED: labels.cancel -->
Changes state: yes. In a GUI session it needs agent control (`control.acquire`).

Cancels the running label generation. Labels of the photos that finished stay. The answer is the result of labels.status.

**Parameters**

No parameters other than `timeout_ms`.

**Result**

| Field | Type | Always | Notes |
| --- | --- | --- | --- |
| `active_model_key` | string | no |  |
| `active_model_profile_id` | string | yes |  |
| `album_labeled` | integer | no |  |
| `album_total` | integer | no |  |
| `album_unlabeled` | integer | no |  |
| `canceled` | integer | no |  |
| `embedded` | integer | no |  |
| `failed` | integer | no |  |
| `model_activation_running` | boolean | no |  |
| `remaining_seconds` | integer | no |  |
| `running` | boolean | yes |  |
| `skipped` | integer | no |  |
| `status_text` | string | yes |  |
| `total` | integer | no |  |
<!-- END GENERATED: labels.cancel -->

**Errors**

- Open a project before you cancel a generation.

**Example**

```bash
alcedo-cli --json call labels.cancel
```
