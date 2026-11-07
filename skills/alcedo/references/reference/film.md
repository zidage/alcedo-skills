# Film commands

## `film.list`

<!-- BEGIN GENERATED: film.list -->
Changes state: no.

Lists the films and print materials of the film print browser in browser order: the negatives, the colour reversal films, then the print materials, each list by brand and family. 'name' is the name of the option in editor.catalog, 'short_label' the name without the brand. A negative has 'balance_light', the light that the film is balanced for (D55 daylight or T3200 tungsten). 'editor_value' is the odt property that the entry sets; give it to editor.set on 'odt' with "method": "film_print" (a colour reversal film reads no print material). When the film print resources are not available, 'warnings' has film_resources_unavailable and no entry has 'balance_light'. Needs no open project.

**Parameters**

| Name | Type | Required | Default | Notes |
| --- | --- | --- | --- | --- |
| `brand` | string | no |  | Only the entries of this brand, for example Kodak (case-insensitive). An empty string selects negative_scan and cine_look, which have no brand. |
| `list` | `negative` \| `reversal` \| `print` | no |  | Only the entries of this list of the film print browser: the negatives, the colour reversal films, or the print materials. |
| `query` | string | no |  | Case-insensitive text that the name, the short label, the family, or the identifier contains. |

**Result**

| Field | Type | Always | Notes |
| --- | --- | --- | --- |
| `films` | array of object | yes |  |
| `films[].balance_light` | string | no |  |
| `films[].brand` | string | yes |  |
| `films[].editor_value` | object | yes |  |
| `films[].family` | string | yes |  |
| `films[].id` | string | yes |  |
| `films[].list` | `negative` \| `reversal` \| `print` | yes |  |
| `films[].name` | string | yes |  |
| `films[].short_label` | string | yes |  |
| `total` | integer | yes |  |
| `warnings` | array of object | yes |  |
| `warnings[].code` | string | yes |  |
| `warnings[].message` | string | yes |  |
<!-- END GENERATED: film.list -->

`film.list` lists the films and print materials of the Film Print display transform, in the order
of the film print browser of the Display Transform panel: the negatives, the colour reversal
films, and then the print materials. Each list is grouped by brand (Kodak, Fujifilm, Agfa) and
then by family. It needs no open project. Alcedo Studio 0.3.4 and later have this command.

Each item of `films` has these fields:

| Field | Notes |
| --- | --- |
| `id` | The identifier that `odt` stores, for example `kodak_portra_400`. |
| `name` | The name of the option in `editor.catalog`, for example `Kodak Portra 400`. |
| `list` | `negative`, `reversal` (a colour reversal film, a slide film), or `print`. |
| `brand` | `Kodak`, `Fujifilm`, or `Agfa`. Empty for `negative_scan` and `cine_look`, which the browser shows above the brand groups. |
| `family` | The group under the brand: `Photo`, `Cinema`, `Classic Cinema`, `Aerial` for the negatives; `Cinema Print`, `Paper`, `Display` for the print materials. Empty for the colour reversal films, `negative_scan`, and `cine_look`. |
| `short_label` | The name without the brand, as the browser shows it. |
| `balance_light` | Only for a negative: the spectrum of the light that the film is balanced for, `D55` (daylight) or `T3200` (tungsten), for example `T3200` for `kodak_5219` (Vision3 500T). The colour reversal films have no `balance_light`. |
| `editor_value` | The `odt` property that the entry sets: `{"negative": "<id>"}` for a negative or a colour reversal film, `{"print_material": "<id>"}` for a print material. |

To select a film print, give `editor.set` on `odt` the method and the `editor_value` of a film
and of a print material in one value:

```bash
alcedo-cli --json call editor.set '{"field":"odt","value":{"method":"film_print","negative":"kodak_portra_400","print_material":"kodak_2383"},"note":"agent: Portra 400 on Vision 2383"}'
```

`odt` accepts the film print properties only with `"method": "film_print"`. When the photo has
method Film Print already, a write of one `editor_value` alone changes only that film or print
material. A colour reversal film has no print: it reads no `print_material`, and the stored print
material stays. Print material `negative_scan` selects Negative Scan: a film scanner reads the
negative, and the OpenDRT settings of `odt` show the positive. See
[Editor fields](editor_fields.md#film-print) for the properties of each form.

**Warnings**

When the film print resources of the installation are missing or damaged, `warnings` has one
entry with `code` `film_resources_unavailable` and the error text in `message`. The entries then
have no `balance_light`, and a render with method Film Print fails with the same error. Tell the
user that the installation is incomplete; use a film simulation LUT (`lut.list`) in its place only
when the user agrees.

**Errors**

- `-32602` `/list`: not `negative`, `reversal`, or `print`.

**Example**

```bash
alcedo-cli --json call film.list '{"list":"negative","query":"portra"}'
```

```json
{"films":[{"balance_light":"D55","brand":"Kodak","editor_value":{"negative":"kodak_portra_400"},"family":"Photo","id":"kodak_portra_400","list":"negative","name":"Kodak Portra 400","short_label":"Portra 400"},{"balance_light":"D55","brand":"Kodak","editor_value":{"negative":"kodak_portra_160"},"family":"Photo","id":"kodak_portra_160","list":"negative","name":"Kodak Portra 160","short_label":"Portra 160"},{"balance_light":"D55","brand":"Kodak","editor_value":{"negative":"kodak_portra_800"},"family":"Photo","id":"kodak_portra_800","list":"negative","name":"Kodak Portra 800","short_label":"Portra 800"}],"total":3,"warnings":[]}
```
