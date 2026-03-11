# -*- coding: utf-8 -*-
"""
DOSYA: app/services/state_service.py
MODUL: app.services.state_service
ROL:
- Uygulama durumunu json olarak kaydetme / okuma
SURUM: 2
TARIH: 2026-03-10
"""

from __future__ import annotations

from pathlib import Path

from app.core.helpers import read_json_file, write_json_file

STATE_FILENAME = ".apk_kurucu_state.json"


def get_state_path(project_root: str | Path) -> str:
    return str(Path(project_root) / STATE_FILENAME)


def load_state(project_root: str | Path) -> tuple[bool, dict | str]:
    return read_json_file(get_state_path(project_root))


def save_state(project_root: str | Path, data: dict) -> tuple[bool, str]:
    return write_json_file(get_state_path(project_root), data)


def merge_state(project_root: str | Path, partial_data: dict) -> tuple[bool, str]:
    ok, existing = load_state(project_root)

    final_data: dict = {}
    if ok and isinstance(existing, dict):
        final_data.update(existing)

    if isinstance(partial_data, dict):
        final_data.update(partial_data)

    return save_state(project_root, final_data)