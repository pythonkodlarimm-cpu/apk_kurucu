# -*- coding: utf-8 -*-
"""
DOSYA: app/services/export_service.py
MODUL: app.services.export_service
ROL:
- Repo / yayin hazirlik dosyalarini uretme ve kaydetme
SURUM: 2
TARIH: 2026-03-10
"""

from __future__ import annotations

from pathlib import Path

from app.core.config import (
    TEMPLATE_BUILD_COMMANDS_FILENAME,
    TEMPLATE_BUILD_STATUS_FILENAME,
    TEMPLATE_GITIGNORE_FILENAME,
    TEMPLATE_PUSH_COMMANDS_FILENAME,
    TEMPLATE_RELEASE_CHECKLIST_FILENAME,
)
from app.core.helpers import ensure_dir
from app.core.templates import (
    build_build_commands_template,
    build_build_status_template,
    build_gitignore_template,
    build_push_commands_template,
    build_release_checklist_template,
)


def generate_gitignore_content() -> str:
    return build_gitignore_template()


def generate_build_commands_content(raw: dict | None) -> str:
    return build_build_commands_template(raw or {})


def generate_release_checklist_content(raw: dict | None) -> str:
    return build_release_checklist_template(raw or {})


def generate_push_commands_content(raw: dict | None) -> str:
    return build_push_commands_template(raw or {})


def generate_build_status_content(raw: dict | None) -> str:
    return build_build_status_template(raw or {})


def save_gitignore(project_root: str | Path) -> tuple[bool, str]:
    ok, info = ensure_dir(project_root)
    if not ok:
        return False, info

    try:
        target = Path(info) / TEMPLATE_GITIGNORE_FILENAME
        target.write_text(generate_gitignore_content(), encoding="utf-8")
        return True, f"Kaydedildi: {target}"
    except Exception as exc:
        return False, f"Kaydedilemedi: {exc}"


def save_build_commands(project_root: str | Path, raw: dict | None) -> tuple[bool, str]:
    ok, info = ensure_dir(project_root)
    if not ok:
        return False, info

    try:
        target = Path(info) / TEMPLATE_BUILD_COMMANDS_FILENAME
        target.write_text(generate_build_commands_content(raw), encoding="utf-8")
        return True, f"Kaydedildi: {target}"
    except Exception as exc:
        return False, f"Kaydedilemedi: {exc}"


def save_release_checklist(project_root: str | Path, raw: dict | None) -> tuple[bool, str]:
    ok, info = ensure_dir(project_root)
    if not ok:
        return False, info

    try:
        target = Path(info) / TEMPLATE_RELEASE_CHECKLIST_FILENAME
        target.write_text(generate_release_checklist_content(raw), encoding="utf-8")
        return True, f"Kaydedildi: {target}"
    except Exception as exc:
        return False, f"Kaydedilemedi: {exc}"


def save_push_commands(project_root: str | Path, raw: dict | None) -> tuple[bool, str]:
    ok, info = ensure_dir(project_root)
    if not ok:
        return False, info

    try:
        target = Path(info) / TEMPLATE_PUSH_COMMANDS_FILENAME
        target.write_text(generate_push_commands_content(raw), encoding="utf-8")
        return True, f"Kaydedildi: {target}"
    except Exception as exc:
        return False, f"Kaydedilemedi: {exc}"


def save_build_status(project_root: str | Path, raw: dict | None) -> tuple[bool, str]:
    ok, info = ensure_dir(project_root)
    if not ok:
        return False, info

    try:
        target = Path(info) / TEMPLATE_BUILD_STATUS_FILENAME
        target.write_text(generate_build_status_content(raw), encoding="utf-8")
        return True, f"Kaydedildi: {target}"
    except Exception as exc:
        return False, f"Kaydedilemedi: {exc}"


def save_repo_bundle(project_root: str | Path, raw: dict | None) -> tuple[bool, str]:
    results: list[str] = []

    ok1, msg1 = save_gitignore(project_root)
    results.append(msg1)

    ok2, msg2 = save_build_commands(project_root, raw)
    results.append(msg2)

    ok3, msg3 = save_release_checklist(project_root, raw)
    results.append(msg3)

    ok4, msg4 = save_push_commands(project_root, raw)
    results.append(msg4)

    ok5, msg5 = save_build_status(project_root, raw)
    results.append(msg5)

    success = ok1 and ok2 and ok3 and ok4 and ok5
    prefix = "Repo hazirlik dosyalari kaydedildi." if success else "Repo hazirlik dosyalarinda hata var."
    return success, prefix + "\n" + "\n".join(results)