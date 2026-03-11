# -*- coding: utf-8 -*-

from __future__ import annotations

from app.core.config import APK_MIME_TYPE


def is_android_environment() -> bool:
    """
    Kodun Android ortaminda calisip calismadigini kontrol eder.
    """
    try:
        from jnius import autoclass  # noqa: F401
        return True
    except Exception:
        return False


def can_request_package_installs() -> tuple[bool, str]:
    """
    Android 8+ cihazlarda "unknown apps" / paket kurma izni durumunu kontrol eder.
    Android disinda False doner.
    """
    if not is_android_environment():
        return False, "Android ortami algilanmadi."

    try:
        from jnius import autoclass
        from android import mActivity

        PythonActivity = autoclass("org.kivy.android.PythonActivity")
        BuildVersion = autoclass("android.os.Build$VERSION")
        PackageManager = autoclass("android.content.pm.PackageManager")

        activity = mActivity if mActivity is not None else PythonActivity.mActivity

        if activity is None:
            return False, "Android activity bulunamadi."

        sdk_int = int(BuildVersion.SDK_INT)

        if sdk_int < 26:
            return True, "Android 8 oncesinde ayri paket kurma izni kontrolu gerekmez."

        package_manager = activity.getPackageManager()
        if package_manager is None:
            return False, "PackageManager alinamadi."

        allowed = bool(package_manager.canRequestPackageInstalls())
        if allowed:
            return True, "Paket kurma izni mevcut."

        return False, "Bu uygulama icin paket kurma izni kapali."
    except Exception as exc:
        return False, f"Izin kontrolu sirasinda hata olustu: {exc}"


def open_unknown_app_sources_settings() -> tuple[bool, str]:
    """
    Android 8+ icin uygulamaya ozel 'Install unknown apps' ayar ekranini acar.
    """
    if not is_android_environment():
        return False, "Android ortami algilanmadi."

    try:
        from jnius import autoclass, cast
        from android import mActivity

        PythonActivity = autoclass("org.kivy.android.PythonActivity")
        Intent = autoclass("android.content.Intent")
        Uri = autoclass("android.net.Uri")
        Settings = autoclass("android.provider.Settings")

        activity = mActivity if mActivity is not None else PythonActivity.mActivity
        if activity is None:
            return False, "Android activity bulunamadi."

        package_name = activity.getPackageName()
        uri = Uri.parse(f"package:{package_name}")

        intent = Intent(Settings.ACTION_MANAGE_UNKNOWN_APP_SOURCES, uri)
        intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)

        activity.startActivity(intent)
        return True, "Bilinmeyen uygulama kaynaklari ayari acildi."
    except Exception as exc:
        return False, f"Ayar ekrani acilamadi: {exc}"


def install_apk(apk_path: str) -> tuple[bool, str]:
    """
    Verilen APK dosyasi icin Android sistem kurulum ekranini acmaya calisir.

    Not:
    - Normal kullanici cihazlarinda sessiz kurulum yapmaz.
    - Sistem paket yukleyicisini acarak kullanici onayi ister.
    """
    if not apk_path:
        return False, "APK yolu bos."

    if not is_android_environment():
        return False, "Bu islem yalnizca Android cihazda calisir."

    try:
        from jnius import autoclass, cast
        from android import mActivity

        PythonActivity = autoclass("org.kivy.android.PythonActivity")
        Intent = autoclass("android.content.Intent")
        Uri = autoclass("android.net.Uri")
        File = autoclass("java.io.File")

        activity = mActivity if mActivity is not None else PythonActivity.mActivity
        if activity is None:
            return False, "Android activity bulunamadi."

        file_obj = File(apk_path)
        if not bool(file_obj.exists()):
            return False, "APK dosyasi bulunamadi."

        file_uri = Uri.fromFile(file_obj)

        intent = Intent(Intent.ACTION_VIEW)
        intent.setDataAndType(file_uri, APK_MIME_TYPE)
        intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
        intent.addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION)

        activity.startActivity(intent)
        return True, "Sistem kurulum ekrani acildi."
    except Exception as exc:
        return False, f"Kurulum baslatilamadi: {exc}"
