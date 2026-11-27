# Command reference

Protocol version 1, Alcedo Studio 0.3.7. `alcedo-cli schema` prints the same list from a running
session.

Each section has the description, the parameters, and the result. These parts are generated
from [commands.json](commands.json); do not edit them by hand. The errors and examples are
written by hand. Every command also accepts
`timeout_ms`; see [cli.md](../cli.md#call).

"Changes state: yes" means that a GUI session needs agent control for the command
([Concepts](../concepts.md#agent-control-gui-host)).

| Group | Commands |
| --- | --- |
| [Session](session.md) | `session.ping`, `session.describe`, `state.get`, `session.shutdown` |
| [Control](control.md) | `control.acquire`, `control.release`, `control.get` |
| [Project](project.md) | `project.create`, `project.open`, `project.save`, `project.close` |
| [Library](library.md) | `library.import`, `library.folders`, `library.folder.create`, `library.folder.rename`, `library.folder.move`, `library.folder.delete`, `library.link`, `library.list`, `library.stats`, `library.info`, `library.thumbnail`, `library.thumbnails`, `library.rate`, `library.color_label`, `library.delete_mark`, `library.color_labels`, `library.color_label_name.set`, `library.delete`, `library.mounts`, `library.mount`, `library.sync`, `library.unmount`, `library.selection.get`, `library.selection.set` |
| [Tasks](tasks.md) | `tasks.list`, `tasks.wait` |
| [Editor](editor.md) | `editor.open`, `editor.close`, `editor.catalog`, `editor.get`, `editor.set`, `editor.batch_set`, `editor.undo`, `editor.redo`, `editor.history`, `editor.actions` |
| [Render](render.md) | `render.preview` |
| [Nodes](nodes.md) | `nodes.list`, `nodes.set_visibility` |
| [Versions](versions.md) | `versions.list`, `versions.create`, `versions.branch`, `versions.checkout`, `versions.rename`, `versions.remove` |
| [Adjustments](adjustments.md) | `adjustments.items`, `adjustments.copy`, `adjustments.paste` |
| [Presets](presets.md) | `presets.list`, `presets.save`, `presets.apply` |
| [Export](export.md) | `export.options`, `export.run`, `export.status` |
| [Search](search.md) | `search.query` |
| [LUT](lut.md) | `lut.list` |
| [Film](film.md) | `film.list` |
| [AI Denoise](denoise.md) | `denoise.status`, `denoise.set` |
| [AI Labels](labels.md) | `labels.status`, `labels.install_model`, `labels.activate_model`, `labels.generate`, `labels.cancel` |
| [Tone Curve](curve.md) | `curve.presets` |

[Editor fields](editor_fields.md) lists every field of `editor.set`.
