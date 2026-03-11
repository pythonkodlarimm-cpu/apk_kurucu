# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/build_tracker_screen.py
MODUL: app.ui.build_tracker_screen
ROL:
- Build durum notlari, actions ve artifact bilgilerini yonetme
- GitHub API'den son run / artifact bilgisi cekebilme
SURUM: 3
TARIH: 2026-03-10
"""

from __future__ import annotations

from pathlib import Path

from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput

from app.core.helpers import pretty_json
from app.services.export_service import (
    generate_build_status_content,
    save_build_status,
)
from app.services.github_api_service import (
    fetch_artifacts,
    fetch_workflow_runs,
)
from app.services.state_service import load_state, merge_state
from app.ui.widgets import PrimaryButton, SectionSubtitle, SectionTitle, StatusBox


class BuildTrackerScreen(BoxLayout):
    def __init__(self, github_screen=None, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.padding = dp(16)
        self.spacing = dp(10)

        self.github_screen = github_screen

        self._build_ui()

    def _build_ui(self) -> None:
        self.title_widget = SectionTitle("Build Takibi")
        self.subtitle_widget = SectionSubtitle(
            "Workflow durumunu, notları ve artifact bağlantısını burada tut."
        )

        self.project_root_input = TextInput(
            hint_text="Proje kök yolu",
            multiline=False,
            size_hint_y=None,
            height=dp(44),
            text=str(Path.cwd()),
        )

        self.last_status_input = TextInput(
            hint_text="Son durum",
            multiline=False,
            size_hint_y=None,
            height=dp(44),
            text="Hazır",
        )

        self.last_note_input = TextInput(
            hint_text="Durum notu",
            multiline=True,
            size_hint_y=None,
            height=dp(88),
        )

        self.preview_button = PrimaryButton("Build Status Önizleme")
        self.save_button = PrimaryButton("Build Status Kaydet")
        self.fetch_runs_button = PrimaryButton("Run Listesi Çek")
        self.fetch_artifacts_button = PrimaryButton("Artifact Listesi Çek")
        self.save_state_button = PrimaryButton("Duruma Kaydet")
        self.load_state_button = PrimaryButton("Durumdan Yükle")

        self.output_box = TextInput(
            hint_text="Build status / API yaniti burada görünür",
            multiline=True,
            readonly=True,
        )

        self.status_box = StatusBox()

        self.preview_button.bind(on_press=self.on_preview)
        self.save_button.bind(on_press=self.on_save)
        self.fetch_runs_button.bind(on_press=self.on_fetch_runs)
        self.fetch_artifacts_button.bind(on_press=self.on_fetch_artifacts)
        self.save_state_button.bind(on_press=self.on_save_state)
        self.load_state_button.bind(on_press=self.on_load_state)

        self.add_widget(self.title_widget)
        self.add_widget(self.subtitle_widget)
        self.add_widget(self.project_root_input)
        self.add_widget(self.last_status_input)
        self.add_widget(self.last_note_input)
        self.add_widget(self.preview_button)
        self.add_widget(self.save_button)
        self.add_widget(self.fetch_runs_button)
        self.add_widget(self.fetch_artifacts_button)
        self.add_widget(self.save_state_button)
        self.add_widget(self.load_state_button)
        self.add_widget(self.output_box)
        self.add_widget(self.status_box)

        self.status_box.title_widget.text = "Hazır"
        self.status_box.set_message("Build takibi ekranı hazır.")

    def _get_form_data(self) -> dict:
        data = {
            "last_status": self.last_status_input.text.strip(),
            "last_note": self.last_note_input.text.strip(),
        }

        if self.github_screen is not None and hasattr(self.github_screen, "get_form_data"):
            github_data = self.github_screen.get_form_data()
            data.update(github_data)

        return data

    def on_preview(self, _instance) -> None:
        safe_data = dict(self._get_form_data())
        safe_data.pop("token", None)
        self.output_box.text = generate_build_status_content(safe_data)
        self.status_box.title_widget.text = "Önizleme"
        self.status_box.set_message("Build status içeriği üretildi.")

    def on_save(self, _instance) -> None:
        safe_data = dict(self._get_form_data())
        safe_data.pop("token", None)
        ok, message = save_build_status(self.project_root_input.text.strip(), safe_data)
        self.status_box.title_widget.text = "Tamam" if ok else "Hata"
        self.status_box.set_message(message)

    def on_fetch_runs(self, _instance) -> None:
        ok, payload = fetch_workflow_runs(self._get_form_data())
        self.output_box.text = pretty_json(payload)
        self.status_box.title_widget.text = "Tamam" if ok else "Hata"
        self.status_box.set_message("Run listesi çekildi." if ok else "Run listesi çekilemedi.")

    def on_fetch_artifacts(self, _instance) -> None:
        ok, payload = fetch_artifacts(self._get_form_data())
        self.output_box.text = pretty_json(payload)
        self.status_box.title_widget.text = "Tamam" if ok else "Hata"
        self.status_box.set_message("Artifact listesi çekildi." if ok else "Artifact listesi çekilemedi.")

    def on_save_state(self, _instance) -> None:
        safe_data = dict(self._get_form_data())
        safe_data.pop("token", None)
        data = {"build_tracker": safe_data}
        ok, message = merge_state(self.project_root_input.text.strip(), data)
        self.status_box.title_widget.text = "Tamam" if ok else "Hata"
        self.status_box.set_message(message)

    def on_load_state(self, _instance) -> None:
        ok, payload = load_state(self.project_root_input.text.strip())
        if not ok:
            self.status_box.title_widget.text = "Hata"
            self.status_box.set_message(str(payload))
            return

        if not isinstance(payload, dict):
            self.status_box.title_widget.text = "Hata"
            self.status_box.set_message("Durum verisi geçersiz.")
            return

        tracker_data = payload.get("build_tracker", {})
        if not isinstance(tracker_data, dict):
            self.status_box.title_widget.text = "Hata"
            self.status_box.set_message("Build tracker verisi bulunamadı.")
            return

        self.last_status_input.text = str(tracker_data.get("last_status", ""))
        self.last_note_input.text = str(tracker_data.get("last_note", ""))

        self.status_box.title_widget.text = "Tamam"
        self.status_box.set_message("Build tracker verisi durum dosyasından yüklendi.")