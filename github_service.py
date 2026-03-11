# -*- coding: utf-8 -*-
"""
DOSYA: app/services/github_service.py
MODUL: app.services.github_service

ROL:
- GitHub workflow icerigi uretir
- Repo bilgi icerigi uretir
- Workflow ve repo info dosyalarini kaydeder

SURUM: 1
TARIH: 2026-03-11
"""

from __future__ import annotations

from pathlib import Path

from app.core.config import (
    DEFAULT_GITHUB_ACTIONS_URL,
    DEFAULT_GITHUB_ARTIFACT_NAME,
    DEFAULT_GITHUB_ARTIFACT_URL,
    DEFAULT_GITHUB_BRANCH,
    DEFAULT_GITHUB_OWNER,
    DEFAULT_GITHUB_REMOTE_NAME,
    DEFAULT_GITHUB_REPO,
    TEMPLATE_GITHUB_REPO_INFO_FILENAME,
    TEMPLATE_GITHUB_WORKFLOW_RELATIVE,
)
from app.core.helpers import ensure_dir
from app.core.templates import (
    build_github_actions_template,
    build_repo_info_template,
)


def get_default_github_config() -> dict:
    return {
        "owner": DEFAULT_GITHUB_OWNER,
        "repo": DEFAULT_GITHUB_REPO,
        "branch": DEFAULT_GITHUB_BRANCH,
        "remote_name": DEFAULT_GITHUB_REMOTE_NAME,
        "artifact_name": DEFAULT_GITHUB_ARTIFACT_NAME,
        "actions_url": DEFAULT_GITHUB_ACTIONS_URL,
        "artifact_url": DEFAULT_GITHUB_ARTIFACT_URL,
    }


def normalize_github_config(raw: dict | None) -> dict:
    data = get_default_github_config()

    if not isinstance(raw, dict):
        return data

    for key in data:
        value = raw.get(key)
        if value is None:
            continue
        data[key] = str(value).strip()

    owner = data.get("owner", "").strip()
    repo = data.get("repo", "").strip()

    if owner and repo and not data.get("actions_url"):
        data["actions_url"] = f"https://github.com/{owner}/{repo}/actions"

    return data


def generate_workflow_content(raw: dict | None) -> str:
    data = normalize_github_config(raw)
    return build_github_actions_template(data)


def generate_repo_info_content(raw: dict | None) -> str:
    data = normalize_github_config(raw)
    return build_repo_info_template(data)


def save_github_workflow(
    project_root: str | Path,
    raw: dict | None,
) -> tuple[bool, str]:
    ok, info = ensure_dir(project_root)
    if not ok:
        return False, info

    try:
        target = Path(info) / TEMPLATE_GITHUB_WORKFLOW_RELATIVE
        target.parent.mkdir(parents=True, exist_ok=True)

        content = generate_workflow_content(raw)
        target.write_text(content, encoding="utf-8")

        return True, f"Kaydedildi: {target}"
    except Exception as exc:
        return False, f"Kaydedilemedi: {exc}"


def save_repo_info(
    project_root: str | Path,
    raw: dict | None,
) -> tuple[bool, str]:
    ok, info = ensure_dir(project_root)
    if not ok:
        return False, info

    try:
        target = Path(info) / TEMPLATE_GITHUB_REPO_INFO_FILENAME

        content = generate_repo_info_content(raw)
        target.write_text(content, encoding="utf-8")

        return True, f"Kaydedildi: {target}"
    except Exception as exc:
        return False, f"Kaydedilemedi: {exc}"