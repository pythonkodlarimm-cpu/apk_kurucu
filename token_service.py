# -*- coding: utf-8 -*-
"""
DOSYA: app/services/token_service.py
MODUL: app.services.token_service
ROL:
- GitHub token/config verisini json dosyasindan okur ve yazar
"""

from __future__ import annotations

from pathlib import Path

from app.core.helpers import read_json_file, write_json_file

CONFIG_FILE = Path("config/github_token.json")


def get_token_file_path() -> Path:
    return CONFIG_FILE


def load_github_file_config() -> dict:
    ok, payload = read_json_file(CONFIG_FILE)
    if not ok:
        return {}

    if not isinstance(payload, dict):
        return {}

    github_data = payload.get("github", {})
    if not isinstance(github_data, dict):
        return {}

    result: dict = {}
    for key, value in github_data.items():
        if value is None:
            continue
        result[str(key)] = str(value).strip()

    return result


def has_github_file_config() -> bool:
    return bool(load_github_file_config())


def get_github_token() -> str:
    return load_github_file_config().get("token", "")


def get_repo_owner() -> str:
    return load_github_file_config().get("owner", "")


def get_repo_name() -> str:
    return load_github_file_config().get("repo", "")


def get_repo_branch() -> str:
    return load_github_file_config().get("branch", "main")


def save_github_file_config(new_data: dict) -> tuple[bool, str]:
    if not isinstance(new_data, dict):
        return False, "Kaydedilecek veri geçersiz."

    current = load_github_file_config()
    merged = dict(current)

    for key, value in new_data.items():
        if value is None:
            continue
        merged[str(key)] = str(value).strip()

    payload = {"github": merged}
    return write_json_file(CONFIG_FILE, payload)


def update_github_token(token: str) -> tuple[bool, str]:
    clean_token = str(token or "").strip()
    if not clean_token:
        return False, "Token boş olamaz."

    return save_github_file_config({"token": clean_token})