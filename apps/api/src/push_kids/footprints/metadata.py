"""Bounded decode, minimal EXIF and stripped display images. No full EXIF persistence."""

import json
import math
import subprocess
import sys
import warnings
from dataclasses import dataclass, field
from datetime import date, datetime
from pathlib import Path

from PIL import Image, ImageOps, UnidentifiedImageError

MAX_PIXELS = 40_000_000


@dataclass
class PhotoMetadata:
    values: dict = field(default_factory=dict)


def _gps_number(parts, reference: str | None, positive: str, negative: str, limit: int):
    if reference not in (positive, negative) or len(parts) != 3:
        return None
    numbers = [float(v) for v in parts]
    if not all(math.isfinite(v) and v >= 0 for v in numbers):
        return None
    if numbers[1] >= 60 or numbers[2] >= 60:
        return None
    result = numbers[0] + numbers[1] / 60 + numbers[2] / 3600
    if result > limit:
        return None
    return result if reference == positive else -result


def _extract(image) -> dict:
    values: dict = {}
    try:
        exif = image.getexif()
        nested = exif.get_ifd(34665) if 34665 in exif else {}
    except (ValueError, TypeError, KeyError, SyntaxError):
        return values
    try:
        raw = nested.get(36867) or exif.get(36867)
        if raw:
            wall = datetime.strptime(str(raw).strip("\x00"), "%Y:%m:%d %H:%M:%S")
            values.update(
                local_date=wall.date(), local_time=wall.time().isoformat(), time_source="exif"
            )
            offset = nested.get(36881) or exif.get(36881)
            if offset and len(str(offset)) == 6:
                text = str(offset)
                if text[0] in "+-" and text[3] == ":":
                    minutes = int(text[1:3]) * 60 + int(text[4:6])
                    minutes *= 1 if text[0] == "+" else -1
                    if -720 <= minutes <= 840 and int(text[4:6]) < 60:
                        values["offset_minutes"] = minutes
    except (ValueError, TypeError, KeyError, OverflowError):
        pass
    try:
        gps = exif.get_ifd(34853) if 34853 in exif else {}
        if gps:
            lat = _gps_number(gps.get(2, []), gps.get(1), "N", "S", 90)
            lon = _gps_number(gps.get(4, []), gps.get(3), "E", "W", 180)
            datum = str(gps.get(18, "WGS-84")).replace(" ", "").upper()
            if lat is not None and lon is not None and datum in ("WGS-84", "WGS84"):
                values.update(
                    latitude=lat,
                    longitude=lon,
                    coordinate_system="wgs84",
                    precision="poi",
                    location_source="gps",
                )
    except (ValueError, TypeError, KeyError, ZeroDivisionError, OverflowError, SyntaxError):
        # Malformed optional EXIF does not destroy an otherwise valid photo.
        pass
    return values


def prepare(source: Path, display: Path, thumbnail: Path) -> PhotoMetadata:
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("error", Image.DecompressionBombWarning)
            with Image.open(source) as image:
                if image.format not in {"JPEG", "PNG", "WEBP"}:
                    raise ValueError("请转换为 JPG、PNG 或 WebP 后上传")
                if image.width * image.height > MAX_PIXELS or getattr(image, "n_frames", 1) > 1:
                    raise ValueError("图片像素过大或包含多帧，请缩小后重试")
                metadata = _extract(image)
                image.load()
                upright = ImageOps.exif_transpose(image).convert("RGB")
                # Fresh pixel container discards EXIF, ICC, XMP and all incidental metadata.
                clean = Image.new("RGB", upright.size, "white")
                clean.paste(upright)
                clean.thumbnail((2048, 2048))
                clean.save(display, format="JPEG", quality=88, optimize=True)
                clean.thumbnail((320, 320))
                clean.save(thumbnail, format="JPEG", quality=78, optimize=True)
                return PhotoMetadata(metadata)
    except (
        UnidentifiedImageError,
        OSError,
        Image.DecompressionBombError,
        Image.DecompressionBombWarning,
    ) as exc:
        raise ValueError("图片无法安全读取，请转换格式或缩小后重试") from exc


def prepare_bounded(source: Path, display: Path, thumbnail: Path) -> PhotoMetadata:
    """A corrupt decoder cannot occupy the durable worker beyond ten seconds."""
    try:
        result = subprocess.run(
            [
                sys.executable,
                str(Path(__file__).resolve()),
                str(source),
                str(display),
                str(thumbnail),
            ],
            capture_output=True,
            timeout=10,
            check=True,
        )
        values = json.loads(result.stdout)
        if values.get("local_date"):
            values["local_date"] = date.fromisoformat(values["local_date"])
        return PhotoMetadata(values)
    except (subprocess.SubprocessError, ValueError, OSError) as exc:
        raise ValueError("图片处理失败或超时，请转换格式或缩小后重试") from exc


if __name__ == "__main__":
    prepared = prepare(*(Path(path) for path in sys.argv[1:4]))
    print(json.dumps(prepared.values, default=str))
