# -*- coding: utf-8 -*-

from __future__ import annotations

from app.core.helpers import normalize_path
from app.android.installer import is_android_environment


def pick_file() -> tuple[bool, str, str]:
    """
    Basit dosya secme giris noktasi.

    Donus:
        (basarili_mi, secilen_yol, mesaj)

    Not:
    - Bu surumde gercek Android belge secici entegre degil.
    - Simdilik kullanıcıya manuel yol girisi kullanilir.
    """
    if is_android_environment():
        return (
            False,
            "",
            "Bu surumde Android dosya secici henuz bagli degil. APK yolunu elle girin.",
        )

    return (
        False,
        "",
        "Masaustu ortaminda yerel dosya secici bagli degil. APK yolunu elle girin.",
    )


def get_demo_apk_path() -> str:
    """
    Test amacli ornek APK yolu.
    """
    return normalize_path("/storage/emulated/0/Download/ornek.apk")


def prepare_user_path(raw_path: str | None) -> str:
    """
    Kullanici metninden gelen yolu normalize eder.
    """
    return normalize_path(raw_path)


def path_to_display(path: str | None) -> str:
    """
    Arayuzde gostermek icin yolu duzenler.
    """
    return normalize_path(path)
