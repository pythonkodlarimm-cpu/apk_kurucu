# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/project_screen.py
MODUL: app.ui.project_screen
ROL:
- Proje ve build ayarlari formu
- Varsayilan build ayarlarini yukler
- Kullanma talimati gosterir
SURUM: 5
TARIH: 2026-03-11
"""

from __future__ import annotations

from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput

from app.services.build_service import bump_build_version, get_default_build_config
from app.ui.widgets import PrimaryButton, SectionSubtitle, SectionTitle, StatusBox


class ProjectScreen(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.padding = dp(16)
        self.spacing = dp(10)
        self.size_hint_y = None

        self.build_config = get_default_build_config()

        self._build_ui()
        self._load_defaults()

        self.bind(minimum_height=self.setter("height"))

    def _build_ui(self) -> None:
        self.title_widget = SectionTitle("Proje Ayarları")
        self.subtitle_widget = SectionSubtitle(
            "Uygulama adı, paket adı, sürüm ve Android build ayarlarını buradan yönet."
        )

        self.help_label = Label(
            text=(
                "Kullanim Talimati:\n"
                "1) Bu ekrandaki alanlar buildozer.spec, requirements.txt ve README uretiminde kullanilir.\n"
                "2) Varsayılanları Yükle butonu stabil ayarlari geri getirir.\n"
                "3) Sürüm +1 Patch butonu sürümün son rakamini arttirir.\n"
                "4) En kritik alanlar: Requirements, Android API, Min API, NDK, Archs ve ikon yolu.\n"
                "5) Build almadan once bu ekrandaki ayarlari kontrol et.\n"
                "6) Önerilen requirements: python3,kivy==2.3.0,pyjnius==1.6.1\n"
                "7) Önerilen Android ayarlari: API 34 / Min API 24 / NDK 25b."
            ),
            size_hint_y=None,
            height=dp(190),
            halign="left",
            valign="middle",
        )
        self.help_label.bind(size=self._update_help_text_size)

        self.title_input = self._make_input("Uygulama başlığı")
        self.package_name_input = self._make_input("Paket adı")
        self.package_domain_input = self._make_input("Paket domain")
        self.version_input = self._make_input("Sürüm")
        self.requirements_input = self._make_input("Requirements")
        self.android_api_input = self._make_input("Android API")
        self.android_minapi_input = self._make_input("Android Min API")
        self.android_ndk_input = self._make_input("Android NDK")
        self.android_archs_input = self._make_input("Android archs")
        self.orientation_input = self._make_input("Orientation")
        self.icon_input = self._make_input("İkon yolu")

        self.button_row = BoxLayout(
            orientation="horizontal",
            spacing=dp(10),
            size_hint_y=None,
            height=dp(48),
        )

        self.refresh_button = PrimaryButton("Varsayılanları Yükle")
        self.bump_version_button = PrimaryButton("Sürüm +1 Patch")

        self.status_box = StatusBox()

        self.refresh_button.bind(on_press=self.on_refresh_pressed)
        self.bump_version_button.bind(on_press=self.on_bump_version_pressed)

        self.button_row.add_widget(self.refresh_button)
        self.button_row.add_widget(self.bump_version_button)

        self.add_widget(self.title_widget)
        self.add_widget(self.subtitle_widget)
        self.add_widget(self.help_label)
        self.add_widget(self.title_input)
        self.add_widget(self.package_name_input)
        self.add_widget(self.package_domain_input)
        self.add_widget(self.version_input)
        self.add_widget(self.requirements_input)
        self.add_widget(self.android_api_input)
        self.add_widget(self.android_minapi_input)
        self.add_widget(self.android_ndk_input)
        self.add_widget(self.android_archs_input)
        self.add_widget(self.orientation_input)
        self.add_widget(self.icon_input)
        self.add_widget(self.button_row)
        self.add_widget(self.status_box)

        self.status_box.title_widget.text = "Bilgi"
        self.status_box.set_message("Proje ayarları hazır.")

    def _make_input(self, hint_text: str) -> TextInput:
        return TextInput(
            hint_text=hint_text,
            multiline=False,
            size_hint_y=None,
            height=dp(44),
        )

    def _update_help_text_size(self, instance, _value) -> None:
        instance.text_size = (instance.width - dp(12), None)

    def _load_defaults(self) -> None:
        self.title_input.text = self.build_config.get("title", "")
        self.package_name_input.text = self.build_config.get("package_name", "")
        self.package_domain_input.text = self.build_config.get("package_domain", "")
        self.version_input.text = self.build_config.get("version", "")
        self.requirements_input.text = self.build_config.get("requirements", "")
        self.android_api_input.text = self.build_config.get("android_api", "")
        self.android_minapi_input.text = self.build_config.get("android_minapi", "")
        self.android_ndk_input.text = self.build_config.get("android_ndk", "")
        self.android_archs_input.text = self.build_config.get("android_archs", "")
        self.orientation_input.text = self.build_config.get("orientation", "")
        self.icon_input.text = self.build_config.get("icon_filename", "")

    def _apply_form_data(self, data: dict) -> None:
        self.title_input.text = data.get("title", "")
        self.package_name_input.text = data.get("package_name", "")
        self.package_domain_input.text = data.get("package_domain", "")
        self.version_input.text = data.get("version", "")
        self.requirements_input.text = data.get("requirements", "")
        self.android_api_input.text = data.get("android_api", "")
        self.android_minapi_input.text = data.get("android_minapi", "")
        self.android_ndk_input.text = data.get("android_ndk", "")
        self.android_archs_input.text = data.get("android_archs", "")
        self.orientation_input.text = data.get("orientation", "")
        self.icon_input.text = data.get("icon_filename", "")

    def on_refresh_pressed(self, _instance) -> None:
        self.build_config = get_default_build_config()
        self._load_defaults()
        self.status_box.title_widget.text = "Tamam"
        self.status_box.set_message("Varsayılan build ayarları yüklendi.")

    def on_bump_version_pressed(self, _instance) -> None:
        updated = bump_build_version(self.get_form_data())
        self._apply_form_data(updated)
        self.status_box.title_widget.text = "Sürüm"
        self.status_box.set_message(
            f"Yeni sürüm: {updated.get('version', '')}"
        )

    def get_form_data(self) -> dict:
        return {
            "title": self.title_input.text.strip(),
            "package_name": self.package_name_input.text.strip(),
            "package_domain": self.package_domain_input.text.strip(),
            "version": self.version_input.text.strip(),
            "requirements": self.requirements_input.text.strip(),
            "android_api": self.android_api_input.text.strip(),
            "android_minapi": self.android_minapi_input.text.strip(),
            "android_ndk": self.android_ndk_input.text.strip(),
            "android_archs": self.android_archs_input.text.strip(),
            "orientation": self.orientation_input.text.strip(),
            "icon_filename": self.icon_input.text.strip(),
        }