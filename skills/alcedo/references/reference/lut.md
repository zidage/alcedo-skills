# LUT commands

## `lut.list`

<!-- BEGIN GENERATED: lut.list -->
Changes state: no.

Lists the LUTs of the LUT library with the rules of the LUT browser. A 'query' matches the name, file name, aliases, source, film, print, and path, and sorts the matches by search rank; without a query the LUTs are sorted by name. 'editor_value' of a LUT is the value for editor.set on the 'lut' field that the LUT browser applies: the reference, the name, and the remembered encodings. A LUT that the grade cannot apply has 'applicable' false and no 'editor_value'. Waits while the library loads or refreshes its inventory. Needs no open project.

**Parameters**

| Name | Type | Required | Default | Notes |
| --- | --- | --- | --- | --- |
| `category` | `general` \| `film_simulation` | no |  | Only LUTs of this category. |
| `favorites` | boolean | no |  | Only favorite LUTs. Default false. |
| `limit` | integer | no |  | 1 to 500. The number of LUTs to return. Default 50. |
| `offset` | integer | no |  | at least 0. The first LUT to return. Default 0. |
| `package` | string | no |  | Only LUTs of this installed official package, for example spectral_film_lut. An empty string selects the LUTs outside packages. |
| `query` | string | no |  | Search text, as in the search field of the LUT browser. |

**Result**

| Field | Type | Always | Notes |
| --- | --- | --- | --- |
| `has_more` | boolean | yes |  |
| `inventory_complete` | boolean | yes |  |
| `limit` | integer | yes |  |
| `luts` | array | yes |  |
| `offset` | integer | yes |  |
| `root` | string | yes |  |
| `total` | integer | yes |  |
<!-- END GENERATED: lut.list -->

`lut.list` reads the LUT library of Alcedo Studio: the user's own `.cube` files and the LUTs of
the installed official packages (Settings > LUT Library). It needs no open project. The first
call after the start of a session waits until the library has loaded its inventory.

Each item of `luts` has these fields. A field without a value is not in the item.

| Field | Notes |
| --- | --- |
| `entry_id` | The stable identity of the LUT, for example `official:spectral_film_lut/<lut id>` or `library:user/look.cube`. |
| `name` | The name that the LUT browser shows. An official film simulation is named by its film brand and stock. |
| `file_stem`, `path` | The file name without `.cube`, and the path relative to `root`. |
| `title` | The `TITLE` line of the file. |
| `official` | The file declares `origin: alcedo`. |
| `package` | The installed official package that holds the file. Not set for a file outside packages. |
| `category` | `general` or `film_simulation`. |
| `lut_id`, `source`, `film`, `print`, `print_option`, `variant` | The metadata of an official LUT. `film` and `print` have `id`, `name`, and `brand`; `print` also has `kind` (`film` or `paper`). |
| `input_space`, `output_space` | The color spaces that the metadata declares, for example `ACEScc`. |
| `display_requirement` | The output transform that the LUT was made for, for example `Use only with ACES 2.0 SDR 100 nits`. Information only: the LUT works with any display transform; judge the look in the preview. |
| `description` | The description of the metadata. |
| `lut_3d_size`, `lut_1d_size` | The table sizes. |
| `favorite` | The user marked the LUT as a favorite. |
| `applicable` | The grade can apply the LUT: a valid 3D table without a 1D shaper. |
| `header_error` | Why the file cannot be read. Such a LUT is not applicable. |
| `reference` | The tagged reference of the LUT for the `reference` property of the `lut` field. |
| `remembered_encodings` | The input and output encodings that the user saved for this LUT. |
| `editor_value` | Only for an applicable LUT: the complete value for `editor.set` on `lut`, as the LUT browser applies it. It has `reference`, `name`, and `input_encoding` and `output_encoding` (the remembered encodings, else `acescc`). |

To apply a LUT, give its `editor_value` to `editor.set` as is. Add `strength` (0 to 1) to the
value for a weaker look. A reference stays valid when the user moves the library to another
folder, and an official reference stays valid when the package is updated.

**Errors**

- `-32602` `/category`: not `general` or `film_simulation`.
- `-32602` `/limit`: less than 1 or more than 500.

**Example**

```bash
alcedo-cli --json call lut.list '{"query":"vision3 250d","category":"film_simulation","limit":1}'
```

```json
{"has_more":true,"inventory_complete":true,"limit":1,"luts":[{"applicable":true,"category":"film_simulation","editor_value":{"input_encoding":"acescc","name":"Kodak Vision3 250D 5207","output_encoding":"acescc","reference":{"kind":"official","lut_id":"spectral_film_lut:kodak_vision3_250d_5207:adx","package_id":"spectral_film_lut"}},"entry_id":"official:spectral_film_lut/spectral_film_lut:kodak_vision3_250d_5207:adx","favorite":false,"file_stem":"kodak_vision3_250d_5207__adx","film":{"brand":"Kodak","id":"kodak_vision3_250d_5207","name":"Vision3 250D 5207"},"input_space":"ACEScc","lut_3d_size":65,"lut_id":"spectral_film_lut:kodak_vision3_250d_5207:adx","name":"Kodak Vision3 250D 5207","official":true,"output_space":"ACEScc","package":"spectral_film_lut","path":"packages/spectral_film_lut/content/8843fa0ca4fc9d18e15155802b54223238a74740ff1fde639bcd72b7d9185ac0/kodak_vision3_250d_5207__adx.cube","reference":{"kind":"official","lut_id":"spectral_film_lut:kodak_vision3_250d_5207:adx","package_id":"spectral_film_lut"},"remembered_encodings":{"input_encoding":"acescc","output_encoding":"acescc"},"source":{"id":"spectral_film_lut","name":"Spectral Film LUT"},"title":"Kodak Vision3 250D 5207 negative -> ADX16 -> ACEScc LMT","variant":"adx"}],"offset":0,"root":"D:\\misc\\luts","total":11}
```

Apply the LUT to the photo that the editor has open. The value is the `editor_value` above:

```bash
alcedo-cli --json call editor.set '{"field":"lut","value":{"input_encoding":"acescc","name":"Kodak Vision3 250D 5207","output_encoding":"acescc","reference":{"kind":"official","lut_id":"spectral_film_lut:kodak_vision3_250d_5207:adx","package_id":"spectral_film_lut"}},"note":"agent: film look"}'
```

```json
{"field":"lut","head_commit":"8c7f9da6c06575392c60839279612656","value":{"input_encoding":"acescc","lutId":"spectral_film_lut:kodak_vision3_250d_5207:adx","lutName":"Kodak Vision3 250D 5207","ocio_lmt":"","output_encoding":"acescc","packageId":"spectral_film_lut","path":"","referenceKind":"official","strength":1}}
```
