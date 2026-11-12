# Library commands

## `library.import`

<!-- BEGIN GENERATED: library.import -->
Changes state: yes. In a GUI session it needs agent control (`control.acquire`).

Imports the files 'paths', or the supported files of 'folder' (with its subfolders when 'recursive', the default), into the current folder of the open project. Returns a task id for tasks.wait as soon as the import starts.

**Parameters**

| Name | Type | Required | Default | Notes |
| --- | --- | --- | --- | --- |
| `folder` | string | no |  | A folder to import. |
| `paths` | array of string | no |  | at least 1 item(s). Files to import. |
| `recursive` | boolean | no | `true` | Include the subfolders of 'folder'. |

**Result**

| Field | Type | Always | Notes |
| --- | --- | --- | --- |
| `task_id` | string | yes |  |
<!-- END GENERATED: library.import -->

Give `folder` or `paths`. Wait for the task before you list the photos: `tasks.wait` with the
`task_id`, or with `idle: true`.

**Errors**

- `-32602`: `give exactly one of paths and folder`.
- `-32602` `/folder` or `/paths/<n>`: the folder or file does not exist.
- `-32001`: `No project is open.`
- `-32005`: `An import is already running.` Wait with `tasks.wait`, then try again.

**Example**

```bash
alcedo-cli --json call library.import '{"folder":"D:/Photos/2026-trip"}'
alcedo-cli --json call tasks.wait '{"task_id":"import-1"}'
```

```json
{"task_id":"import-1"}
{"counts":{"completed":1,"excluded":0,"failed":0,"total":1,"unsupported":0},"kind":"import","message":"Import complete: 1 imported, 0 not selected, 0 unsupported, 0 failed","progress":100,"state":"succeeded","task_id":"import-1"}
```

## `library.folders`

<!-- BEGIN GENERATED: library.folders -->
Changes state: no.

Returns the folder tree of the open project as a list, parents before children. The root folder is first.

**Parameters**

No parameters other than `timeout_ms`.

**Result**

| Field | Type | Always | Notes |
| --- | --- | --- | --- |
| `folders` | array | yes |  |
<!-- END GENERATED: library.folders -->

**Errors**

- `-32001`: no project is loaded.

**Example**

```bash
alcedo-cli --json call library.folders
```

```json
{"folders":[{"depth":0,"folder_id":0,"name":"","parent_id":0,"path":"/"}]}
```

## `library.list`

<!-- BEGIN GENERATED: library.list -->
Changes state: no.

Returns one page of the photos of a folder (the root folder by default) in the order of 'sort', then by element id. 'color_label' keeps the photos with that code and 'deleted' the photos with (true) or without (false) the Delete mark. 'camera', 'lens', 'capture_date', 'rating', 'import_date', and 'label' keep the photos of that library.stats bucket. Together the parameters keep the photos that match all of them. 'total' is the photo count of the folder that matches.

**Parameters**

| Name | Type | Required | Default | Notes |
| --- | --- | --- | --- | --- |
| `camera` | string | no |  | Only photos of this library.stats camera bucket; '(unknown)' is the bucket without a camera model. |
| `capture_date` | string | no |  | Only photos of this library.stats capture_date bucket (YYYY-MM-DD); the empty text is the bucket without a capture date. |
| `color_label` | `red` \| `orange` \| `yellow` \| `green` \| `blue` \| `purple` \| `gray` | no |  | Only photos with this code. |
| `deleted` | boolean | no |  | Only photos with (true) or without (false) the Delete mark. |
| `descending` | boolean | no | `false` |  |
| `folder_id` | integer | no |  | 0 to 4294967295. A folder id from library.folders. |
| `import_date` | string | no |  | Only photos of this library.stats import_date bucket (YYYY-MM-DD in 'time_zone'); the empty text is the bucket without an import time. Needs 'time_zone'. |
| `label` | string | no |  | Only photos of this library.stats label bucket: a semantic label key of the active model. |
| `lens` | string | no |  | Only photos of this library.stats lens bucket; '(unknown)' is the bucket without a lens. |
| `limit` | integer | no | `100` | 1 to 1000. |
| `offset` | integer | no | `0` | at least 0. |
| `rating` | string | no |  | Only photos of this library.stats rating bucket; a text that is not a number is the bucket without a rating. |
| `sort` | `none` \| `capture_time` \| `import_time` \| `camera_model` \| `lens` \| `rating` \| `labels` \| `edit_time` | no | `"none"` |  |
| `time_zone` | string | no |  | The IANA time zone of the import days: 'import_date' and the import_date buckets of library.stats need it. |

**Result**

| Field | Type | Always | Notes |
| --- | --- | --- | --- |
| `items` | array of object | yes |  |
| `items[].color_labels` | array of `red` \| `orange` \| `yellow` \| `green` \| `blue` \| `purple` \| `gray` | yes | The color label codes of the photo in code order. |
| `items[].delete_mark` | boolean | yes | The Delete mark. The mark changes nothing on disk. |
| `items[].element_id` | integer | yes |  |
| `items[].file_name` | string | yes |  |
| `items[].image_id` | integer | yes |  |
| `items[].rating` | integer | yes |  |
| `offset` | integer | yes |  |
| `total` | integer | yes |  |
<!-- END GENERATED: library.list -->

An unknown `folder_id` gives an empty page. To read all photos, repeat with `offset` until
`offset` + the item count reaches `total`.

Each item carries the marks of the photo: `rating`, `color_labels` (the code keys in code order,
see `library.color_labels`), and `delete_mark`. `color_label` keeps the photos with one code;
`deleted: true` keeps the photos with the Delete mark and `deleted: false` the photos without
it.

`camera`, `lens`, `capture_date`, `rating`, `import_date`, and `label` keep the photos of one
`library.stats` bucket: pass the `label` of the bucket as `library.stats` returns it. The
filter is the one of the Library statistics bar, so a bucket label selects `count` photos.
`import_date` needs `time_zone`, the IANA zone of the import days. All filter parameters
together keep the photos that match each of them. `total` counts the photos that match.

**Errors**

- `-32602` `/color_label`: an unknown code key. Keys are lower case: `red`, `orange`, `yellow`,
  `green`, `blue`, `purple`, `gray`.
- `-32602`: `import_date` without `time_zone`, or an `import_date` that is not a
  `YYYY-MM-DD` day.
- `-32001`: no project is loaded.

**Example**

```bash
alcedo-cli --json call library.list '{"limit":10}'
alcedo-cli --json call library.list '{"deleted":true}'
alcedo-cli --json call library.list '{"camera":"ILCE-7M3","limit":10}'
```

```json
{"items":[{"color_labels":[],"delete_mark":false,"element_id":1,"file_name":"DSC0027.ARW","image_id":1,"rating":0},{"color_labels":["red","blue"],"delete_mark":false,"element_id":2,"file_name":"DSC00800.ARW","image_id":2,"rating":0},{"color_labels":[],"delete_mark":true,"element_id":3,"file_name":"DSC06683.dng","image_id":3,"rating":0}],"offset":0,"total":3}
{"items":[{"color_labels":[],"delete_mark":true,"element_id":3,"file_name":"DSC06683.dng","image_id":3,"rating":0}],"offset":0,"total":1}
{"items":[{"color_labels":[],"delete_mark":false,"element_id":1,"file_name":"DSC0135.ARW","image_id":1,"rating":0}],"offset":0,"total":1}
```

## `library.stats`

<!-- BEGIN GENERATED: library.stats -->
Changes state: no.

Returns the statistics of the photos of a folder (the root folder by default) that the Library statistics bar shows: the photos of each capture_date, camera, lens, label, and rating bucket, of each color label code, and with the Delete mark. With 'time_zone' it also returns the import_date buckets. The filter parameters are the ones of library.list. A bucket label selects its photos in the bucket parameter of library.list and library.stats.

**Parameters**

| Name | Type | Required | Default | Notes |
| --- | --- | --- | --- | --- |
| `camera` | string | no |  | Only photos of this library.stats camera bucket; '(unknown)' is the bucket without a camera model. |
| `capture_date` | string | no |  | Only photos of this library.stats capture_date bucket (YYYY-MM-DD); the empty text is the bucket without a capture date. |
| `color_label` | `red` \| `orange` \| `yellow` \| `green` \| `blue` \| `purple` \| `gray` | no |  | Only photos with this code. |
| `deleted` | boolean | no |  | Only photos with (true) or without (false) the Delete mark. |
| `folder_id` | integer | no |  | 0 to 4294967295. A folder id from library.folders. |
| `import_date` | string | no |  | Only photos of this library.stats import_date bucket (YYYY-MM-DD in 'time_zone'); the empty text is the bucket without an import time. Needs 'time_zone'. |
| `label` | string | no |  | Only photos of this library.stats label bucket: a semantic label key of the active model. |
| `lens` | string | no |  | Only photos of this library.stats lens bucket; '(unknown)' is the bucket without a lens. |
| `rating` | string | no |  | Only photos of this library.stats rating bucket; a text that is not a number is the bucket without a rating. |
| `time_zone` | string | no |  | The IANA time zone of the import days: 'import_date' and the import_date buckets of library.stats need it. |

**Result**

| Field | Type | Always | Notes |
| --- | --- | --- | --- |
| `camera` | array of object | yes | Camera models; '(unknown)' is the photos without a camera model. |
| `camera[].count` | integer | yes |  |
| `camera[].label` | string | yes |  |
| `capture_date` | array of object | yes | Capture days (YYYY-MM-DD); the empty label is the photos without a capture date. |
| `capture_date[].count` | integer | yes |  |
| `capture_date[].label` | string | yes |  |
| `color_labels` | array of object | yes | The photos of each color label code, in code order. |
| `color_labels[].code` | `red` \| `orange` \| `yellow` \| `green` \| `blue` \| `purple` \| `gray` | yes |  |
| `color_labels[].count` | integer | yes |  |
| `delete_mark` | integer | yes | The photos with the Delete mark. |
| `import_date` | array of object | no | Import days (YYYY-MM-DD) in 'time_zone'; only with 'time_zone'. |
| `import_date[].count` | integer | yes |  |
| `import_date[].label` | string | yes |  |
| `label` | array of object | yes | Semantic label keys of the active model. |
| `label[].count` | integer | yes |  |
| `label[].label` | string | yes |  |
| `lens` | array of object | yes | Lenses; '(unknown)' is the photos without a lens. |
| `lens[].count` | integer | yes |  |
| `lens[].label` | string | yes |  |
| `rating` | array of object | yes | Ratings. |
| `rating[].count` | integer | yes |  |
| `rating[].label` | string | yes |  |
| `total` | integer | yes | The photos of the folder that match. |
<!-- END GENERATED: library.stats -->

Each dimension lists its buckets in the order of the statistics bar, each with its `label` and
its photo `count`. A `label` selects the photos of its bucket in the parameter of the same name
of `library.list` and `library.stats`. `(unknown)` is the camera or lens bucket of the photos
without that value; the empty `label` is the capture day or import day bucket of the photos
without that value. `label` holds the semantic label keys of the active model of the project.
`color_labels` lists the seven codes in code order. The filter parameters are the ones of
`library.list`; `total` and every bucket count the photos that match them.

**Errors**

- `-32602`: `import_date` without `time_zone`, or an `import_date` that is not a
  `YYYY-MM-DD` day.
- `-32007`: a `time_zone` that the database does not know.
- `-32001`: no project is loaded.

**Example**

```bash
alcedo-cli --json call library.stats '{"time_zone":"America/New_York"}'
```

```json
{"camera":[{"count":1,"label":"ILCE-7M3"}],"capture_date":[{"count":1,"label":"2022-09-18"}],"color_labels":[{"code":"red","count":0},{"code":"orange","count":0},{"code":"yellow","count":0},{"code":"green","count":0},{"code":"blue","count":0},{"code":"purple","count":0},{"code":"gray","count":0}],"delete_mark":0,"import_date":[{"count":1,"label":"2026-10-04"}],"label":[],"lens":[{"count":1,"label":"FE 28mm F2"}],"rating":[{"count":1,"label":"0"}],"total":1}
```

## `library.thumbnail`

<!-- BEGIN GENERATED: library.thumbnail -->
Changes state: no.

Renders the library thumbnail of a photo and writes it as a PNG file whose long edge is 'long_edge'. 'out' must end in .png and must not exist: the command creates a new file and does not replace an existing one.

**Parameters**

| Name | Type | Required | Default | Notes |
| --- | --- | --- | --- | --- |
| `element_id` | integer | yes |  | 1 to 4294967295. |
| `long_edge` | integer | no | `512` | 16 to 2048. |
| `out` | string | yes |  | The new PNG file; it must not exist. |

**Result**

| Field | Type | Always | Notes |
| --- | --- | --- | --- |
| `height` | integer | yes |  |
| `path` | string | yes |  |
| `width` | integer | yes |  |
<!-- END GENERATED: library.thumbnail -->

The thumbnail shows the committed edits of the photo. Edits of the open editor image show after
the editor commits them (`editor.close`, `project.save`). The library keeps a thumbnail cache,
so a thumbnail made just after an edit can still show the earlier edits. To see the current
edits of the open photo, use `render.preview`.

**Errors**

- `-32602` `/element_id`: unknown element id.
- `-32602` `/out`: the path does not end in `.png`, or a file, folder, or link has the path. The
  command does not replace it and renders nothing. Give a new path.
- `-32007`: the render or the PNG write failed. The command removes the file that it created.

**Example**

```bash
alcedo-cli --json call library.thumbnail '{"element_id":2,"out":"D:/Photos/thumbs/DSC00800.png","long_edge":256}'
```

```json
{"height":171,"path":"D:/Photos/thumbs/DSC00800.png","width":256}
```

## `library.thumbnails`

<!-- BEGIN GENERATED: library.thumbnails -->
Changes state: no.

Renders the library thumbnails of 'element_ids' and writes each as the PNG file <element_id>.png in 'out_dir', with the long edge 'long_edge'. Answers when every thumbnail is written or has failed: each item has 'path', 'width', and 'height', or 'error'. A file that exists is not replaced; its item has 'error'.

**Parameters**

| Name | Type | Required | Default | Notes |
| --- | --- | --- | --- | --- |
| `element_ids` | array of integer | yes |  | 1 to 1000 items; each item at least 1. |
| `long_edge` | integer | no | `512` | 16 to 2048. |
| `out_dir` | string | yes |  | Folder of the PNG files. |

**Result**

| Field | Type | Always | Notes |
| --- | --- | --- | --- |
| `failed_count` | integer | yes |  |
| `items` | array of object | yes |  |
| `items[].element_id` | integer | yes |  |
| `items[].error` | string | no |  |
| `items[].height` | integer | no |  |
| `items[].path` | string | no |  |
| `items[].width` | integer | no |  |
| `written_count` | integer | yes |  |
<!-- END GENERATED: library.thumbnails -->

The thumbnails of many photos in one command, for example for a contact sheet. The files are
named by the element id and show the committed edits, as `library.thumbnail` does. Several
thumbnails render at the same time; the answer comes when the last one is written or has
failed. A photo whose thumbnail fails has `error` in its item and does not fail the command.
Give a `timeout_ms` that fits the number of photos: a thumbnail that is not in the cache needs
a RAW decode.

**Errors**

- `-32602` `/element_ids`: unknown ids (`data.unknown_ids` lists them; nothing is written), or
  more than 1000 ids.
- `-32602` `/out_dir`: the folder cannot be created.
- `-32001`: no project is loaded.
- `-32006`: the thumbnails did not finish within `timeout_ms`. The files written so far stay.

A file `<element_id>.png` that exists in `out_dir` is not replaced: only the item of that photo
has `error`, and the other items continue. Use a new folder, or remove the old files first.

**Example**

```bash
alcedo-cli --json call library.thumbnails '{"element_ids":[2,6],"out_dir":"D:/Photos/thumbs","long_edge":256}'
```

```json
{"failed_count":0,"items":[{"element_id":2,"height":256,"path":"D:/Photos/thumbs/2.png","width":171},{"element_id":6,"height":256,"path":"D:/Photos/thumbs/6.png","width":171}],"written_count":2}
```

## `library.info`

<!-- BEGIN GENERATED: library.info -->
Changes state: no.

Returns the source file, the marks (rating, color_labels, delete_mark), and the capture values of 'element_ids', in that order. The capture values come from the metadata that the import read: capture_time, camera_make, camera_model, lens, focal_mm, aperture, shutter, shutter_seconds, iso, width, and height. A value that the metadata does not have is left out of the item.

**Parameters**

| Name | Type | Required | Default | Notes |
| --- | --- | --- | --- | --- |
| `element_ids` | array of integer | yes |  | 1 to 1000 items; each item at least 1. |

**Result**

| Field | Type | Always | Notes |
| --- | --- | --- | --- |
| `items` | array of object | yes |  |
| `items[].aperture` | number | no | The f-number. |
| `items[].camera_make` | string | no |  |
| `items[].camera_model` | string | no |  |
| `items[].capture_time` | string | no | YYYY-MM-DD HH:MM:SS by the camera clock. |
| `items[].color_labels` | array of `red` \| `orange` \| `yellow` \| `green` \| `blue` \| `purple` \| `gray` | yes | The color label codes of the photo in code order. |
| `items[].delete_mark` | boolean | yes | The Delete mark. The mark changes nothing on disk. |
| `items[].element_id` | integer | yes |  |
| `items[].file_name` | string | yes |  |
| `items[].file_path` | string | no | The source file of the photo. |
| `items[].focal_mm` | number | no | The real focal length in mm. |
| `items[].height` | integer | no |  |
| `items[].image_id` | integer | yes |  |
| `items[].iso` | integer | no |  |
| `items[].lens` | string | no |  |
| `items[].metadata_error` | string | no | Why the metadata cannot be read; the item then has only the library columns. |
| `items[].rating` | integer | yes |  |
| `items[].shutter` | string | no | The exposure time, for example 1/250s. |
| `items[].shutter_seconds` | number | no |  |
| `items[].width` | integer | no | The image width in pixels. |
<!-- END GENERATED: library.info -->

The source file and the capture values of photos, for a contact sheet label or to tell similar
photos apart. The values come from the metadata that the import read; a camera or a file that
does not record a value leaves it out of the item. `capture_time` is the camera clock without a
time zone. `width` and `height` are the size of the image as the metadata gives it. The command
gives no focus point: each camera maker records it in its own way.

When the metadata of a photo cannot be read, its item has only the library fields and
`metadata_error`. The library fields are `element_id`, `image_id`, `file_name`, and the marks
`rating`, `color_labels`, and `delete_mark` (see `library.color_label` and
`library.delete_mark`).

**Errors**

- `-32602` `/element_ids`: unknown ids (`data.unknown_ids` lists them), or more than 1000 ids.
- `-32001`: no project is loaded.

**Example**

```bash
alcedo-cli --json call library.info '{"element_ids":[2,6]}'
```

```json
{"items":[{"aperture":2,"camera_make":"Sony","camera_model":"ILCE-7M3","capture_time":"2022-09-18 21:36:18","color_labels":["red"],"delete_mark":false,"element_id":2,"file_name":"DSC0027.ARW","file_path":"D:/Photos/2022-canada/DSC0027.ARW","focal_mm":28,"height":6024,"image_id":2,"iso":80,"lens":"FE 28mm F2","rating":0,"shutter":"1/1000s","shutter_seconds":0.001,"width":4024},{"aperture":6.3,"camera_make":"Sony","camera_model":"Sony ILCE-1","capture_time":"2023-10-22 21:08:01","color_labels":[],"delete_mark":true,"element_id":6,"file_name":"DSC06683.dng","file_path":"D:/Photos/2023-yosemite/DSC06683.dng","focal_mm":50,"height":8672,"image_id":6,"iso":200,"lens":"FE 20-70mm F4 G","rating":0,"shutter":"1/800s","shutter_seconds":0.00125,"width":5784}]}
```

For many photos at once, see the contact sheet script in the skill (`scripts/contact_sheet.py`).

## `library.rate`

<!-- BEGIN GENERATED: library.rate -->
Changes state: yes. In a GUI session it needs agent control (`control.acquire`).

Sets the star rating (0 to 5) of 'element_ids'. One photo is rated at once and the result holds 'applied_count'. Several photos use the batch save, and the result holds the 'task_id' of the save task.

**Parameters**

| Name | Type | Required | Default | Notes |
| --- | --- | --- | --- | --- |
| `element_ids` | array of integer | yes |  | at least 1 item(s); each item at least 1. |
| `rating` | integer | yes |  | 0 to 5. |

**Result**

The schema lists no fields; see the description and the example.
<!-- END GENERATED: library.rate -->

**Errors**

- `-32602` `/element_ids`: unknown ids; `data.unknown_ids` lists them. Nothing is rated.
- `-32602` `/rating`: the rating is not 0 to 5.

**Example**

```bash
alcedo-cli --json call library.rate '{"element_ids":[3],"rating":2}'
alcedo-cli --json call library.rate '{"element_ids":[1,2],"rating":4}'
```

```json
{"applied_count":1,"rating":2}
{"rated_count":2,"rating":4,"task_id":"bgtask-2"}
```

## `library.color_label`

<!-- BEGIN GENERATED: library.color_label -->
Changes state: yes. In a GUI session it needs agent control (`control.acquire`).

Sets ('on': true) or clears ('on': false) one color label code on every photo of 'element_ids'. The other codes of each photo stay. The batch save runs as a task: the result holds its 'task_id' for tasks.wait. A batch while another mark batch saves, or a photo that a running delete holds, is rejected.

**Parameters**

| Name | Type | Required | Default | Notes |
| --- | --- | --- | --- | --- |
| `code` | `red` \| `orange` \| `yellow` \| `green` \| `blue` \| `purple` \| `gray` | yes |  | The color label code. |
| `element_ids` | array of integer | yes |  | at least 1 item(s); each item at least 1. |
| `on` | boolean | yes |  |  |

**Result**

| Field | Type | Always | Notes |
| --- | --- | --- | --- |
| `code` | string | yes |  |
| `marked_count` | integer | yes |  |
| `on` | boolean | yes |  |
| `task_id` | string | yes |  |
<!-- END GENERATED: library.color_label -->

A photo can have any number of the seven color label codes. The command adds (`on: true`) or
removes (`on: false`) one code on every photo and keeps the other codes of each photo. The
project stores the codes only; the name of a code (`library.color_labels`) is a setting of
the computer. The Library shows the new codes at once; wait for the `task_id` before you read
them back with `library.list` or `library.info`.

**Errors**

- `-32602` `/code`: an unknown code key. Keys are lower case.
- `-32602` `/element_ids`: unknown ids; `data.unknown_ids` lists them. Nothing changes.
- `-32002`: another mark batch (color label or Delete mark) is still saving, or a running delete
  holds one of the photos. `data.reason` names it, for example `Image marks are still being
  saved.` Wait for the earlier task and try again. Nothing changes.

**Example**

```bash
alcedo-cli --json call library.color_label '{"element_ids":[2,5],"code":"red","on":true}'
alcedo-cli --json call tasks.wait '{"task_id":"bgtask-3"}'
```

```json
{"code":"red","marked_count":2,"on":true,"task_id":"bgtask-3"}
```

## `library.delete_mark`

<!-- BEGIN GENERATED: library.delete_mark -->
Changes state: yes. In a GUI session it needs agent control (`control.acquire`).

Sets ('on': true) or clears ('on': false) the Delete mark of every photo of 'element_ids'. The mark changes nothing on disk; library.delete is the separate step that deletes photos. The batch save runs as a task: the result holds its 'task_id' for tasks.wait. A batch while another mark batch saves, or a photo that a running delete holds, is rejected.

**Parameters**

| Name | Type | Required | Default | Notes |
| --- | --- | --- | --- | --- |
| `element_ids` | array of integer | yes |  | at least 1 item(s); each item at least 1. |
| `on` | boolean | yes |  |  |

**Result**

| Field | Type | Always | Notes |
| --- | --- | --- | --- |
| `marked_count` | integer | yes |  |
| `on` | boolean | yes |  |
| `task_id` | string | yes |  |
<!-- END GENERATED: library.delete_mark -->

The Delete mark marks photos for a later delete. It changes nothing on disk and keeps the photo
in the project; the Library shows it under a dark cover with a trash icon. `library.delete` is
the separate step that removes photos from the project.

**Errors**

- `-32602` `/element_ids`: unknown ids; `data.unknown_ids` lists them. Nothing changes.
- `-32002`: another mark batch is still saving, or a running delete holds one of the photos.
  Nothing changes.

**Example**

```bash
alcedo-cli --json call library.delete_mark '{"element_ids":[6],"on":true}'
```

```json
{"marked_count":1,"on":true,"task_id":"bgtask-4"}
```

## `library.color_labels`

<!-- BEGIN GENERATED: library.color_labels -->
Changes state: no.

Returns the seven color label codes in code order (red, orange, yellow, green, blue, purple, gray) with their names. The name of a code is a setting of the computer that every project shares; the code key never changes.

**Parameters**

No parameters other than `timeout_ms`.

**Result**

| Field | Type | Always | Notes |
| --- | --- | --- | --- |
| `codes` | array of object | yes |  |
| `codes[].code` | `red` \| `orange` \| `yellow` \| `green` \| `blue` \| `purple` \| `gray` | yes |  |
| `codes[].color` | string | yes | The display color as #RRGGBB. |
| `codes[].default_name` | string | yes | The color name in the application language. |
| `codes[].index` | integer | yes | The position of the code, 0 (red) to 6 (gray). |
| `codes[].name` | string | yes | The name that the Library shows: the user name, or the color name. |
| `codes[].renamed` | boolean | yes | True when the code has a user name. |
<!-- END GENERATED: library.color_labels -->

The seven codes in code order: `red`, `orange`, `yellow`, `green`, `blue`, `purple`, `gray`. The
key of a code never changes. `name` is what the Library shows: the user name of the code, or the
color name in the application language when the code has no user name (`renamed: false`). The
names are shared by every project on the computer. Use the names to understand what the user
means by a label, for example "Client picks", and the keys in the other commands.

**Example**

```bash
alcedo-cli --json call library.color_labels
```

```json
{"codes":[{"code":"red","color":"#E5534B","default_name":"Red","index":0,"name":"Client picks","renamed":true},{"code":"orange","color":"#E8863A","default_name":"Orange","index":1,"name":"Orange","renamed":false},{"code":"yellow","color":"#D8B43A","default_name":"Yellow","index":2,"name":"Yellow","renamed":false},{"code":"green","color":"#4FAE6B","default_name":"Green","index":3,"name":"Green","renamed":false},{"code":"blue","color":"#4C8DDB","default_name":"Blue","index":4,"name":"Blue","renamed":false},{"code":"purple","color":"#9B6BD3","default_name":"Purple","index":5,"name":"Purple","renamed":false},{"code":"gray","color":"#8C8C8C","default_name":"Gray","index":6,"name":"Gray","renamed":false}]}
```

## `library.color_label_name.set`

<!-- BEGIN GENERATED: library.color_label_name.set -->
Changes state: yes. In a GUI session it needs agent control (`control.acquire`).

Sets the user name of a color label code for every project on the computer. Line breaks and tabs become spaces, other control characters and bidirectional controls are removed, and the name is trimmed and cut to 40 Unicode code points; an empty name gives the code its color name back. Returns the library.color_labels item of the code, whose name is the stored name.

**Parameters**

| Name | Type | Required | Default | Notes |
| --- | --- | --- | --- | --- |
| `code` | `red` \| `orange` \| `yellow` \| `green` \| `blue` \| `purple` \| `gray` | yes |  | The color label code. |
| `name` | string | yes |  |  |

**Result**

| Field | Type | Always | Notes |
| --- | --- | --- | --- |
| `code` | `red` \| `orange` \| `yellow` \| `green` \| `blue` \| `purple` \| `gray` | yes |  |
| `color` | string | yes | The display color as #RRGGBB. |
| `default_name` | string | yes | The color name in the application language. |
| `index` | integer | yes | The position of the code, 0 (red) to 6 (gray). |
| `name` | string | yes | The name that the Library shows: the user name, or the color name. |
| `renamed` | boolean | yes | True when the code has a user name. |
<!-- END GENERATED: library.color_label_name.set -->

Renames a code for every project on the computer, like Settings > Library > Color Labels. Rename
a code only when the user asks for it. A name is one line: line breaks and tabs become spaces,
and other control characters are removed. The name is trimmed and cut to 40 Unicode code points,
so a code point outside the Basic Multilingual Plane (most emoji) stays whole at the cut. The `name` of the answer is the stored name. An empty name removes
the user name, so the code shows its color name again.

**Errors**

- `-32602` `/code`: an unknown code key.
- `-32003`, `-32004`: GUI session without agent control.

**Example**

```bash
alcedo-cli --json call library.color_label_name.set '{"code":"red","name":"Client picks"}'
alcedo-cli --json call library.color_label_name.set '{"code":"red","name":""}'
```

```json
{"code":"red","color":"#E5534B","default_name":"Red","index":0,"name":"Client picks","renamed":true}
{"code":"red","color":"#E5534B","default_name":"Red","index":0,"name":"Red","renamed":false}
```

## `library.delete`

<!-- BEGIN GENERATED: library.delete -->
Changes state: yes. In a GUI session it needs agent control (`control.acquire`).

Deletes 'element_ids'. With scope 'project' the photos leave the project; this needs the root folder as the current folder. With scope 'album' they leave the current album. Answers -32002 (rejected) while a task holds the photos: a mark, rating, or paste adjustments batch that is saving, or another delete. Send it again after tasks.wait. Other start failures answer -32007 (failed).

**Parameters**

| Name | Type | Required | Default | Notes |
| --- | --- | --- | --- | --- |
| `element_ids` | array of integer | yes |  | at least 1 item(s); each item at least 1. |
| `scope` | `project` \| `album` | yes |  |  |

**Result**

| Field | Type | Always | Notes |
| --- | --- | --- | --- |
| `deleted_ids` | array | yes |  |
| `failed_ids` | array | yes |  |
<!-- END GENERATED: library.delete -->

`library.delete` removes the photos from the project or the album. It does not delete the
image files on the disk. To mark photos for a later delete that the user reviews first, use
`library.delete_mark`.

**Errors**

- `-32602` `/element_ids`: unknown ids; `data.unknown_ids` lists them. Nothing is deleted.
- `-32602` `/scope`: `scope` is missing.
- `-32002`: the scope does not fit the current folder, for example `The current folder gives
  the delete scope 'album', not 'project'.` Change the current folder, then send the command
  again.
- `-32002`: a task holds the photos, for example `Image marks are being saved.` while a
  `library.color_label`, `library.delete_mark`, or `library.rate` batch of these photos saves,
  while an adjustments paste runs, or while another delete runs. Wait for the task (`tasks.wait {"idle": true}`), then send the
  same command again.
- `-32007`: the delete did not start for another reason, such as a running import or export,
  or no photo was deleted. `data.reason` gives the reason.

When some photos cannot be deleted, the command succeeds and `failed_ids` lists them.

**Example**

```bash
alcedo-cli --json call library.delete '{"element_ids":[3],"scope":"project"}'
```

```json
{"deleted_ids":[3],"failed_ids":[],"message":"Deleted 1 image(s)."}
```

## `library.selection.get`

<!-- BEGIN GENERATED: library.selection.get -->
Changes state: no.

Returns the library selection of the GUI. The headless host has no selection.

**Parameters**

No parameters other than `timeout_ms`.

**Result**

| Field | Type | Always | Notes |
| --- | --- | --- | --- |
| `items` | array | yes |  |
<!-- END GENERATED: library.selection.get -->

**Errors**

- `-32001`: headless host.

**Example** (GUI session)

```bash
alcedo-cli --session gui --json call library.selection.get
```

```json
{"items":[{"element_id":41,"file_name":"DSC02240.ARW","image_id":41}]}
```

Headless:

```json
{"error":{"code":-32001,"data":{"reason":"The library selection exists only in the GUI."},"message":"The library selection exists only in the GUI."}}
```

## `library.selection.set`

<!-- BEGIN GENERATED: library.selection.set -->
Changes state: yes. In a GUI session it needs agent control (`control.acquire`).

Replaces the library selection of the GUI with 'element_ids'. The headless host has no selection.

**Parameters**

| Name | Type | Required | Default | Notes |
| --- | --- | --- | --- | --- |
| `element_ids` | array of integer | yes |  | each item at least 1. |

**Result**

| Field | Type | Always | Notes |
| --- | --- | --- | --- |
| `items` | array | yes |  |
<!-- END GENERATED: library.selection.set -->

An empty list clears the selection.

**Errors**

- `-32001`: headless host.
- `-32003`, `-32004`: GUI session without agent control.

**Example** (GUI session, with agent control)

```bash
alcedo-cli --session gui --json call library.selection.set '{"element_ids":[41]}'
```

```json
{"items":[{"element_id":41,"file_name":"DSC02240.ARW","image_id":41}]}
```
