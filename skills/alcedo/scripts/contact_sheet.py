#!/usr/bin/env python3
"""Makes contact sheets of Alcedo Studio photos for an agent that culls or compares them.

    python contact_sheet.py --out-dir <dir> [source] [options]

The script starts one `alcedo-cli batch` process and sends every command over its one session
connection: it reads the photos, their metadata (`library.info`), and their thumbnails
(`library.thumbnails`). It then draws sheets with a grid of cells. Each cell has the thumbnail,
an optional detail crop beside it, and a label: the sequence number, the element id, the file
name, the rating, the capture time, and the camera, lens, focal length, aperture, shutter, and
ISO when the metadata has them. A value that the metadata does not have is left blank.

Source (one of them; default: every photo of the root folder):

    --ids 12,40,41        These element ids, in this order.
    --ids-file <file>     Element ids from a file (whitespace or comma separated).
    --selection           The library selection of the GUI session.
    --search <text>       The matches of search.query (the current folder of the session).
    --folder <id|path>    The photos of a folder (a folder_id or a path of library.folders).

Output in --out-dir:

    <prefix>_001.jpg ...  The sheets.
    <prefix>.json         The index: for each sequence number, its sheet, row, column, and cell
                          box in pixels, and the element id, file path, and metadata of the
                          photo. Use the element id with the other alcedo-cli commands.
    thumbs/, details/     The PNG files that the sheets were drawn from.

Detail crops (--detail center, or --detail x,y with x and y from 0 to 1) show a part of the
photo at the full detail of the editor beside each thumbnail, for a sharpness check. They open
each photo in the editor (`editor.open`, then `render.preview` with a region), which takes much
longer than the thumbnails. In a GUI session the agent must hold control (`control.acquire`);
the script opens the photo that was open before again at the end.

Needs Python 3.9 or later with Pillow (`pip install pillow`) and alcedo-cli.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import math
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any, Iterable, Optional

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError as error:  # pragma: no cover - depends on the machine
    sys.stderr.write(f"contact_sheet.py needs Pillow: {error}\n"
                     "Install it with: python -m pip install pillow\n")
    sys.exit(2)

# Limits of the alcedo-cli commands that the script calls.
MAX_IDS_PER_REQUEST = 1000
MAX_LIST_LIMIT = 1000
MAX_SEARCH_LIMIT = 48
MAX_THUMBNAIL_LONG_EDGE = 2048
MAX_PREVIEW_LONG_EDGE = 4096
# Time limits: one thumbnail can need a RAW decode; the editor opens a photo in a few seconds.
THUMBNAIL_TIMEOUT_MS_PER_PHOTO = 10000
MIN_TIMEOUT_MS = 120000
# The detail crop covers this part of the long edge when the metadata has no image size.
DEFAULT_DETAIL_SHARE = 0.15

SORT_KEYS = ("capture_time", "file_name", "rating", "element_id", "camera_model", "lens", "input")

BACKGROUND = (24, 24, 24)
CELL_BACKGROUND = (38, 38, 38)
TEXT = (235, 235, 235)
DIM_TEXT = (165, 165, 165)
BADGE_BACKGROUND = (0, 0, 0)
BADGE_TEXT = (255, 214, 64)
MISSING_THUMBNAIL = (70, 40, 40)


class CliError(RuntimeError):
    """An error answer of a command, or a lost alcedo-cli process."""

    def __init__(self, message: str, error: Optional[dict] = None):
        super().__init__(message)
        self.error = error or {}

    @property
    def code(self) -> Optional[int]:
        return self.error.get("code")


class AlcedoBatch:
    """One `alcedo-cli batch` process: one session connection for every command."""

    def __init__(self, cli: str, session: Optional[str], session_dir: Optional[str]):
        command = [cli]
        if session:
            command += ["--session", session]
        if session_dir:
            command += ["--session-dir", session_dir]
        command.append("batch")
        try:
            self.process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                            stderr=subprocess.PIPE, encoding="utf-8", bufsize=1)
        except OSError as error:
            raise CliError(f"cannot start {cli}: {error}") from error
        self.next_id = 1

    def call(self, method: str, params: Optional[dict] = None) -> dict:
        request = {"id": self.next_id, "method": method, "params": params or {}}
        self.next_id += 1
        try:
            self.process.stdin.write(json.dumps(request) + "\n")
            self.process.stdin.flush()
        except OSError:
            pass  # The process exited; readline below reports it with its error output.
        line = self.process.stdout.readline()
        if not line:
            self.process.wait()
            detail = self.process.stderr.read().strip()
            raise CliError(f"alcedo-cli batch exited with code {self.process.returncode} during "
                           f"{method}: {detail}")
        answer = json.loads(line)
        if "error" in answer:
            error = answer["error"]
            reason = error.get("data", {}).get("reason") if isinstance(error.get("data"), dict) \
                else None
            raise CliError(f"{method} failed with {error.get('code')}: "
                           f"{reason or error.get('message')}", error)
        return answer["result"]

    def close(self) -> None:
        if self.process.stdin and not self.process.stdin.closed:
            self.process.stdin.close()
        try:
            self.process.wait(timeout=30)
        except subprocess.TimeoutExpired:
            self.process.kill()


def find_cli(explicit: Optional[str]) -> str:
    if explicit:
        # Windows CreateProcess does not resolve a relative path with forward slashes.
        return str(Path(explicit).resolve())
    found = shutil.which("alcedo-cli")
    if not found:
        raise CliError("alcedo-cli is not on the PATH; give it with --cli <path>")
    return found


def parse_ids(text: str) -> list[int]:
    ids = []
    for word in text.replace(",", " ").split():
        value = int(word)
        if value < 1:
            raise ValueError(f"element id {value} is not positive")
        ids.append(value)
    return ids


def chunks(values: list, size: int) -> Iterable[list]:
    for start in range(0, len(values), size):
        yield values[start:start + size]


def list_folder(batch: AlcedoBatch, folder: Optional[str]) -> list[int]:
    params: dict[str, Any] = {}
    if folder is not None:
        if folder.isdigit():
            params["folder_id"] = int(folder)
        else:
            wanted = "/" + folder.strip("/").replace("\\", "/")
            folders = batch.call("library.folders")["folders"]
            matches = [entry for entry in folders if entry["path"].rstrip("/") == wanted.rstrip("/")
                       or (wanted == "/" and entry["depth"] == 0)]
            if not matches:
                known = ", ".join(entry["path"] for entry in folders)
                raise CliError(f"no folder with the path {folder}; the folders are: {known}")
            params["folder_id"] = matches[0]["folder_id"]
    ids: list[int] = []
    offset = 0
    while True:
        page = batch.call("library.list", {**params, "offset": offset, "limit": MAX_LIST_LIMIT})
        ids += [item["element_id"] for item in page["items"]]
        offset += len(page["items"])
        if not page["items"] or offset >= page["total"]:
            return ids


def search_ids(batch: AlcedoBatch, text: str) -> list[int]:
    ids: list[int] = []
    offset = 0
    while True:
        page = batch.call("search.query", {"text": text, "offset": offset,
                                           "limit": MAX_SEARCH_LIMIT})
        if page.get("semantic_unavailable"):
            raise CliError("the natural language search is not available; search with a file "
                           "name, camera, lens, or date, or turn the search on in Settings")
        if page.get("too_long"):
            raise CliError("the search text is too long")
        ids += [match["element_id"] for match in page.get("matches", [])]
        offset += len(page.get("matches", []))
        if not page.get("has_more") or not page.get("matches"):
            return ids


def unique(ids: list[int]) -> list[int]:
    seen: set[int] = set()
    return [value for value in ids if not (value in seen or seen.add(value))]


def read_infos(batch: AlcedoBatch, ids: list[int]) -> list[dict]:
    infos: list[dict] = []
    for part in chunks(ids, MAX_IDS_PER_REQUEST):
        infos += batch.call("library.info", {"element_ids": part})["items"]
    return infos


def sort_photos(photos: list[dict], key: str, descending: bool) -> list[dict]:
    if key == "input":
        return list(reversed(photos)) if descending else photos

    def value(photo: dict):
        field = photo.get(key)
        if isinstance(field, str):
            field = field.casefold()
        # Photos without the value come last in both directions.
        return (field is None or field == "", field if field is not None else "")

    present = [photo for photo in photos if not value(photo)[0]]
    missing = [photo for photo in photos if value(photo)[0]]
    present.sort(key=lambda photo: (value(photo)[1], photo["element_id"]), reverse=descending)
    missing.sort(key=lambda photo: photo["element_id"])
    return present + missing


def write_thumbnails(batch: AlcedoBatch, photos: list[dict], out_dir: Path, long_edge: int) -> None:
    for part in chunks(photos, MAX_IDS_PER_REQUEST):
        timeout_ms = max(MIN_TIMEOUT_MS, THUMBNAIL_TIMEOUT_MS_PER_PHOTO * len(part))
        result = batch.call("library.thumbnails", {
            "element_ids": [photo["element_id"] for photo in part],
            "out_dir": str(out_dir), "long_edge": long_edge, "timeout_ms": timeout_ms})
        for photo, item in zip(part, result["items"]):
            photo["thumbnail"] = item.get("path")
            if "error" in item:
                photo["thumbnail_error"] = item["error"]


def detail_region(photo: dict, position: tuple[float, float], size_px: int) -> dict:
    """A region of size_px by size_px pixels of the full image around position (0 to 1)."""
    width, height = photo.get("width"), photo.get("height")
    if width and height:
        w = min(1.0, size_px / width)
        h = min(1.0, size_px / height)
    else:
        w = h = DEFAULT_DETAIL_SHARE
    x = min(max(position[0] - w / 2, 0.0), 1.0 - w)
    y = min(max(position[1] - h / 2, 0.0), 1.0 - h)
    return {"x": round(x, 6), "y": round(y, 6), "w": round(w, 6), "h": round(h, 6)}


def write_details(batch: AlcedoBatch, photos: list[dict], out_dir: Path,
                  position: tuple[float, float], size_px: int, previous: Optional[int]) -> None:
    """Writes the detail crops. Opens previous again at the end, or closes the editor."""
    try:
        for number, photo in enumerate(photos, 1):
            sys.stderr.write(f"\rdetail crop {number}/{len(photos)}")
            sys.stderr.flush()
            try:
                batch.call("editor.open", {"element_id": photo["element_id"]})
                result = batch.call("render.preview", {
                    "out_dir": str(out_dir), "compare": "none",
                    "long_edge": min(size_px, MAX_PREVIEW_LONG_EDGE),
                    "file_stem": str(photo["element_id"]),
                    "region": detail_region(photo, position, size_px)})
                photo["detail"] = result["current"]["path"]
            except CliError as error:
                if error.code in (-32003, -32004):
                    raise CliError("detail crops open each photo in the editor: acquire agent "
                                   "control first (control.acquire), and stop when the user "
                                   f"stopped the agent ({error})", error.error) from error
                photo["detail_error"] = str(error)
        sys.stderr.write("\n")
    finally:
        if previous:
            batch.call("editor.open", {"element_id": previous})
        else:
            batch.call("editor.close")


def load_font(size: int) -> ImageFont.ImageFont:
    for name in ("DejaVuSans.ttf", "arial.ttf", "Arial.ttf", "Helvetica.ttc",
                 "/System/Library/Fonts/Helvetica.ttc", "/Library/Fonts/Arial.ttf",
                 "C:/Windows/Fonts/arial.ttf", "C:/Windows/Fonts/msyh.ttc"):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    try:
        return ImageFont.load_default(size=size)
    except TypeError:  # Pillow before 10.1
        return ImageFont.load_default()


def text_width(draw: ImageDraw.ImageDraw, text: str, font) -> float:
    return draw.textlength(text, font=font)


def fit_text(draw: ImageDraw.ImageDraw, text: str, font, width: int) -> str:
    """Shortens text with an ellipsis in the middle until it fits width."""
    if text_width(draw, text, font) <= width:
        return text
    keep = len(text)
    while keep > 1:
        keep -= 1
        head = text[:(keep + 1) // 2]
        tail = text[len(text) - keep // 2:] if keep // 2 else ""
        candidate = f"{head}\u2026{tail}"
        if text_width(draw, candidate, font) <= width:
            return candidate
    return "\u2026"


def number_text(value: float) -> str:
    return f"{value:.1f}".rstrip("0").rstrip(".")


def label_lines(photo: dict) -> list[tuple[str, tuple[int, int, int]]]:
    """The label of a cell. A line whose values are all missing stays empty."""
    rating = photo.get("rating", 0)
    rating_text = f"rating {rating}/5" if rating else "unrated"
    exposure = []
    if photo.get("focal_mm"):
        exposure.append(f"{number_text(photo['focal_mm'])}mm")
    if photo.get("aperture"):
        exposure.append(f"f/{number_text(photo['aperture'])}")
    if photo.get("shutter"):
        exposure.append(photo["shutter"])
    if photo.get("iso"):
        exposure.append(f"ISO {photo['iso']}")
    make, model = photo.get("camera_make") or "", photo.get("camera_model") or ""
    # Many cameras repeat the make in the model name: "Sony ILCE-1", not "Sony Sony ILCE-1".
    if make and model.casefold().startswith(make.casefold()):
        camera = model
    else:
        camera = " ".join(part for part in (make, model) if part)
    return [
        (f"#{photo['seq']}  id {photo['element_id']}  {rating_text}", TEXT),
        (photo.get("file_name", ""), TEXT),
        (photo.get("capture_time", ""), DIM_TEXT),
        (camera, DIM_TEXT),
        (photo.get("lens", ""), DIM_TEXT),
        ("  ".join(exposure), DIM_TEXT),
    ]


def paste_fitted(sheet: Image.Image, path: Optional[str], box: tuple[int, int, int, int]) -> None:
    x, y, w, h = box
    if not path:
        ImageDraw.Draw(sheet).rectangle((x, y, x + w - 1, y + h - 1), fill=MISSING_THUMBNAIL)
        return
    with Image.open(path) as source:
        image = source.convert("RGB")
    image.thumbnail((w, h), Image.Resampling.LANCZOS)
    sheet.paste(image, (x + (w - image.width) // 2, y + (h - image.height) // 2))


def draw_sheets(photos: list[dict], args: argparse.Namespace, out_dir: Path) -> list[dict]:
    cell = args.cell
    font_size = max(11, cell // 22)
    font = load_font(font_size)
    badge_font = load_font(max(14, cell // 12))
    line_height = round(font_size * 1.3)
    label_height = line_height * 6 + 8
    image_width = cell * 2 + args.gap if args.detail else cell
    cell_width = image_width + 2 * args.gap
    cell_height = cell + label_height + 2 * args.gap
    per_sheet = args.columns * args.rows
    sheets = []
    for sheet_index, part in enumerate(chunks(photos, per_sheet), 1):
        rows = math.ceil(len(part) / args.columns)
        sheet = Image.new("RGB", (cell_width * args.columns, cell_height * rows), BACKGROUND)
        draw = ImageDraw.Draw(sheet)
        for position, photo in enumerate(part):
            row, column = divmod(position, args.columns)
            left, top = column * cell_width, row * cell_height
            draw.rectangle((left + 2, top + 2, left + cell_width - 3, top + cell_height - 3),
                           fill=CELL_BACKGROUND)
            image_left, image_top = left + args.gap, top + args.gap
            paste_fitted(sheet, photo.get("thumbnail"), (image_left, image_top, cell, cell))
            if args.detail:
                paste_fitted(sheet, photo.get("detail"),
                             (image_left + cell + args.gap, image_top, cell, cell))
            badge = f"{photo['seq']}"
            _, _, badge_right, badge_bottom = draw.textbbox((image_left + 5, image_top + 4), badge,
                                                            font=badge_font)
            draw.rectangle((image_left, image_top, badge_right + 5, badge_bottom + 5),
                           fill=BADGE_BACKGROUND)
            draw.text((image_left + 5, image_top + 4), badge, font=badge_font, fill=BADGE_TEXT)
            text_top = image_top + cell + 6
            for line, color in label_lines(photo):
                if line:
                    draw.text((image_left, text_top), fit_text(draw, line, font, image_width),
                              font=font, fill=color)
                text_top += line_height
            photo.update({"sheet": sheet_index, "row": row, "column": column,
                          "box": [left, top, cell_width, cell_height]})
        path = out_dir / f"{args.prefix}_{sheet_index:03d}.{args.format}"
        if args.format == "jpg":
            sheet.save(path, "JPEG", quality=args.quality)
        else:
            sheet.save(path, "PNG")
        for photo in part:
            photo["sheet_path"] = str(path)
        sheets.append({"index": sheet_index, "path": str(path), "width": sheet.width,
                       "height": sheet.height, "first_seq": part[0]["seq"],
                       "last_seq": part[-1]["seq"]})
        sys.stderr.write(f"sheet {sheet_index}: {path}\n")
    return sheets


INDEX_FIELDS = ("seq", "sheet", "row", "column", "box", "sheet_path", "element_id", "image_id",
                "file_name", "file_path", "rating", "capture_time", "camera_make",
                "camera_model", "lens", "focal_mm", "aperture", "shutter", "shutter_seconds",
                "iso", "width", "height", "thumbnail", "thumbnail_error", "detail",
                "detail_error", "metadata_error")


def parse_position(text: str) -> tuple[float, float]:
    if text == "center":
        return (0.5, 0.5)
    try:
        x_text, y_text = text.split(",")
        x, y = float(x_text), float(y_text)
    except ValueError as error:
        raise argparse.ArgumentTypeError("use center or x,y with x and y from 0 to 1") from error
    if not (0.0 <= x <= 1.0 and 0.0 <= y <= 1.0):
        raise argparse.ArgumentTypeError("x and y must be from 0 to 1")
    return (x, y)


def parse_args(argv: Optional[list[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Make contact sheets of Alcedo Studio photos.")
    parser.add_argument("--out-dir", required=True, help="Folder of the sheets and the index.")
    source = parser.add_mutually_exclusive_group()
    source.add_argument("--ids", help="Element ids, comma separated, in this order.")
    source.add_argument("--ids-file", help="A file of element ids.")
    source.add_argument("--selection", action="store_true",
                        help="The library selection of the GUI session.")
    source.add_argument("--search", help="The matches of this search text.")
    source.add_argument("--folder", help="A folder_id or a folder path of library.folders.")
    parser.add_argument("--sort", choices=SORT_KEYS, default="capture_time",
                        help="Order of the photos (default capture_time; input keeps the order "
                             "of the source).")
    parser.add_argument("--descending", action="store_true")
    parser.add_argument("--columns", type=int, default=6, help="Cells per row (default 6).")
    parser.add_argument("--rows", type=int, default=5, help="Rows per sheet (default 5).")
    parser.add_argument("--cell", type=int, default=320,
                        help="Size of the thumbnail square in pixels (default 320).")
    parser.add_argument("--gap", type=int, default=10, help="Space around a cell in pixels.")
    parser.add_argument("--detail", type=parse_position, metavar="center|X,Y",
                        help="Add a detail crop at this position beside each thumbnail.")
    parser.add_argument("--detail-size", type=int,
                        help="Size of the detail crop in image pixels (default: --cell).")
    parser.add_argument("--prefix", default="contact_sheet", help="First part of the file names.")
    parser.add_argument("--format", choices=("jpg", "png"), default="jpg")
    parser.add_argument("--quality", type=int, default=88, help="JPEG quality (default 88).")
    parser.add_argument("--cli", help="The alcedo-cli program (default: on the PATH).")
    parser.add_argument("--session", help="The session name (as alcedo-cli --session).")
    parser.add_argument("--session-dir", help="The session directory (as alcedo-cli).")
    args = parser.parse_args(argv)
    for name in ("columns", "rows"):
        if getattr(args, name) < 1:
            parser.error(f"--{name} must be at least 1")
    if not 32 <= args.cell <= MAX_THUMBNAIL_LONG_EDGE:
        parser.error(f"--cell must be from 32 to {MAX_THUMBNAIL_LONG_EDGE}")
    if args.detail_size is not None and not 16 <= args.detail_size <= MAX_PREVIEW_LONG_EDGE:
        parser.error(f"--detail-size must be from 16 to {MAX_PREVIEW_LONG_EDGE}")
    return args


def collect_ids(batch: AlcedoBatch, args: argparse.Namespace) -> tuple[list[int], dict]:
    if args.ids:
        return parse_ids(args.ids), {"kind": "ids"}
    if args.ids_file:
        return parse_ids(Path(args.ids_file).read_text(encoding="utf-8")), {
            "kind": "ids_file", "path": str(Path(args.ids_file).resolve())}
    if args.selection:
        items = batch.call("library.selection.get")["items"]
        return [item["element_id"] for item in items], {"kind": "selection"}
    if args.search is not None:
        return search_ids(batch, args.search), {"kind": "search", "text": args.search}
    return list_folder(batch, args.folder), {"kind": "folder", "folder": args.folder or "/"}


def run(args: argparse.Namespace) -> int:
    out_dir = Path(args.out_dir).resolve()
    thumbs_dir, details_dir = out_dir / "thumbs", out_dir / "details"
    out_dir.mkdir(parents=True, exist_ok=True)
    batch = AlcedoBatch(find_cli(args.cli), args.session, args.session_dir)
    try:
        state = batch.call("state.get")
        ids, source = collect_ids(batch, args)
        ids = unique(ids)
        if not ids:
            raise CliError(f"the source ({source['kind']}) has no photos")
        photos = sort_photos(read_infos(batch, ids), args.sort, args.descending)
        for seq, photo in enumerate(photos, 1):
            photo["seq"] = seq
        sys.stderr.write(f"{len(photos)} photos; writing thumbnails\n")
        write_thumbnails(batch, photos, thumbs_dir, args.cell)
        if args.detail:
            write_details(batch, photos, details_dir, args.detail, args.detail_size or args.cell,
                          state["editor"].get("element_id") or None)
    finally:
        batch.close()

    sheets = draw_sheets(photos, args, out_dir)
    index = {
        "created": dt.datetime.now().astimezone().isoformat(timespec="seconds"),
        "project_path": state["project"].get("path"),
        "host_mode": state.get("host_mode"),
        "session": args.session or os.environ.get("ALCEDO_SESSION"),
        "source": source,
        "sort": {"key": args.sort, "descending": args.descending},
        "grid": {"columns": args.columns, "rows": args.rows, "cell": args.cell,
                 "detail": None if not args.detail else {
                     "x": args.detail[0], "y": args.detail[1],
                     "size": args.detail_size or args.cell}},
        "sheets": sheets,
        "photos": [{field: photo.get(field) for field in INDEX_FIELDS} for photo in photos],
    }
    index_path = out_dir / f"{args.prefix}.json"
    index_path.write_text(json.dumps(index, ensure_ascii=False, indent=1), encoding="utf-8")
    failed = sum(1 for photo in photos if photo.get("thumbnail_error"))
    print(json.dumps({"index": str(index_path), "sheets": [sheet["path"] for sheet in sheets],
                      "photo_count": len(photos), "thumbnail_failures": failed}))
    return 0


def main(argv: Optional[list[str]] = None) -> int:
    args = parse_args(argv)
    try:
        return run(args)
    except (CliError, ValueError, OSError) as error:
        sys.stderr.write(f"contact_sheet.py: {error}\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
