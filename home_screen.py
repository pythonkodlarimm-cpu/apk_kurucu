# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/home_screen.py
MODUL: app.ui.home_screen
ROL:
- APK secme, dogrulama, kurulum baslatma ekrani
SURUM: 2
TARIH: 2026-03-10
"""

from __future__ import annotations

from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput

from app.android.installer import (
    can_request_package_installs,
    install_apk,
    open_unknown_app_sources_settings,
)
from app.core.config import (
    MAX_PATH_PREVIEW_LENGTH,
    MESSAGE_NO_FILE_SELECTED,
    STATUS_NO_FILE,
    STATUS_READY,
    TEXT_APP_SUBTITLE,
    TEXT_APP_TITLE,
    TEXT_CLEAR_BUTTON,
    TEXT_INSTALL_BUTTON,
    TEXT_SELECT_BUTTON,
)
from app.core.helpers import shorten_text
from app.services.apk_service import build_empty_apk_info, get_apk_info
from app.services.file_service import get_demo_apk_path, pick_file, prepare_user_path
from app.ui.widgets import (
    InfoCard,
    PrimaryButton,
    SecondaryButton,
    SectionSubtitle,
    SectionTitle,
    StatusBox,
)


class HomeScreen(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.padding = dp(16)
        self.spacing = dp(12)

        self.selected_path = ""
        self.current_info = build_empty_apk_info()

        self._build_ui()
        self._refresh_info(self.current_info)
        self._set_status(STATUS_READY, MESSAGE_NO_FILE_SELECTED)

    def _build_ui(self) -> None:
        self.title_widget = SectionTitle(TEXT_APP_TITLE)
        self.subtitle_widget = SectionSubtitle(TEXT_APP_SUBTITLE)

        self.path_input = TextInput(
            hint_text="APK dosya yolunu buraya yaz",
            multiline=False,
            size_hint_y=None,
            height=dp(46),
        )

        self.info_card = InfoCard()
        self.status_box = StatusBox()

        self.button_row_top = BoxLayout(
            orientation="horizontal",
            spacing=dp(10),
            size_hint_y=None,
            height=dp(48),
        )

        self.button_row_bottom = BoxLayout(
            orientation="horizontal",
            spacing=dp(10),
            size_hint_y=None,
            height=dp(44),
        )

        self.select_button = PrimaryButton(TEXT_SELECT_BUTTON)
        self.install_button = PrimaryButton(TEXT_INSTALL_BUTTON)
        self.clear_button = SecondaryButton(TEXT_CLEAR_BUTTON)
        self.demo_button = SecondaryButton("Örnek APK Yolu Yükle")

        self.select_button.bind(on_press=self.on_select_pressed)
        self.install_button.bind(on_press=self.on_install_pressed)
        self.clear_button.bind(on_press=self.on_clear_pressed)
        self.demo_button.bind(on_press=self.on_demo_pressed)
        self.path_input.bind(text=self.on_path_text_changed)

        self.button_row_top.add_widget(self.select_button)
        self.button_row_top.add_widget(self.install_button)

        self.button_row_bottom.add_widget(self.demo_button)
        self.button_row_bottom.add_widget(self.clear_button)

        self.add_widget(self.title_widget)
        self.add_widget(self.subtitle_widget)
        self.add_widget(self.path_input)
        self.add_widget(self.info_card)
        self.add_widget(self.button_row_top)
        self.add_widget(self.button_row_bottom)
        self.add_widget(self.status_box)

    def on_path_text_changed(self, _instance, value: str) -> None:
        prepared = prepare_user_path(value)
        self.selected_path = prepared

        if not prepared:
            info = build_empty_apk_info()
            self.current_info = info
            self._refresh_info(info)
            self._set_status(STATUS_NO_FILE, MESSAGE_NO_FILE_SELECTED)
            return

        info = get_apk_info(prepared)
        self.current_info = info
        self._refresh_info(info)
        self._set_status(info.get("status", STATUS_READY), info.get("message", ""))

    def on_select_pressed(self, _instance) -> None:
        ok, picked_path, message = pick_file()

        if ok and picked_path:
            self.path_input.text = picked_path
            return

        raw_path = self.path_input.text.strip()
        prepared = prepare_user_path(raw_path)

        if not prepared:
            self._set_status("Dosya Seç", message or MESSAGE_NO_FILE_SELECTED)
            return

        info = get_apk_info(prepared)
        self.selected_path = prepared
        self.current_info = info
        self._refresh_info(info)
        self._set_status(info.get("status", STATUS_READY), info.get("message", ""))

    def on_install_pressed(self, _instance) -> None:
        info = self.current_info or build_empty_apk_info()

        if not info.get("is_valid", False):
            self._set_status(
                info.get("status", STATUS_NO_FILE),
                info.get("message", MESSAGE_NO_FILE_SELECTED),
            )
            return

        allowed, permission_message = can_request_package_installs()

        if not allowed:
            opened, opened_message = open_unknown_app_sources_settings()
            if opened:
                self._set_status(
                    "İzin Gerekli",
                    permission_message + "\nAyar ekranı açıldı. İzni verip geri dön.",
                )
                return

            self._set_status("İzin Gerekli", permission_message or opened_message)
            return

        success, message = install_apk(info.get("path", ""))
        if success:
            self._set_status("Kurulum Başlatıldı", message)
            return

        self._set_status("Kurulum Hatası", message)

    def on_clear_pressed(self, _instance) -> None:
        self.selected_path = ""
        self.current_info = build_empty_apk_info()
        self.path_input.text = ""
        self._refresh_info(self.current_info)
        self._set_status(STATUS_NO_FILE, MESSAGE_NO_FILE_SELECTED)

    def on_demo_pressed(self, _instance) -> None:
        self.path_input.text = get_demo_apk_path()

    def _refresh_info(self, info: dict) -> None:
        path_preview = shorten_text(info.get("path", ""), MAX_PATH_PREVIEW_LENGTH)

        self.info_card.update_info(
            name=info.get("name", ""),
            path=path_preview,
            size_text=info.get("size_text", "Bilinmiyor"),
            status=info.get("status", ""),
        )

    def _set_status(self, title: str, message: str) -> None:
        self.status_box.title_widget.text = str(title)
        self.status_box.set_message(message or "")
