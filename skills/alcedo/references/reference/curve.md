# Tone Curve commands

## `curve.presets`

<!-- BEGIN GENERATED: curve.presets -->
Changes state: no.

Lists the Tone Curve presets in the order of the preset menu: Linear, the contrast shapes, Cl. Digit (the curve of the RAW import look), and the films. 'points' are the control points that a preset writes, on the curve axis (ACEScc, 18% grey at 0.41359). 'editor_value' applies the preset to the RGB curve: give it to editor.set on 'curve'. The id also applies to a channel curve, for example {"red": "kodak_2383"}. An id that names no preset, such as the earlier film_like, applies cl_digital. The document stores the points, not the id. Needs no open project.

**Parameters**

No parameters other than `timeout_ms`.

**Result**

| Field | Type | Always | Notes |
| --- | --- | --- | --- |
| `presets` | array of object | yes |  |
| `presets[].editor_value` | object | yes |  |
| `presets[].group` | `` \| `Contrast` \| `Rendering` \| `Film` | yes |  |
| `presets[].id` | string | yes |  |
| `presets[].name` | string | yes |  |
| `presets[].points` | array of object | yes |  |
| `presets[].points[].x` | number | yes |  |
| `presets[].points[].y` | number | yes |  |
| `total` | integer | yes |  |
<!-- END GENERATED: curve.presets -->

`curve.presets` lists the presets of the Tone Curve section, in the order of its preset menu. It
needs no open project. Alcedo Studio 0.3.6 and later have this command.

| Group | Presets (`id`) | Source |
| --- | --- | --- |
| | `linear` | The identity curve |
| `Contrast` | `soft_contrast`, `medium_contrast`, `strong_contrast` | S curves around 18% grey |
| `Rendering` | `cl_digital` | Cl. Digit (classic digital): one S curve of 7 points, shadows below the identity line, a soft shoulder into white |
| `Film` | `kodak_2383`, `fuji_velvia_50`, `kodak_ektachrome_e100` | The neutral tone of the film from the film print data |

Each preset keeps 18% grey where it is and changes the contrast, the shadows, and the highlights.
Cl. Digit is the RGB curve of a newly imported RAW photo. A preset id that names no preset,
such as `film_like` (the id of this preset in earlier builds), applies `cl_digital`. The film presets give only the tone of
the film; for the colour of the film use Film Print ([film.list](film.md)).

Each item of `presets` has these fields:

| Field | Notes |
| --- | --- |
| `id` | The id that a `curve` write accepts, for example `cl_digital`. |
| `name` | The name in the preset menu, for example `Cl. Digit`. |
| `group` | Empty for `linear`, else `Contrast`, `Rendering`, or `Film`. |
| `points` | The control points that the preset writes, on the curve axis (ACEScc; 18% grey at 0.41359). |
| `editor_value` | `{"points": "<id>"}`: the value of `editor.set` on `curve` that applies the preset to the RGB curve. |

In a `curve` write, each of `points`, `red`, `green`, and `blue` takes a list of points or a
preset id. The write stores the points of the preset; `editor.get` gives the points, not the id.
One write is one history commit:

```bash
alcedo-cli --json call editor.set '{"field":"curve","value":{"points":"medium_contrast"},"note":"agent: more mid-tone contrast"}'
alcedo-cli --json call editor.set '{"field":"curve","value":{"blue":"kodak_2383"}}'
```

**Errors**

- `editor.set` on `curve`, `-32602` `/value`: `curve.<key> names no Tone Curve preset: <id>;
  curve.presets lists them`.

**Example**

```bash
alcedo-cli --json call curve.presets
```

The result has `total` 9 and the nine presets in the order of the table above.
