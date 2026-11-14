# Editor fields

`editor.set`, `editor.batch_set`, and `editor.get` use these fields. The values are UI values:
the numbers that the editor panels show. A value outside the range, an unknown property, or an
unknown option is rejected with `-32602`; it is not clamped.

The **reset value** is the value of the panel reset. A photo without edits starts with the
default look of Alcedo Studio instead: exposure +1.5, contrast 15, saturation 30, and the other
fields at their reset values. Read the values with `editor.get` before you change them.

## Notes on the fields

- **Tone** (`exposure`, `contrast`, `highlights`, `shadows`, `white`, `black`): exposure is in
  stops (EV). The other tone fields are -100 to 100.
- **White balance:** `color_temp` is the white balance of the RAW decode. Its `mode` is
  `as_shot` (the camera white balance; `kelvin` and `tint` report it) or `custom` (your `kelvin`
  and `tint`). A write with `kelvin` or `tint` sets the mode to `custom`; write
  `{"mode":"as_shot"}` to go back to the camera white balance. `kelvin` is the color temperature
  of the light in the scene, so a higher `kelvin` makes the image warmer (more yellow) and a
  lower `kelvin` makes it cooler (more blue). Positive `tint` makes the image more magenta;
  negative `tint` makes it more green. Start from the as-shot values that `editor.get` returns
  and change them in steps of about 300 K and 5 tint. `grade_white_balance` is a second white
  balance in the color grade, after the RAW decode.
- **Crop and rotation:** `crop_rotate` holds the crop rectangle and the rotation:
  - `x` and `y` are the top-left corner of the crop and `width` and `height` its size, all as
    fractions of the image width and height. `y` goes down: `{"x":0.5,"y":0,"width":0.5,
    "height":0.5}` is the top-right quarter.
  - A positive `angle_degrees` turns the image clockwise. To level a horizon that rises to the
    right by 2 degrees (counterclockwise), add 2 to `angle_degrees`.
  - The editor keeps the rotated crop inside the image, so the value in the result can differ
    from the value you sent: use the returned value. A rotation makes the crop smaller; set
    the angle back to 0 and the crop to `{"x":0,"y":0,"width":1,"height":1}` to undo it.
- **Tone curve** (`curve`): four curves. `points` is the RGB curve, and `red`, `green`, and
  `blue` are the channel curves. Each curve is a list of 2 to 16 points `{"x":..,"y":..}` in the
  unit square, with `x` strictly increasing; `{"x":0,"y":0}` and `{"x":1,"y":1}` alone are the
  identity. The render applies the RGB curve to each channel, then the curve of the channel. A
  write gives one or more of the four curves and keeps the others: `{"points":[...]}` changes
  only the RGB curve, and `{"blue":[...]}` changes only the blue curve. `editor.get` gives
  `points` always and a channel curve only when it is not the identity. In a write, a curve can
  also be the id of a Tone Curve preset, for example `{"points":"cl_digital"}`: the write stores
  the points of the preset ([curve.presets](curve.md)). The reset value resets
  the four curves.
- **LUTs** (`lut`): a write gives the complete value. Use the `editor_value` of the LUT that
  [`lut.list`](lut.md) returns. `editor.get` gives `lut` in the same shape, with `strength`, so
  you can write the value from `editor.get` back with a change.
- **Input profile:** `input_profile` applies only to a raster image, not to a RAW image. A RAW
  image has no input profile: `editor.get` does not return the field, and `editor.set` on it
  answers `-32602`.
- **Display transform** (`odt`): `method` is `open_drt` (OpenDRT, the default), `aces_2_0`
  (ACES 2.0), or `film_print` (Film Print, the film simulation). See [Film print](#film-print).

## Film print

Method `film_print` of `odt` simulates film from its spectral data: the scene exposes a film, and
the film is printed on a print material, scanned (Negative Scan), or viewed on a light table (a
colour reversal film). [`film.list`](film.md) lists the films and print materials with their
names, brands, and families.

Select it with the method, the film, and the print material in one write:

```json
{"field":"odt","value":{"method":"film_print","negative":"kodak_portra_400","print_material":"kodak_2383"}}
```

The film print properties are accepted only with `"method": "film_print"`. A write that changes
the method follows the rule of the Display Transform panel: method `film_print` turns on
`film_grain` at 100 when it is 0 (a stored strength above 0 stays), and another method on a
photo with Film Print sets `film_grain` to 0. The rule is a second history commit, and the
result of `editor.set` lists both fields in `values`. When the same `editor.batch_set` writes
`film_grain`, the value of the batch is kept. The film print settings that the panel remembers
for the user are not applied: a write sets only the properties that it gives.

The film print has three forms. Each form reads these properties of `odt`:

| Form | Selected by | Properties that it reads | Output |
| --- | --- | --- | --- |
| Print | a negative (`list` `negative`) and a print material other than `negative_scan` | `negative`, `print_material`, `scene_light`, `light_spread`, `halation`, `enlarger_flare` | Rec. 709 SDR: `encoding_space` `rec709` and `peak_luminance` 100; `encoding_eotf` is one of the Rec. 709 values. Another space or peak is rejected. |
| Colour reversal film (light table) | a film of `list` `reversal` | `negative`, `scene_light`, `light_spread`, `halation`, `enlarger_flare` (here the flare of the loupe, which lifts the shadows of the slide); the stored `print_material` is not read | Rec. 709 SDR, as the print |
| Negative Scan | a negative and `print_material` `negative_scan` | `negative`, `scene_light`, `light_spread`, `halation`, the scan settings (`auto`, `auto_strength`, `auto_density`, `scan_contrast`, `scan_exposure_stops`, `cyan`, `magenta`, `yellow`, `black`), the scanner (`scanner_red_nm`, `scanner_green_nm`, `scanner_blue_nm`, `scanner_width_nm`, `scanner_light`), and the OpenDRT settings (`look_preset`, `tonescale_preset`, `creative_white`); no `enlarger_flare` | OpenDRT with the encodings of `odt` (`encoding_space`, `encoding_eotf`, `peak_luminance`), SDR or HDR |

What the properties do:

- `scene_light`: the light on the scene when the film is exposed. `as_shot` (the default) uses
  the color temperature of the RAW white balance; without a RAW white balance it renders as
  `reference`. `reference` is the light that the film is balanced for (`balance_light` of
  `film.list`). Another light gives the cast of real film: a tungsten film turns cool in
  daylight, and a daylight film turns warm in tungsten light. A write that selects
  `negative_scan` also selects `as_shot` unless it gives a `scene_light`.
- `light_spread`: the spread of light in the emulsion, the sharpness of the film. 1 is the
  sharpness of the datasheet; a larger value is softer.
- `halation`: light that the film base reflects back into the red layer, a red glow around bright
  lights. 1 is the standard strength.
- `enlarger_flare`: stray light of the enlarger lens on the paper; it turns the highlights of the
  print gray.
- Negative Scan: `auto` `off` keeps the cast of the scene light and the film; `neutral`, `warm`,
  and `cool` remove part of the cast (`auto_strength`). `scan_exposure_stops`,
  `scan_contrast`, and `cyan`, `magenta`, `yellow` change the inversion; `black` sets the film
  base to black. The scanner properties are the bands and the light of the virtual scanner; the
  defaults are an ideal scanner.

Two fields of their own act with the film print:

- `film_grain`: the grain of the film. With Film Print it is the grain in the dyes of the
  negative, and 100 is the granularity of the datasheet of the film; the range is 0 to 200.
- `film_format`: the size of the film frame, `16mm`, `35mm` (the default), or `70mm`. The image
  fills the frame, so a smaller frame makes the grain, the light spread, and the halation larger
  in the image.

## Field tables

These tables are generated from [editor_catalog.json](editor_catalog.json) (`editor.catalog`).

<!-- BEGIN GENERATED: editor-fields -->
### Scalar fields

| Field | Aliases | Panel | Range | Step | Decimals | Reset value |
| --- | --- | --- | --- | --- | --- | --- |
| `exposure` |  | tone | -10 to 10 | 0.01 | 2 | 0 |
| `contrast` |  | tone | -100 to 100 | 1 | 0 | 0 |
| `highlights` |  | tone | -100 to 100 | 1 | 0 | 0 |
| `shadows` |  | tone | -100 to 100 | 1 | 0 | 0 |
| `white` | `whites` | tone | -100 to 100 | 1 | 0 | 0 |
| `black` | `blacks` | tone | -100 to 100 | 1 | 0 | 0 |
| `saturation` |  | look | -100 to 100 | 1 | 0 | 0 |
| `vibrance` |  | look | -100 to 100 | 1 | 0 | 0 |
| `diffusion` |  | post | 0 to 100 | 1 | 0 | 0 |
| `clarity` |  | post | -100 to 100 | 1 | 0 | 0 |
| `sharpen` |  | post | 0 to 100 | 1 | 0 | 0 |
| `film_grain` |  | post | 0 to 200 | 1 | 0 | 0 |
| `halation` |  | post | 0 to 100 | 1 | 0 | 0 |

### Object fields

A write can give some of the properties; the others keep their values.

#### `film_format` (post panel)

| Property | Type | Range or values | Step | Decimals |
| --- | --- | --- | --- | --- |
| `film_format` | option | `16mm` (16mm), `35mm` (35mm), `70mm` (70mm) |  |  |

Reset value: `{"film_format": "35mm"}`

#### `raw_decode` (raw panel)

| Property | Type | Range or values | Step | Decimals |
| --- | --- | --- | --- | --- |
| `method` | option | `default` (Default), `legacy` (Legacy), `neural_engine` (Neural Engine) |  |  |
| `highlights_reconstruct` | boolean |  |  |  |

Reset value: `{"highlights_reconstruct": true, "method": "default"}`

#### `input_profile` (raw panel)

| Property | Type | Range or values | Step | Decimals |
| --- | --- | --- | --- | --- |
| `profile_override` | option | `auto` (Auto (from file)), `srgb` (sRGB), `display_p3` (Display P3), `adobe_rgb` (Adobe RGB), `rec2020` (Rec.2020), `prophoto` (ProPhoto), `linear_rec709` (Linear Rec.709) |  |  |

Reset value: `{"profile_override": "auto"}`

#### `lens_calib` (raw panel)

| Property | Type | Range or values | Step | Decimals |
| --- | --- | --- | --- | --- |
| `enabled` | boolean |  |  |  |
| `lens_maker` | string |  |  |  |
| `lens_model` | string |  |  |  |

Reset value: `{"enabled": false, "lens_maker": "", "lens_model": ""}`

#### `crop_rotate` (geometry panel)

| Property | Type | Range or values | Step | Decimals |
| --- | --- | --- | --- | --- |
| `x` | number | -1 to 1 | 0.001 | 3 |
| `y` | number | -1 to 1 | 0.001 | 3 |
| `width` | number | 0.0001 to 1 | 0.001 | 3 |
| `height` | number | 0.0001 to 1 | 0.001 | 3 |
| `angle_degrees` | number | -180 to 180 | 0.1 | 1 |
| `aspect_preset` | option | `free` (Free), `custom` (Custom), `ratio_2_35_1_35mm` (2.35:1 (35mm)), `ratio_1_1` (1:1), `ratio_16_9` (16:9), `ratio_1_9_1_imax` (1.9:1 (IMAX)), `ratio_1_85_1_dci` (1.85:1 (DCI)), `ratio_2_2_1_70mm` (2.2:1 (70mm)), `ratio_1_43_1_70mm_imax` (1.43:1 (70mm IMAX)), `ratio_4_3_35mm` (4:3 (35mm)), `ratio_1_5_1_native_vistavision` (1.5:1 (native or VistaVision)), `ratio_2_76_1_panavision_ultra` (2.76:1 (Panavision Ultra)) |  |  |
| `aspect_width` | number | 0.0001 to 100 | 0.01 | 2 |
| `aspect_height` | number | 0.0001 to 100 | 0.01 | 2 |

Reset value: `{"angle_degrees": 0, "aspect_height": 1, "aspect_preset": "free", "aspect_width": 1, "height": 1, "width": 1, "x": 0, "y": 0}`

#### `odt` (display panel)

| Property | Type | Range or values | Step | Decimals |
| --- | --- | --- | --- | --- |
| `method` | option | `aces_2_0` (ACES 2.0), `open_drt` (OpenDRT), `film_print` (Film Print) |  |  |
| `encoding_space` | option | `rec709` (Rec.709), `p3_d65` (P3-D65), `rec2020` (Rec.2020) |  |  |
| `encoding_eotf` | option | `bt1886` (BT.1886), `gamma_2_2` (Gamma 2.2), `srgb_piecewise` (sRGB), `st2084` (ST 2084 (PQ)), `hlg` (HLG) |  |  |
| `peak_luminance` | number | 100 to 1000 | 1 | 0 |
| `limiting_space` | option | `rec709` (Rec.709), `rec2020` (Rec.2020), `p3_d65` (P3-D65) |  |  |
| `look_preset` | option | `standard` (Standard), `arriba` (Arriba), `sylvan` (Sylvan), `colorful` (Colorful), `aery` (Aery), `dystopic` (Dystopic), `umbra` (Umbra), `custom` (Custom) |  |  |
| `tonescale_preset` | option | `use_look_preset` (Use Look Preset), `low_contrast` (Low Contrast), `medium_contrast` (Medium Contrast), `high_contrast` (High Contrast), `arriba_tonescale` (Arriba Tonescale), `sylvan_tonescale` (Sylvan Tonescale), `colorful_tonescale` (Colorful Tonescale), `aery_tonescale` (Aery Tonescale), `dystopic_tonescale` (Dystopic Tonescale), `umbra_tonescale` (Umbra Tonescale), `aces_1_x` (ACES 1.x), `aces_2_0` (ACES 2.0), `marvelous_tonscape` (Marvelous Tonscape), `dagrinchi_tonegroan` (Dagrinchi Tonegroan), `custom` (Custom) |  |  |
| `creative_white` | option | `use_look_preset` (Use Look Preset), `d93` (D93), `d75` (D75), `d65` (D65), `d60` (D60), `d55` (D55), `d50` (D50) |  |  |
| `negative` | option | `kodak_5207` (Kodak Vision3 250D 5207), `kodak_5219` (Kodak Vision3 500T 5219), `kodak_5213` (Kodak Vision3 200T 5213), `kodak_5203` (Kodak Vision3 50D 5203), `kodak_5206` (Kodak Verita 200D 5206), `kodak_portra_400` (Kodak Portra 400), `kodak_portra_160` (Kodak Portra 160), `kodak_portra_800` (Kodak Portra 800), `kodak_ektar_100` (Kodak Ektar 100), `kodak_gold_200` (Kodak Gold 200), `kodak_ultramax_400` (Kodak Ultramax 400), `fuji_eterna_500` (Fuji Eterna 500), `fuji_eterna_500_vivid` (Fuji Eterna 500 Vivid), `fuji_pro_400h` (Fuji Pro 400H), `fuji_pro_160c` (Fuji Pro 160C), `fuji_pro_160s` (Fuji Pro 160S), `fuji_natura_1600` (Fuji Natura 1600), `fuji_superia_xtra_400` (Fuji Superia X-Tra 400), `fuji_superia_reala` (Fuji Superia Reala), `fuji_c200` (Fuji C200), `kodak_5277` (Kodak Vision 320T 5277), `kodak_5293` (Kodak EXR 200T 5293), `kodak_exr_5248` (Kodak EXR 100T 5248), `kodak_5248` (Kodak 5248), `kodak_5247` (Kodak 5247), `kodak_5247_II` (Kodak 5247 II), `kodak_5250` (Kodak 5250), `kodak_vericolor_iii` (Kodak Vericolor III), `kodak_aerocolor` (Kodak Aerocolor IV 2460), `agfa_vista_100` (Agfa Vista 100), `fuji_velvia_50` (Fujichrome Velvia 50), `fuji_velvia_100` (Fujichrome Velvia 100), `fuji_provia_100f` (Fujichrome Provia 100F), `fuji_astia_100f` (Fujichrome Astia 100F), `kodak_ektachrome_e100` (Kodak Ektachrome E100) |  |  |
| `print_material` | option | `negative_scan` (Negative Scan), `cine_look` (Cine Look (2383)), `kodak_2383` (Kodak Vision 2383), `kodak_endura_premier` (Kodak Endura Premier Paper), `kodak_portra_endura` (Kodak Portra Endura Paper), `kodak_supra_endura` (Kodak Supra Endura Paper), `kodak_2393` (Kodak Vision Premier 2393), `fuji_3513di` (Fuji Eterna-CP Type 3513DI), `fuji_3523XD` (Fuji Eterna-CP 3523XD), `fuji_ca_maxima` (Fuji Crystal Archive Maxima), `fuji_ca_dpII` (Fuji Crystal Archive DPII), `fuji_ca_pdII` (Fuji Crystal Archive Pro PDII), `fuji_ca_super_c` (Fuji Crystal Archive Super Type C), `fujiflex_new` (Fujiflex Crystal Archive New Version), `fujiflex_old` (Fujiflex Crystal Archive Old Version), `kodak_duraflex_plus` (Kodak Duraflex Plus), `kodak_5383` (Kodak 5383), `kodak_5384` (Kodak 5384), `kodak_5381` (Kodak 5381), `kodak_exr_5386` (Kodak EXR 5386) |  |  |
| `scene_light` | option | `reference` (Reference), `as_shot` (As Shot), `daylight` (Daylight), `tungsten` (Tungsten), `fluorescent` (Fluorescent), `led` (LED), `sodium` (Sodium), `street_mixed` (Street Mixed), `street_sodium` (Street Sodium), `street_led` (Street LED), `interior_warm` (Interior Warm), `interior_office` (Interior Office) |  |  |
| `light_spread` | number | 0 to 3 | 0.01 | 2 |
| `halation` | number | 0 to 8 | 0.01 | 2 |
| `enlarger_flare` | number | 0 to 0.1 | 0.001 | 3 |
| `auto` | option | `off` (Off), `neutral` (Neutral), `warm` (Warm), `cool` (Cool) |  |  |
| `auto_strength` | number | 0 to 1 | 0.05 | 2 |
| `auto_density` | number | 0 to 1 | 0.05 | 2 |
| `scan_contrast` | number | 0.5 to 1.5 | 0.05 | 2 |
| `scan_exposure_stops` | number | -3 to 3 | 0.05 | 2 |
| `cyan` | number | -0.30000001192092896 to 0.30000001192092896 | 0.01 | 2 |
| `magenta` | number | -0.30000001192092896 to 0.30000001192092896 | 0.01 | 2 |
| `yellow` | number | -0.30000001192092896 to 0.30000001192092896 | 0.01 | 2 |
| `black` | number | 0 to 1.5 | 0.05 | 2 |
| `scanner_red_nm` | number | 600 to 720 | 5 | 0 |
| `scanner_green_nm` | number | 500 to 590 | 5 | 0 |
| `scanner_blue_nm` | number | 400 to 490 | 5 | 0 |
| `scanner_width_nm` | number | 10 to 120 | 5 | 0 |
| `scanner_light` | option | `halogen` (Halogen), `equal_energy` (Equal Energy) |  |  |

Reset value: `{"auto": "neutral", "auto_density": 0, "auto_strength": 0.5, "black": 1, "creative_white": "use_look_preset", "cyan": 0, "encoding_eotf": "gamma_2_2", "encoding_space": "rec709", "enlarger_flare": 0.01, "halation": 1, "light_spread": 1, "limiting_space": "rec709", "look_preset": "standard", "magenta": 0, "method": "open_drt", "negative": "kodak_5207", "peak_luminance": 100, "print_material": "kodak_endura_premier", "scan_contrast": 1, "scan_exposure_stops": 0, "scanner_blue_nm": 450, "scanner_green_nm": 545, "scanner_light": "halogen", "scanner_red_nm": 650, "scanner_width_nm": 40, "scene_light": "as_shot", "tonescale_preset": "use_look_preset", "yellow": 0}`

Valid `encoding_eotf` values of each `encoding_space`:

- `p3_d65`: `gamma_2_2`, `srgb_piecewise`, `st2084`
- `rec2020`: `st2084`, `hlg`
- `rec709`: `bt1886`, `gamma_2_2`, `srgb_piecewise`

#### `color_temp` (raw panel)

| Property | Type | Range or values | Step | Decimals |
| --- | --- | --- | --- | --- |
| `mode` | option | `as_shot` (As Shot), `custom` (Custom) |  |  |
| `kelvin` | number | 2000 to 15000; slider scale `kelvin_pivot`, position 0 to 4096, 6000 K at 2048 | 1 | 0 |
| `tint` | number | -150 to 150 | 1 | 0 |

Reset value: `{"kelvin": 6500, "mode": "as_shot", "tint": 0}`

#### `grade_white_balance` (look panel)

| Property | Type | Range or values | Step | Decimals |
| --- | --- | --- | --- | --- |
| `temperature` | number | 2000 to 15000; slider scale `kelvin_pivot`, position 0 to 4096, 6000 K at 2048 | 1 | 0 |
| `tint` | number | -150 to 150 | 1 | 0 |

Reset value: `{"temperature": 5999.9931640625, "tint": 9.711277961730957}`

#### `hls` (look panel)

| Property | Type | Range or values | Step | Decimals |
| --- | --- | --- | --- | --- |
| `hue` | number | 0 to 315 | 45 | 0 |
| `hue_shift` | number_list | 8 numbers, -30 to 30 | 1 | 0 |
| `lightness` | number_list | 8 numbers, -100 to 100 | 1 | 0 |
| `chroma` | number_list | 8 numbers, -100 to 100 | 1 | 0 |
| `hue_smoothness` | number_list | 8 numbers, 1 to 180 | 1 | 0 |

Reset value: `{"chroma": [0, 0, 0, 0, 0, 0, 0, 0], "hue": 0, "hue_shift": [0, 0, 0, 0, 0, 0, 0, 0], "hue_smoothness": [45, 45, 45, 45, 45, 45, 45, 45], "lightness": [0, 0, 0, 0, 0, 0, 0, 0]}`

#### `color_wheel` (look panel)

| Property | Type | Range or values | Step | Decimals |
| --- | --- | --- | --- | --- |
| `lift_x` | number | -1 to 1 | 0.001 | 3 |
| `lift_y` | number | -1 to 1 | 0.001 | 3 |
| `lift_master` | number | -2 to 2 | 0.01 | 2 |
| `gamma_x` | number | -1 to 1 | 0.001 | 3 |
| `gamma_y` | number | -1 to 1 | 0.001 | 3 |
| `gamma_master` | number | -2 to 2 | 0.01 | 2 |
| `gain_x` | number | -1 to 1 | 0.001 | 3 |
| `gain_y` | number | -1 to 1 | 0.001 | 3 |
| `gain_master` | number | -2 to 2 | 0.01 | 2 |
| `offset_x` | number | -1 to 1 | 0.001 | 3 |
| `offset_y` | number | -1 to 1 | 0.001 | 3 |
| `offset_master` | number | -2 to 2 | 0.01 | 2 |

Reset value: `{"gain_master": 0, "gain_x": 0, "gain_y": 0, "gamma_master": 0, "gamma_x": 0, "gamma_y": 0, "lift_master": 0, "lift_x": 0, "lift_y": 0, "offset_master": 0, "offset_x": 0, "offset_y": 0}`

### Model fields

A `lut` write gives the complete value. A `curve` write gives one or more of its four curves and leaves the other curves as they are.

#### `curve` (tone panel)

{"points": [{"x": number, "y": number}, ...], "red": [...], "green": [...], "blue": [...]}: the RGB curve (points) and the red, green, and blue curves, each 2 to 16 control points in the unit square with x strictly increasing. A write needs one or more of the four keys and leaves the other curves as they are; in a write, the value of a key can be the id of a Tone Curve preset (curve.presets), which writes the points of the preset. The render applies the RGB curve to each channel, then the curve of the channel

Reset value: `{"blue": [{"x": 0, "y": 0}, {"x": 1, "y": 1}], "green": [{"x": 0, "y": 0}, {"x": 1, "y": 1}], "points": [{"x": 0, "y": 0}, {"x": 1, "y": 1}], "red": [{"x": 0, "y": 0}, {"x": 1, "y": 1}]}`

#### `lut` (lut panel)

{"cube_path": string} or a tagged {"reference": object}, and optional "name", "strength" (0 to 1), "input_encoding", and "output_encoding" (color encoding ids). {} is no LUT

Reset value: `{}`
<!-- END GENERATED: editor-fields -->
