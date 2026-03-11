# -*- coding: utf-8 -*-
"""
DOSYA: app/core/config.py
MODUL: app.core.config
ROL:
- Uygulama sabitleri
- Varsayilan proje/build/repo/api ayarlari
SURUM: 9
TARIH: 2026-03-11
"""

from __future__ import annotations

# =========================================================
# UYGULAMA GENEL
# =========================================================

APP_NAME = "APK Kurucu"
APP_PACKAGE_NAME = "apk_kurucu"
APP_PACKAGE_DOMAIN = "org.example"
APP_VERSION = "0.7.0"

# =========================================================
# DOSYA / APK AYARLARI
# =========================================================

SUPPORTED_EXTENSIONS = [".apk"]
APK_MIME_TYPE = "application/vnd.android.package-archive"

# =========================================================
# DURUM METİNLERİ
# =========================================================

STATUS_READY = "Hazır"
STATUS_NO_FILE = "Henüz dosya seçilmedi"
STATUS_FILE_SELECTED = "Dosya seçildi"
STATUS_APK_VALID = "APK doğrulandı"
STATUS_APK_INVALID = "Geçersiz APK"
STATUS_INSTALL_STARTED = "Kurulum başlatıldı"
STATUS_ERROR = "Hata oluştu"

# =========================================================
# ARAYÜZ METİNLERİ
# =========================================================

TEXT_APP_TITLE = "APK Kurucu"
TEXT_APP_SUBTITLE = "APK seç, doğrula, kurulum başlat ve build dosyalarını hazırla."

TEXT_SELECT_BUTTON = "APK Seç"
TEXT_INSTALL_BUTTON = "Kurulumu Başlat"
TEXT_CLEAR_BUTTON = "Temizle"

TEXT_LABEL_FILE_NAME = "Dosya Adı"
TEXT_LABEL_FILE_PATH = "Dosya Yolu"
TEXT_LABEL_FILE_SIZE = "Boyut"
TEXT_LABEL_FILE_STATUS = "Durum"

# =========================================================
# MESAJLAR
# =========================================================

MESSAGE_NO_FILE_SELECTED = "Henüz bir APK dosyası seçilmedi."
MESSAGE_FILE_NOT_FOUND = "Dosya bulunamadı."
MESSAGE_INVALID_EXTENSION = "Seçilen dosya .apk uzantılı değil."
MESSAGE_EMPTY_PATH = "Dosya yolu boş."
MESSAGE_NOT_A_FILE = "Seçilen yol bir dosya değil."
MESSAGE_APK_READY = "APK kuruluma hazır."
MESSAGE_INSTALLER_NOT_READY = "Android kurulum modülü hazır değil."
MESSAGE_UNKNOWN_ERROR = "Beklenmeyen bir hata oluştu."

# =========================================================
# UI AYARLARI
# =========================================================

UI_PADDING = 16
UI_SPACING = 12
UI_BUTTON_HEIGHT = 48
UI_INFO_CARD_HEIGHT = 220

MAX_PATH_PREVIEW_LENGTH = 64

# =========================================================
# PROJE VARSAYILANLARI
# =========================================================

DEFAULT_PROJECT_TITLE = "APK Kurucu"
DEFAULT_PACKAGE_NAME = "apk_kurucu"
DEFAULT_PACKAGE_DOMAIN = "org.example"
DEFAULT_VERSION = "0.7.0"

# Buildozer tarafinda kullanilacak requirements
DEFAULT_REQUIREMENTS = "python3,kivy==2.3.0,pyjnius"

# Android build ayarlari
DEFAULT_ANDROID_API = "34"
DEFAULT_ANDROID_MINAPI = "24"
DEFAULT_ANDROID_NDK = "25b"
DEFAULT_ANDROID_ARCHS = "arm64-v8a, armeabi-v7a"

DEFAULT_ORIENTATION = "portrait"
DEFAULT_ICON_FILENAME = "assets/icons/app_icon.png"

# =========================================================
# GITHUB / REPO AYARLARI
# =========================================================

DEFAULT_PROJECT_ROOT_NAME = "apk_kurucu"

DEFAULT_GITHUB_OWNER = ""
DEFAULT_GITHUB_REPO = "apk_kurucu"
DEFAULT_GITHUB_BRANCH = "main"
DEFAULT_GITHUB_REMOTE_NAME = "origin"

DEFAULT_GITHUB_WORKFLOW_NAME = "android-build"
DEFAULT_GITHUB_WORKFLOW_FILE_NAME = "android-build.yml"

DEFAULT_GITHUB_ARTIFACT_NAME = "apk_kurucu-debug-apk"
DEFAULT_GITHUB_ARTIFACT_URL = ""
DEFAULT_GITHUB_ACTIONS_URL = ""

DEFAULT_GITHUB_TOKEN = ""
DEFAULT_GITHUB_API_BASE_URL = "https://api.github.com"
DEFAULT_GITHUB_HTTP_TIMEOUT = 20

# =========================================================
# DOSYA ADLARI
# =========================================================

DEFAULT_GITIGNORE_NAME = ".gitignore"
DEFAULT_BUILD_COMMANDS_NAME = "BUILD_COMMANDS.md"
DEFAULT_RELEASE_CHECKLIST_NAME = "RELEASE_CHECKLIST.md"
DEFAULT_PUSH_COMMANDS_NAME = "PUSH_COMMANDS.md"
DEFAULT_BUILD_STATUS_NAME = "BUILD_STATUS.md"

# =========================================================
# ŞABLON DOSYA YOLLARI / ADLARI
# =========================================================

TEMPLATE_BUILDZER_FILENAME = "buildozer.spec"
TEMPLATE_REQUIREMENTS_FILENAME = "requirements.txt"
TEMPLATE_README_FILENAME = "README.md"

TEMPLATE_GITHUB_WORKFLOW_RELATIVE = ".github/workflows/android-build.yml"

TEMPLATE_GITIGNORE_FILENAME = ".gitignore"
TEMPLATE_BUILD_COMMANDS_FILENAME = "BUILD_COMMANDS.md"
TEMPLATE_RELEASE_CHECKLIST_FILENAME = "RELEASE_CHECKLIST.md"
TEMPLATE_PUSH_COMMANDS_FILENAME = "PUSH_COMMANDS.md"
TEMPLATE_BUILD_STATUS_FILENAME = "BUILD_STATUS.md"

TEMPLATE_GITHUB_REPO_INFO_FILENAME = "GITHUB_REPO_INFO.md"
TEMPLATE_GITHUB_API_INFO_FILENAME = "GITHUB_API_INFO.md"
