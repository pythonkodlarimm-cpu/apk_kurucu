# -*- coding: utf-8 -*-

from __future__ import annotations

from app.core.config import (
    MESSAGE_APK_READY,
    MESSAGE_EMPTY_PATH,
    MESSAGE_FILE_NOT_FOUND,
    MESSAGE_INVALID_EXTENSION,
    MESSAGE_NOT_A_FILE,
    STATUS_APK_INVALID,
    STATUS_APK_VALID,
    STATUS_ERROR,
    SUPPORTED_EXTENSIONS,
)
from app.core.helpers import (
    format_file_size,
    get_extension,
    get_file_size,
    get_filename,
    normalize_path,
    path_exists,
    is_file,
)


def is_apk_file(path: str | None) -> bool:
    """
    Dosyanin .apk uzantili olup olmadigini kontrol eder.
    """
    extension = get_extension(path)
    return extension in SUPPORTED_EXTENSIONS


def validate_apk_path(path: str | None) -> tuple[bool, str]:
    """
    APK dosya yolunu dogrular.

    Donus:
        (gecerli_mi, mesaj)
    """
    normalized = normalize_path(path)

    if not normalized:
        return False, MESSAGE_EMPTY_PATH

    if not path_exists(normalized):
        return False, MESSAGE_FILE_NOT_FOUND

    if not is_file(normalized):
        return False, MESSAGE_NOT_A_FILE

    if not is_apk_file(normalized):
        return False, MESSAGE_INVALID_EXTENSION

    return True, MESSAGE_APK_READY


def get_apk_info(path: str | None) -> dict:
    """
    APK ile ilgili temel bilgileri dondurur.

    Ornek donus:
    {
        "path": "...",
        "name": "uygulama.apk",
        "extension": ".apk",
        "size_bytes": 12345,
        "size_text": "12.06 KB",
        "exists": True,
        "is_file": True,
        "is_apk": True,
        "is_valid": True,
        "message": "APK kuruluma hazır.",
        "status": "APK doğrulandı"
    }
    """
    normalized = normalize_path(path)
    exists = path_exists(normalized)
    file_flag = is_file(normalized)
    apk_flag = is_apk_file(normalized)
    valid, message = validate_apk_path(normalized)
    size_bytes = get_file_size(normalized)

    if valid:
        status = STATUS_APK_VALID
    elif normalized:
        status = STATUS_APK_INVALID
    else:
        status = STATUS_ERROR

    return {
        "path": normalized,
        "name": get_filename(normalized),
        "extension": get_extension(normalized),
        "size_bytes": size_bytes,
        "size_text": format_file_size(size_bytes),
        "exists": exists,
        "is_file": file_flag,
        "is_apk": apk_flag,
        "is_valid": valid,
        "message": message,
        "status": status,
    }


def build_empty_apk_info() -> dict:
    """
    Secim yokken kullanilacak varsayilan bilgi yapisi.
    """
    return {
        "path": "",
        "name": "",
        "extension": "",
        "size_bytes": -1,
        "size_text": "Bilinmiyor",
        "exists": False,
        "is_file": False,
        "is_apk": False,
        "is_valid": False,
        "message": MESSAGE_EMPTY_PATH,
        "status": STATUS_ERROR,
    }
