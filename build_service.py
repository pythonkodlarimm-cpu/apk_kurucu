# -*- coding: utf-8 -*-
"""
DOSYA: app/services/build_service.py
MODUL: app.services.build_service

ROL:
- Build ayarlarini toplar
- buildozer.spec / README / requirements icerigi uretir
- Dosyalari proje kokune kaydeder

SURUM: 5
TARIH: 2026-03-11
"""

from __future__ import annotations

from pathlib import Path

from app.core.config import (
    DEFAULT_ANDROID_API,
    DEFAULT_ANDROID_ARCHS,
    DEFAULT_ANDROID_MINAPI,
    DEFAULT_ANDROID_NDK,
    DEFAULT_ICON_FILENAME,
    DEFAULT_ORIENTATION,
    DEFAULT_PACKAGE_DOMAIN,
    DEFAULT_PACKAGE_NAME,
    DEFAULT_PROJECT_TITLE,
    DEFAULT_REQUIREMENTS,
    DEFAULT_VERSION,
    TEMPLATE_BUILDZER_FILENAME,
    TEMPLATE_README_FILENAME,
    TEMPLATE_REQUIREMENTS_FILENAME,
)
from app.core.helpers import bump_semver, ensure_dir
from app.core.templates import (
    build_buildozer_spec_template,
    build_readme_template,
    build_requirements_template,
)


def get_default_build_config() -> dict:
    return {
        "title": DEFAULT_PROJECT_TITLE,
        "package_name": DEFAULT_PACKAGE_NAME,
        "package_domain": DEFAULT_PACKAGE_DOMAIN,
        "version": DEFAULT_VERSION,
        "requirements": DEFAULT_REQUIREMENTS,
        "android_api": DEFAULT_ANDROID_API,
        "android_minapi": DEFAULT_ANDROID_MINAPI,
        "android_ndk": DEFAULT_ANDROID_NDK,
        "android_archs": DEFAULT_ANDROID_ARCHS,
        "orientation": DEFAULT_ORIENTATION,
        "icon_filename": DEFAULT_ICON_FILENAME,
    }


def normalize_build_config(raw: dict | None) -> dict:
    data = get_default_build_config()

    if not isinstance(raw, dict):
        return data

    for key in data:
        value = raw.get(key)
        if value is None:
            continue

        clean_value = str(value).strip()
        if clean_value:
            data[key] = clean_value

    if not data.get("title"):
        data["title"] = DEFAULT_PROJECT_TITLE

    if not data.get("package_name"):
        data["package_name"] = DEFAULT_PACKAGE_NAME

    if not data.get("package_domain"):
        data["package_domain"] = DEFAULT_PACKAGE_DOMAIN

    if not data.get("version"):
        data["version"] = DEFAULT_VERSION

    if not data.get("requirements"):
        data["requirements"] = DEFAULT_REQUIREMENTS

    if not data.get("android_api"):
        data["android_api"] = DEFAULT_ANDROID_API

    if not data.get("android_minapi"):
        data["android_minapi"] = DEFAULT_ANDROID_MINAPI

    if not data.get("android_ndk"):
        data["android_ndk"] = DEFAULT_ANDROID_NDK

    if not data.get("android_archs"):
        data["android_archs"] = DEFAULT_ANDROID_ARCHS

    if not data.get("orientation"):
        data["orientation"] = DEFAULT_ORIENTATION

    if not data.get("icon_filename"):
        data["icon_filename"] = DEFAULT_ICON_FILENAME

    return data


def bump_build_version(raw: dict | None) -> dict:
    config = normalize_build_config(raw)
    config["version"] = bump_semver(config.get("version", DEFAULT_VERSION))
    return config


def generate_buildozer_spec_content(raw: dict | None) -> str:
    config = normalize_build_config(raw)
    return build_buildozer_spec_template(config)


def generate_readme_content(raw: dict | None) -> str:
    config = normalize_build_config(raw)
    return build_readme_template(config)


def generate_requirements_content(raw: dict | None) -> str:
    config = normalize_build_config(raw)
    return build_requirements_template(config)


def save_buildozer_spec(
    project_root: str | Path,
    raw: dict | None,
) -> tuple[bool, str]:
    ok, info = ensure_dir(project_root)
    if not ok:
        return False, info

    try:
        target = Path(info) / TEMPLATE_BUILDZER_FILENAME
        content = generate_buildozer_spec_content(raw)
        target.write_text(content, encoding="utf-8")
        return True, f"Kaydedildi: {target}"
    except Exception as exc:
        return False, f"Kaydedilemedi: {exc}"


def save_readme(
    project_root: str | Path,
    raw: dict | None,
) -> tuple[bool, str]:
    ok, info = ensure_dir(project_root)
    if not ok:
        return False, info

    try:
        target = Path(info) / TEMPLATE_README_FILENAME
        content = generate_readme_content(raw)
        target.write_text(content, encoding="utf-8")
        return True, f"Kaydedildi: {target}"
    except Exception as exc:
        return False, f"Kaydedilemedi: {exc}"


def save_requirements_txt(
    project_root: str | Path,
    raw: dict | None,
) -> tuple[bool, str]:
    ok, info = ensure_dir(project_root)
    if not ok:
        return False, info

    try:
        target = Path(info) / TEMPLATE_REQUIREMENTS_FILENAME
        content = generate_requirements_content(raw)
        target.write_text(content, encoding="utf-8")
        return True, f"Kaydedildi: {target}"
    except Exception as exc:
        return False, f"Kaydedilemedi: {exc}"


def save_all_project_files(
    project_root: str | Path,
    raw: dict | None,
) -> tuple[bool, str]:
    results: list[str] = []

    ok1, msg1 = save_buildozer_spec(project_root, raw)
    results.append(msg1)

    ok2, msg2 = save_readme(project_root, raw)
    results.append(msg2)

    ok3, msg3 = save_requirements_txt(project_root, raw)
    results.append(msg3)

    success = ok1 and ok2 and ok3

    if success:
        prefix = "Tum proje dosyalari kaydedildi."
    else:
        prefix = "Bazi dosyalar kaydedilemedi."

    return success, prefix + "\n" + "\n".join(results)
