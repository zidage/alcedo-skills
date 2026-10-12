# Control commands

Agent control applies to the GUI host. See [Concepts](../concepts.md#agent-control-gui-host). In
the headless host these commands always report `held: true` and change nothing.

## `control.acquire`

<!-- BEGIN GENERATED: control.acquire -->
Changes state: no.

Takes control of a GUI session so that state-changing commands run. While the agent holds control, the user cannot change the session state; the task island shows the agent task with each state-changing command and its note. Waits while the user drags an editor control. After the user stopped the agent, state-changing commands fail with -32004; call control.acquire again only after the user tells you to continue, and the agent task continues. Fails with -32005 while another holder holds control. The headless host always reports held.

**Parameters**

| Name | Type | Required | Default | Notes |
| --- | --- | --- | --- | --- |
| `holder_name` | string | no | `"agent"` | The name that the task island shows, for example claude-code. |

**Result**

| Field | Type | Always | Notes |
| --- | --- | --- | --- |
| `held` | boolean | yes |  |
| `holder_name` | string | yes |  |
| `revoked_by_user` | boolean | yes | True after the user stopped the agent, until an agent calls control.acquire again. |
<!-- END GENERATED: control.acquire -->

**Errors**

- `-32005`: another holder has control. `data.holder_name` names it.
- `-32006`: the user kept an editor slider down longer than `timeout_ms`.

**Example** (GUI session)

```bash
alcedo-cli --session gui --json call control.acquire '{"holder_name":"claude-code"}'
```

```json
{"held":true,"holder_name":"claude-code","revoked_by_user":false}
```

A state-changing command after **Stop**:

```json
{"error":{"code":-32004,"data":{"reason":"The user stopped the agent. Stop working and ask the user what to do. Call control.acquire only after the user tells you to continue."},"message":"The user stopped the agent. Stop working and ask the user what to do. Call control.acquire only after the user tells you to continue."}}
```

`control.get` after **Stop** stays the same until an agent acquires control. The window has no
button that changes it:

```json
{"held":false,"holder_name":"","revoked_by_user":true}
```

After the user tells the agent to continue, `control.acquire` succeeds and the stopped agent
task continues:

```json
{"held":true,"holder_name":"claude-code","revoked_by_user":false}
```

## `control.release`

<!-- BEGIN GENERATED: control.release -->
Changes state: no.

Gives control of a GUI session back to the user. The agent task finishes as succeeded. Without control the state does not change.

**Parameters**

No parameters other than `timeout_ms`.

**Result**

| Field | Type | Always | Notes |
| --- | --- | --- | --- |
| `held` | boolean | yes |  |
| `holder_name` | string | yes |  |
| `revoked_by_user` | boolean | yes | True after the user stopped the agent, until an agent calls control.acquire again. |
<!-- END GENERATED: control.release -->

**Errors:** none.

**Example** (GUI session)

```bash
alcedo-cli --session gui --json call control.release
```

```json
{"held":false,"holder_name":"","revoked_by_user":false}
```

## `control.get`

<!-- BEGIN GENERATED: control.get -->
Changes state: no.

Returns the agent control state of the session.

**Parameters**

No parameters other than `timeout_ms`.

**Result**

| Field | Type | Always | Notes |
| --- | --- | --- | --- |
| `held` | boolean | yes |  |
| `holder_name` | string | yes |  |
| `revoked_by_user` | boolean | yes | True after the user stopped the agent, until an agent calls control.acquire again. |
<!-- END GENERATED: control.get -->

**Errors:** none.

**Example** (headless session)

```bash
alcedo-cli --json call control.get
```

```json
{"held":true,"holder_name":"","revoked_by_user":false}
```

## A command without control

In a GUI session, a state-changing command without control fails:

```bash
alcedo-cli --session gui --json call editor.set '{"field":"exposure","value":2.5}'
```

```json
{"error":{"code":-32003,"data":{"reason":"This command changes the session state and needs agent control. Call control.acquire first."},"message":"This command changes the session state and needs agent control. Call control.acquire first."}}
```
