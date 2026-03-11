# -*- coding: utf-8 -*-
"""
DOSYA: app/services/github_api_service.py
MODUL: app.services.github_api_service

ROL:
- GitHub API icin token tabanli servis
- Endpoint / header / payload hazirlama
- Gercek GET / POST / DELETE istekleri
- JSON dosyasindaki github config ile birlesebilir
- Hata yorumu ve cozum metni uretir
"""

from __future__ import annotations

import json
import urllib.error
import urllib.parse
import urllib.request

from app.core.config import (
    DEFAULT_GITHUB_API_BASE_URL,
    DEFAULT_GITHUB_BRANCH,
    DEFAULT_GITHUB_HTTP_TIMEOUT,
    DEFAULT_GITHUB_OWNER,
    DEFAULT_GITHUB_REPO,
    DEFAULT_GITHUB_TOKEN,
    DEFAULT_GITHUB_WORKFLOW_FILE_NAME,
)
from app.core.helpers import mask_secret, merge_dicts
from app.core.templates import build_github_api_info_template
from app.services.token_service import load_github_file_config


def get_default_github_api_config() -> dict:
    return {
        "api_base_url": DEFAULT_GITHUB_API_BASE_URL,
        "owner": DEFAULT_GITHUB_OWNER,
        "repo": DEFAULT_GITHUB_REPO,
        "branch": DEFAULT_GITHUB_BRANCH,
        "workflow_file_name": DEFAULT_GITHUB_WORKFLOW_FILE_NAME,
        "token": DEFAULT_GITHUB_TOKEN,
        "timeout": str(DEFAULT_GITHUB_HTTP_TIMEOUT),
    }


def normalize_github_api_config(raw: dict | None) -> dict:
    defaults = get_default_github_api_config()
    file_data = load_github_file_config()

    merged = merge_dicts(defaults, file_data, raw)

    result: dict = {}
    for key, value in merged.items():
        if value is None:
            continue
        result[str(key)] = str(value).strip()

    if not result.get("timeout"):
        result["timeout"] = str(DEFAULT_GITHUB_HTTP_TIMEOUT)

    return result


def is_github_api_config_ready(raw: dict | None) -> tuple[bool, str]:
    data = normalize_github_api_config(raw)

    if not data.get("api_base_url"):
        return False, "API base URL boş."

    if not data.get("owner"):
        return False, "GitHub owner boş."

    if not data.get("repo"):
        return False, "GitHub repo boş."

    if not data.get("branch"):
        return False, "GitHub branch boş."

    if not data.get("workflow_file_name"):
        return False, "Workflow dosya adı boş."

    if not data.get("token"):
        return False, "GitHub token boş."

    return True, "GitHub API yapılandırması hazır."


def build_auth_headers(raw: dict | None) -> dict:
    data = normalize_github_api_config(raw)
    token = data.get("token", "").strip()

    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "apk_kurucu",
    }

    if token:
        headers["Authorization"] = f"Bearer {token}"

    return headers


def build_safe_auth_headers(raw: dict | None) -> dict:
    headers = dict(build_auth_headers(raw))

    if "Authorization" in headers:
        parts = headers["Authorization"].split(" ", 1)
        if len(parts) == 2:
            headers["Authorization"] = f"{parts[0]} {mask_secret(parts[1])}"
        else:
            headers["Authorization"] = mask_secret(headers["Authorization"])

    return headers


def build_repo_api_url(raw: dict | None) -> str:
    data = normalize_github_api_config(raw)
    return f"{data['api_base_url']}/repos/{data['owner']}/{data['repo']}"


def build_workflow_runs_api_url(raw: dict | None) -> str:
    data = normalize_github_api_config(raw)
    return f"{data['api_base_url']}/repos/{data['owner']}/{data['repo']}/actions/runs"


def build_artifacts_api_url(raw: dict | None) -> str:
    data = normalize_github_api_config(raw)
    return f"{data['api_base_url']}/repos/{data['owner']}/{data['repo']}/actions/artifacts"


def build_workflow_dispatch_api_url(raw: dict | None) -> str:
    data = normalize_github_api_config(raw)
    return (
        f"{data['api_base_url']}/repos/{data['owner']}/{data['repo']}"
        f"/actions/workflows/{data['workflow_file_name']}/dispatches"
    )


def build_contents_api_url(raw: dict | None, file_path: str) -> str:
    data = normalize_github_api_config(raw)
    clean_path = str(file_path or "").strip().lstrip("/")
    encoded_path = urllib.parse.quote(clean_path, safe="/")
    return (
        f"{data['api_base_url']}/repos/{data['owner']}/{data['repo']}"
        f"/contents/{encoded_path}"
    )


def build_workflow_dispatch_payload(raw: dict | None) -> dict:
    data = normalize_github_api_config(raw)
    return {
        "ref": data["branch"],
    }


def generate_github_api_info_content(raw: dict | None) -> str:
    data = normalize_github_api_config(raw)
    return build_github_api_info_template(data)


def _get_timeout(raw: dict | None) -> int:
    data = normalize_github_api_config(raw)

    try:
        timeout = int(data.get("timeout", DEFAULT_GITHUB_HTTP_TIMEOUT))
    except Exception:
        timeout = DEFAULT_GITHUB_HTTP_TIMEOUT

    if timeout <= 0:
        return DEFAULT_GITHUB_HTTP_TIMEOUT

    return timeout


def explain_github_api_error(payload: dict | None) -> str:
    if not isinstance(payload, dict):
        return "Bilinmeyen hata."

    status_code = int(payload.get("status_code", 0) or 0)
    error = payload.get("error", {})
    reason = str(payload.get("reason", "")).strip()

    message = ""
    if isinstance(error, dict):
        message = str(error.get("message", "")).strip()

    if status_code == 401:
        return (
            "401 Unauthorized: Token yanlış, süresi dolmuş ya da geçersiz. "
            "config/github_token.json içindeki token değerini kontrol et."
        )

    if status_code == 403:
        return (
            "403 Forbidden: Token yetkisi yetersiz olabilir. "
            "Fine-grained token içinde ilgili repo için uygun izinleri ver. "
            "Workflow işlemleri için 'Actions = Read and write', "
            "dosya silme/düzenleme için 'Contents = Read and write' gerekir."
        )

    if status_code == 404:
        return (
            "404 Not Found: Owner, repo, branch ya da dosya yolu yanlış olabilir. "
            "Repoda yolun gerçekten var olduğunu kontrol et."
        )

    if status_code == 409:
        return (
            "409 Conflict: Dosya SHA bilgisi eski olabilir ya da branch üzerinde çakışma var. "
            "Önce dosya bilgisini yeniden çekip tekrar dene."
        )

    if status_code == 422:
        return (
            "422 Unprocessable Entity: İstek ulaştı ama çalıştırılamadı. "
            "Branch adı, workflow dosya adı ya da gönderilen payload hatalı olabilir."
        )

    if message:
        return f"GitHub mesajı: {message}"

    if reason:
        return f"İstek hatası: {reason}"

    return "GitHub API isteği başarısız oldu."


def _mask_headers_for_debug(headers: dict) -> dict:
    safe_debug_headers = dict(headers)
    if "Authorization" in safe_debug_headers:
        parts = safe_debug_headers["Authorization"].split(" ", 1)
        if len(parts) == 2:
            safe_debug_headers["Authorization"] = (
                f"{parts[0]} {mask_secret(parts[1])}"
            )
        else:
            safe_debug_headers["Authorization"] = mask_secret(
                safe_debug_headers["Authorization"]
            )
    return safe_debug_headers


def _request_json(
    *,
    method: str,
    url: str,
    headers: dict,
    payload: dict | None,
    timeout: int,
) -> tuple[bool, dict]:
    body_bytes = None

    if payload is not None:
        body_bytes = json.dumps(payload).encode("utf-8")

    request = urllib.request.Request(
        url=url,
        data=body_bytes,
        headers=headers,
        method=method.upper(),
    )

    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            raw_text = response.read().decode("utf-8", errors="replace")
            status_code = int(getattr(response, "status", 200))

            try:
                parsed = json.loads(raw_text) if raw_text else {}
            except Exception:
                parsed = {"raw_text": raw_text}

            return True, {
                "ok": True,
                "status_code": status_code,
                "data": parsed,
                "url": url,
                "debug": {
                    "method": method.upper(),
                    "headers": _mask_headers_for_debug(headers),
                    "payload": payload,
                    "timeout": timeout,
                },
            }

    except urllib.error.HTTPError as exc:
        try:
            error_text = exc.read().decode("utf-8", errors="replace")
            parsed = json.loads(error_text) if error_text else {}
        except Exception:
            parsed = {"raw_text": str(exc)}

        result = {
            "ok": False,
            "status_code": int(getattr(exc, "code", 0) or 0),
            "error": parsed,
            "reason": str(exc),
            "url": url,
            "debug": {
                "method": method.upper(),
                "headers": _mask_headers_for_debug(headers),
                "payload": payload,
                "timeout": timeout,
            },
        }
        result["solution"] = explain_github_api_error(result)
        return False, result

    except urllib.error.URLError as exc:
        result = {
            "ok": False,
            "status_code": 0,
            "error": {"message": str(exc)},
            "reason": str(exc),
            "url": url,
            "debug": {
                "method": method.upper(),
                "headers": _mask_headers_for_debug(headers),
                "payload": payload,
                "timeout": timeout,
            },
        }
        result["solution"] = explain_github_api_error(result)
        return False, result

    except Exception as exc:
        result = {
            "ok": False,
            "status_code": 0,
            "error": {"message": str(exc)},
            "reason": str(exc),
            "url": url,
            "debug": {
                "method": method.upper(),
                "headers": _mask_headers_for_debug(headers),
                "payload": payload,
                "timeout": timeout,
            },
        }
        result["solution"] = explain_github_api_error(result)
        return False, result


def fetch_repo_info(raw: dict | None) -> tuple[bool, dict]:
    ok, message = is_github_api_config_ready(raw)
    if not ok:
        return False, {
            "ok": False,
            "message": message,
            "solution": message,
        }

    return _request_json(
        method="GET",
        url=build_repo_api_url(raw),
        headers=build_auth_headers(raw),
        payload=None,
        timeout=_get_timeout(raw),
    )


def fetch_workflow_runs(raw: dict | None) -> tuple[bool, dict]:
    ok, message = is_github_api_config_ready(raw)
    if not ok:
        return False, {
            "ok": False,
            "message": message,
            "solution": message,
        }

    return _request_json(
        method="GET",
        url=build_workflow_runs_api_url(raw),
        headers=build_auth_headers(raw),
        payload=None,
        timeout=_get_timeout(raw),
    )


def fetch_artifacts(raw: dict | None) -> tuple[bool, dict]:
    ok, message = is_github_api_config_ready(raw)
    if not ok:
        return False, {
            "ok": False,
            "message": message,
            "solution": message,
        }

    return _request_json(
        method="GET",
        url=build_artifacts_api_url(raw),
        headers=build_auth_headers(raw),
        payload=None,
        timeout=_get_timeout(raw),
    )


def dispatch_workflow(raw: dict | None) -> tuple[bool, dict]:
    ok, message = is_github_api_config_ready(raw)
    if not ok:
        return False, {
            "ok": False,
            "message": message,
            "solution": message,
        }

    return _request_json(
        method="POST",
        url=build_workflow_dispatch_api_url(raw),
        headers=build_auth_headers(raw),
        payload=build_workflow_dispatch_payload(raw),
        timeout=_get_timeout(raw),
    )


def fetch_file_metadata(raw: dict | None, file_path: str) -> tuple[bool, dict]:
    ok, message = is_github_api_config_ready(raw)
    if not ok:
        return False, {
            "ok": False,
            "message": message,
            "solution": message,
        }

    clean_path = str(file_path or "").strip()
    if not clean_path:
        return False, {
            "ok": False,
            "message": "Dosya yolu boş.",
            "solution": (
                "Repo içi dosya yolunu gir. "
                "Örnek: README.md veya .github/workflows/android-build.yml"
            ),
        }

    return _request_json(
        method="GET",
        url=build_contents_api_url(raw, clean_path),
        headers=build_auth_headers(raw),
        payload=None,
        timeout=_get_timeout(raw),
    )


def delete_repo_file(
    raw: dict | None,
    file_path: str,
    commit_message: str,
) -> tuple[bool, dict]:
    ok, message = is_github_api_config_ready(raw)
    if not ok:
        return False, {
            "ok": False,
            "message": message,
            "solution": message,
        }

    clean_path = str(file_path or "").strip()
    if not clean_path:
        return False, {
            "ok": False,
            "message": "Dosya yolu boş.",
            "solution": (
                "Repo içi dosya yolunu gir. "
                "Örnek: README.md veya .github/workflows/android-build.yml"
            ),
        }

    ok_meta, meta_payload = fetch_file_metadata(raw, clean_path)
    if not ok_meta:
        return False, meta_payload

    data = meta_payload.get("data", {})
    sha = ""
    if isinstance(data, dict):
        sha = str(data.get("sha", "")).strip()

    if not sha:
        return False, {
            "ok": False,
            "message": "Dosya SHA bilgisi alınamadı.",
            "solution": (
                "Dosya gerçekten var mı kontrol et. "
                "Yol birebir doğru olmalı."
            ),
        }

    cfg = normalize_github_api_config(raw)
    payload = {
        "message": str(commit_message or "").strip() or f"Delete {clean_path}",
        "sha": sha,
        "branch": cfg.get("branch", "main"),
    }

    return _request_json(
        method="DELETE",
        url=build_contents_api_url(raw, clean_path),
        headers=build_auth_headers(raw),
        payload=payload,
        timeout=_get_timeout(raw),
    )


def list_repo_path(raw: dict | None, repo_path: str = "") -> tuple[bool, dict]:
    ok, message = is_github_api_config_ready(raw)
    if not ok:
        return False, {
            "ok": False,
            "message": message,
            "solution": message,
        }

    clean_path = str(repo_path or "").strip().lstrip("/")

    return _request_json(
        method="GET",
        url=build_contents_api_url(raw, clean_path),
        headers=build_auth_headers(raw),
        payload=None,
        timeout=_get_timeout(raw),
    )