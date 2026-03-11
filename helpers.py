# -*- coding: utf-8 -*-
"""
DOSYA: app/core/helpers.py
MODUL: app.core.helpers
ROL:
- Ortak yardimci fonksiyonlar
SURUM: 5
TARIH: 2026-03-10
"""

from __future__ import annotations

import json
import os
from pathlib import Path


def safe_str(value: object, default: str = "") -> str:
    try:
        if value is None:
            return default
        return str(value)
    except Exception:
        return default


def normalize_path(path: str | os.PathLike[str] | None) -> str:
    if path is None:
        return ""

    try:
        raw = safe_str(path).strip()
        if not raw:
            return ""
        return os.path.normpath(raw)
    except Exception:
        return ""


def path_exists(path: str | os.PathLike[str] | None) -> bool:
    normalized = normalize_path(path)
    if not normalized:
        return False

    try:
        return Path(normalized).exists()
    except Exception:
        return False


def is_file(path: str | os.PathLike[str] | None) -> bool:
    normalized = normalize_path(path)
    if not normalized:
        return False

    try:
        return Path(normalized).is_file()
    except Exception:
        return False


def is_dir(path: str | os.PathLike[str] | None) -> bool:
    normalized = normalize_path(path)
    if not normalized:
        return False

    try:
        return Path(normalized).is_dir()
    except Exception:
        return False


def ensure_dir(path: str | os.PathLike[str] | None) -> tuple[bool, str]:
    normalized = normalize_path(path)
    if not normalized:
        return False, "Klasör yolu boş."

    try:
        Path(normalized).mkdir(parents=True, exist_ok=True)
        return True, normalized
    except Exception as exc:
        return False, f"Klasör oluşturulamadı: {exc}"


def get_filename(path: str | os.PathLike[str] | None) -> str:
    normalized = normalize_path(path)
    if not normalized:
        return ""

    try:
        return Path(normalized).name
    except Exception:
        return ""


def get_extension(path: str | os.PathLike[str] | None) -> str:
    normalized = normalize_path(path)
    if not normalized:
        return ""

    try:
        return Path(normalized).suffix.lower()
    except Exception:
        return ""


def get_file_size(path: str | os.PathLike[str] | None) -> int:
    normalized = normalize_path(path)
    if not normalized:
        return -1

    try:
        return Path(normalized).stat().st_size
    except Exception:
        return -1


def format_file_size(size_in_bytes: int) -> str:
    try:
        size = int(size_in_bytes)
    except Exception:
        return "Bilinmiyor"

    if size < 0:
        return "Bilinmiyor"

    units = ["B", "KB", "MB", "GB", "TB"]
    value = float(size)
    unit_index = 0

    while value >= 1024 and unit_index < len(units) - 1:
        value /= 1024.0
        unit_index += 1

    if unit_index == 0:
        return f"{int(value)} {units[unit_index]}"

    return f"{value:.2f} {units[unit_index]}"


def shorten_text(text: str | None, max_length: int) -> str:
    value = safe_str(text)
    if max_length <= 0:
        return ""

    if len(value) <= max_length:
        return value

    if max_length <= 3:
        return "." * max_length

    return value[: max_length - 3] + "..."


def safe_bool(value: object) -> bool:
    try:
        return bool(value)
    except Exception:
        return False


def split_csv_text(value: str | None) -> list[str]:
    raw = safe_str(value).strip()
    if not raw:
        return []

    parts = [item.strip() for item in raw.split(",")]
    return [item for item in parts if item]


def bump_semver(version_text: str) -> str:
    raw = safe_str(version_text).strip()
    if not raw:
        return "0.1.0"

    pieces = raw.split(".")
    if len(pieces) != 3:
        return raw

    try:
        major = int(pieces[0])
        minor = int(pieces[1])
        patch = int(pieces[2])
    except Exception:
        return raw

    patch += 1
    return f"{major}.{minor}.{patch}"


def write_text_file(path: str | os.PathLike[str], content: str) -> tuple[bool, str]:
    normalized = normalize_path(path)
    if not normalized:
        return False, "Dosya yolu boş."

    try:
        target = Path(normalized)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
        return True, f"Kaydedildi: {target}"
    except Exception as exc:
        return False, f"Kaydedilemedi: {exc}"


def read_text_file(path: str | os.PathLike[str]) -> tuple[bool, str]:
    normalized = normalize_path(path)
    if not normalized:
        return False, "Dosya yolu boş."

    try:
        content = Path(normalized).read_text(encoding="utf-8")
        return True, content
    except Exception as exc:
        return False, f"Okunamadı: {exc}"


def write_json_file(path: str | os.PathLike[str], data: dict) -> tuple[bool, str]:
    normalized = normalize_path(path)
    if not normalized:
        return False, "Dosya yolu boş."

    try:
        target = Path(normalized)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(
            json.dumps(data, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        return True, f"Kaydedildi: {target}"
    except Exception as exc:
        return False, f"Kaydedilemedi: {exc}"


def read_json_file(path: str | os.PathLike[str]) -> tuple[bool, dict | str]:
    normalized = normalize_path(path)
    if not normalized:
        return False, "Dosya yolu boş."

    try:
        content = Path(normalized).read_text(encoding="utf-8")
        return True, json.loads(content)
    except Exception as exc:
        return False, f"Okunamadı: {exc}"


def mask_secret(value: str | None) -> str:
    raw = safe_str(value).strip()
    if not raw:
        return ""

    if len(raw) <= 8:
        return "*" * len(raw)

    return raw[:4] + "*" * (len(raw) - 8) + raw[-4:]


def merge_dicts(*items: dict | None) -> dict:
    result: dict = {}
    for item in items:
        if isinstance(item, dict):
            result.update(item)
    return result


def pretty_json(value: object) -> str:
    try:
        return json.dumps(value, ensure_ascii=False, indent=2)
    except Exception:
        return safe_str(value)
