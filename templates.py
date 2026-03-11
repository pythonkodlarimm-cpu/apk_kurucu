# -*- coding: utf-8 -*-
"""
DOSYA: app/core/templates.py
MODUL: app.core.templates
ROL:
- buildozer.spec / workflow / README / requirements / repo / api sablonlari
SURUM: 2
TARIH: 2026-03-11
"""

from __future__ import annotations

from app.core.helpers import mask_secret, split_csv_text


def build_buildozer_spec_template(data: dict) -> str:
    title = str(data.get("title", "APK Kurucu")).strip()
    package_name = str(data.get("package_name", "apk_kurucu")).strip()
    package_domain = str(data.get("package_domain", "org.example")).strip()
    version = str(data.get("version", "0.7.0")).strip()
    requirements = str(
        data.get("requirements", "python3,kivy==2.3.0,pyjnius==1.6.1")
    ).strip()
    android_api = str(data.get("android_api", "34")).strip()
    android_minapi = str(data.get("android_minapi", "24")).strip()
    android_ndk = str(data.get("android_ndk", "25b")).strip()
    android_archs = str(
        data.get("android_archs", "arm64-v8a, armeabi-v7a")
    ).strip()
    orientation = str(data.get("orientation", "portrait")).strip()
    icon_filename = str(
        data.get("icon_filename", "assets/icons/app_icon.png")
    ).strip()

    return f"""[app]

title = {title}
package.name = {package_name}
package.domain = {package_domain}

source.dir = .
source.include_exts = py,png,jpg,jpeg,kv,atlas,txt,md,json
source.include_patterns = assets/*,app/*

version = {version}

requirements = {requirements}

orientation = {orientation}
fullscreen = 0

icon.filename = {icon_filename}

android.api = {android_api}
android.minapi = {android_minapi}
android.ndk = {android_ndk}
android.archs = {android_archs}
android.accept_sdk_license = True

android.permissions = REQUEST_INSTALL_PACKAGES,READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE

android.add_compile_options = "-Wno-error=format-security"

log_level = 2
warn_on_root = 1
entrypoint = main.py


[buildozer]

log_level = 2
warn_on_root = 1
"""


def build_github_actions_template(data: dict) -> str:
    artifact_name = str(data.get("artifact_name", "apk_kurucu-debug-apk")).strip()

    return f"""name: Android APK Build

on:
  workflow_dispatch:
  push:
    branches:
      - main
      - master

jobs:
  build:
    runs-on: ubuntu-22.04

    steps:
      - name: Depoyu cek
        uses: actions/checkout@v4

      - name: Python kur
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: Java kur
        uses: actions/setup-java@v4
        with:
          distribution: temurin
          java-version: "17"

      - name: Sistem bagimliliklari
        run: |
          sudo apt-get update
          sudo apt-get install -y \\
            git zip unzip python3-pip autoconf libtool pkg-config \\
            zlib1g-dev cmake libffi-dev libssl-dev build-essential ccache \\
            openjdk-17-jdk

      - name: Python paketleri
        run: |
          python -m pip install --upgrade pip
          pip install buildozer "Cython<3"

      - name: Buildozer ile APK derle
        run: |
          yes | buildozer -v android debug

      - name: APK artifact yukle
        uses: actions/upload-artifact@v4
        with:
          name: {artifact_name}
          path: bin/*.apk
"""


def build_readme_template(data: dict) -> str:
    title = str(data.get("title", "APK Kurucu")).strip()
    version = str(data.get("version", "0.7.0")).strip()
    package_name = str(data.get("package_name", "apk_kurucu")).strip()
    package_domain = str(data.get("package_domain", "org.example")).strip()
    android_api = str(data.get("android_api", "34")).strip()
    android_minapi = str(data.get("android_minapi", "24")).strip()
    requirements = str(
        data.get("requirements", "python3,kivy==2.3.0,pyjnius==1.6.1")
    ).strip()

    return f"""# {title}

Surum: {version}

## Proje Ozeti

Bu proje Python + Kivy tabanli Android APK uretim altyapisi icin hazirlanmistir.

## Paket Bilgileri

- package.name: {package_name}
- package.domain: {package_domain}

## Android Ayarlari

- android.api: {android_api}
- android.minapi: {android_minapi}

## Requirements

{requirements}

## Yerelde Calistirma

python main.py

## APK Derleme

buildozer android debug

## GitHub Actions

Workflow dosyasi:
.github/workflows/android-build.yml

## Notlar

- Cikti genelde bin/ klasorune duser.
- Ilk build uzun surebilir.
- GitHub Actions workflow dosyasi ile bulutta build alinabilir.
"""


def build_requirements_template(data: dict) -> str:
    raw = str(
        data.get("requirements", "python3,kivy==2.3.0,pyjnius==1.6.1")
    ).strip()
    items = split_csv_text(raw)

    safe_lines: list[str] = []
    for item in items:
        lowered = item.lower()
        if lowered in {"python3", "android"}:
            continue
        safe_lines.append(item)

    if not safe_lines:
        safe_lines = ["kivy==2.3.0", "pyjnius==1.6.1"]

    return "\n".join(safe_lines) + "\n"


def build_gitignore_template() -> str:
    return """# Python
__pycache__/
*.pyc
*.pyo
*.pyd
.pytest_cache/

# Kivy
.kivy/

# Buildozer
.bin/
build/
bin/
.spec
buildozer.spec.backup

# Android / local
*.apk
*.aab
.gradle/
local.properties

# Private config
config/github_token.json

# IDE
.vscode/
.idea/

# OS
.DS_Store
Thumbs.db
"""


def build_build_commands_template(data: dict) -> str:
    title = str(data.get("title", "APK Kurucu")).strip()

    return f"""# BUILD COMMANDS

## Proje
{title}

## Yerelde calistirma
python main.py

## Test
pytest

## Buildozer ilk hazirlik
buildozer init

## Debug APK derleme
buildozer android debug

## Derlenen dosyalar
bin/

## Git islemleri
git init
git add .
git commit -m "ilk surum"

## GitHub'a gonderme
git branch -M main
git remote add origin REPO_URL
git push -u origin main

## GitHub Actions
- Repo'ya push yap
- Actions sekmesinden workflow calistir
- Artifact icinden APK indir
"""


def build_release_checklist_template(data: dict) -> str:
    version = str(data.get("version", "0.7.0")).strip()
    title = str(data.get("title", "APK Kurucu")).strip()

    return f"""# RELEASE CHECKLIST

## Uygulama
- Ad: {title}
- Surum: {version}

## Kontrol listesi
- [ ] Paket adi dogru mu
- [ ] Domain dogru mu
- [ ] Surum guncel mi
- [ ] Icon yolu dogru mu
- [ ] requirements guncel mi
- [ ] buildozer.spec olustu mu
- [ ] requirements.txt olustu mu
- [ ] README.md olustu mu
- [ ] .gitignore olustu mu
- [ ] GitHub workflow olustu mu
- [ ] Kod commit edildi mi
- [ ] GitHub'a push yapildi mi
- [ ] Actions build basarili mi
- [ ] Artifact icinden APK indirildi mi
- [ ] APK cihazda test edildi mi
"""


def build_push_commands_template(data: dict) -> str:
    owner = str(data.get("owner", "")).strip()
    repo = str(data.get("repo", "apk_kurucu")).strip()
    branch = str(data.get("branch", "main")).strip()
    remote_name = str(data.get("remote_name", "origin")).strip()

    https_url = ""
    if owner and repo:
        https_url = f"https://github.com/{owner}/{repo}.git"

    return f"""# PUSH COMMANDS

## Uzak repo
- owner: {owner or "-"}
- repo: {repo}
- branch: {branch}
- remote: {remote_name}

## HTTPS remote
{https_url or "OWNER ve REPO bilgisi eksik."}

## Ilk gonderim
git init
git add .
git commit -m "ilk surum"
git branch -M {branch}
git remote add {remote_name} {https_url or "REPO_URL"}
git push -u {remote_name} {branch}

## Guncelleme gonderimi
git add .
git commit -m "guncelleme"
git push {remote_name} {branch}
"""


def build_repo_info_template(data: dict) -> str:
    owner = str(data.get("owner", "")).strip()
    repo = str(data.get("repo", "apk_kurucu")).strip()
    branch = str(data.get("branch", "main")).strip()
    remote_name = str(data.get("remote_name", "origin")).strip()
    actions_url = str(data.get("actions_url", "")).strip()
    artifact_url = str(data.get("artifact_url", "")).strip()

    repo_url = ""
    if owner and repo:
        repo_url = f"https://github.com/{owner}/{repo}"

    return f"""# GITHUB REPO INFO

- owner: {owner or "-"}
- repo: {repo}
- branch: {branch}
- remote: {remote_name}
- repo_url: {repo_url or "-"}
- actions_url: {actions_url or "-"}
- artifact_url: {artifact_url or "-"}
"""


def build_build_status_template(data: dict) -> str:
    repo = str(data.get("repo", "apk_kurucu")).strip()
    branch = str(data.get("branch", "main")).strip()
    actions_url = str(data.get("actions_url", "")).strip()
    artifact_url = str(data.get("artifact_url", "")).strip()
    last_status = str(data.get("last_status", "Hazır")).strip()
    last_note = str(data.get("last_note", "")).strip()

    return f"""# BUILD STATUS

- repo: {repo}
- branch: {branch}
- last_status: {last_status}
- last_note: {last_note or "-"}
- actions_url: {actions_url or "-"}
- artifact_url: {artifact_url or "-"}
"""


def build_github_api_info_template(data: dict) -> str:
    api_base_url = str(data.get("api_base_url", "https://api.github.com")).strip()
    owner = str(data.get("owner", "")).strip()
    repo = str(data.get("repo", "apk_kurucu")).strip()
    branch = str(data.get("branch", "main")).strip()
    workflow_file_name = str(
        data.get("workflow_file_name", "android-build.yml")
    ).strip()
    token = str(data.get("token", "")).strip()

    masked = mask_secret(token)

    repo_api = "-"
    workflow_runs_api = "-"
    artifacts_api = "-"
    dispatch_api = "-"

    if owner and repo:
        repo_api = f"{api_base_url}/repos/{owner}/{repo}"
        workflow_runs_api = f"{api_base_url}/repos/{owner}/{repo}/actions/runs"
        artifacts_api = f"{api_base_url}/repos/{owner}/{repo}/actions/artifacts"
        dispatch_api = (
            f"{api_base_url}/repos/{owner}/{repo}"
            f"/actions/workflows/{workflow_file_name}/dispatches"
        )

    return f"""# GITHUB API INFO

- api_base_url: {api_base_url}
- owner: {owner or "-"}
- repo: {repo}
- branch: {branch}
- workflow_file_name: {workflow_file_name}
- token_masked: {masked or "-"}

## Endpoints
- repo_api: {repo_api}
- workflow_runs_api: {workflow_runs_api}
- artifacts_api: {artifacts_api}
- workflow_dispatch_api: {dispatch_api}
"""