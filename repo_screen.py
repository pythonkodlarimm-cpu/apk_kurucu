# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/repo_screen.py
MODUL: app.ui.repo_screen
ROL:
- GitHub / repo hazirlik dosyalari onizleme ve kaydetme
SURUM: 3
TARIH: 2026-03-10
"""

from __future__ import annotations

from pathlib import Path

from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput

from app.core.helpers import merge_dicts
from app.services.export_service import (
    generate_build_commands_content,
    generate_build_status_content,
    generate_gitignore_content,
    generate_push_commands_content,
    generate_release_checklist_content,
    save_build_commands,
    save_build_status,
    save_gitignore,
    save_push_commands,
    save_release_checklist,
    save_repo_bundle,
)
from app.ui.widgets import PrimaryButton, SectionSubtitle, SectionTitle, StatusBox


class RepoScreen(BoxLayout):
    def __init__(self, project_screen=None, github_screen=None, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.padding = dp(16)
        self.spacing = dp(10)

        self.project_screen = project_screen
        self.github_screen = github_screen

        self._build_ui()

    def _build_ui(self) -> None:
        self.title_widget = SectionTitle("Repo / Yayın Hazırlığı")
        self.subtitle_widget = SectionSubtitle(
            "GitHub için .gitignore, build komutları, push komutları ve kontrol listesi üret."
        )

        self.project_root_input = TextInput(
            hint_text="Proje kök yolu",
            multiline=False,
            size_hint_y=None,
            height=dp(44),
            text=str(Path.cwd()),
        )

        self.preview_gitignore_button = PrimaryButton(".gitignore Önizleme")
        self.save_gitignore_button = PrimaryButton(".gitignore Kaydet")

        self.preview_commands_button = PrimaryButton("Build Commands Önizleme")
        self.save_commands_button = PrimaryButton("Build Commands Kaydet")

        self.preview_push_button = PrimaryButton("Push Commands Önizleme")
        self.save_push_button = PrimaryButton("Push Commands Kaydet")

        self.preview_checklist_button = PrimaryButton("Checklist Önizleme")
        self.save_checklist_button = PrimaryButton("Checklist Kaydet")

        self.preview_status_button = PrimaryButton("Build Status Önizleme")
        self.save_status_button = PrimaryButton("Build Status Kaydet")

        self.save_bundle_button = PrimaryButton("Repo Paketini Kaydet")

        self.output_box = TextInput(
            hint_text="Üretilen içerik burada görünür",
            multiline=True,
            readonly=True,
        )

        self.status_box = StatusBox()

        self.preview_gitignore_button.bind(on_press=self.on_preview_gitignore)
        self.save_gitignore_button.bind(on_press=self.on_save_gitignore)

        self.preview_commands_button.bind(on_press=self.on_preview_commands)
        self.save_commands_button.bind(on_press=self.on_save_commands)

        self.preview_push_button.bind(on_press=self.on_preview_push)
        self.save_push_button.bind(on_press=self.on_save_push)

        self.preview_checklist_button.bind(on_press=self.on_preview_checklist)
        self.save_checklist_button.bind(on_press=self.on_save_checklist)

        self.preview_status_button.bind(on_press=self.on_preview_status)
        self.save_status_button.bind(on_press=self.on_save_status)

        self.save_bundle_button.bind(on_press=self.on_save_bundle)

        self.add_widget(self.title_widget)
        self.add_widget(self.subtitle_widget)
        self.add_widget(self.project_root_input)

        self.add_widget(self.preview_gitignore_button)
        self.add_widget(self.save_gitignore_button)

        self.add_widget(self.preview_commands_button)
        self.add_widget(self.save_commands_button)

        self.add_widget(self.preview_push_button)
        self.add_widget(self.save_push_button)

        self.add_widget(self.preview_checklist_button)
        self.add_widget(self.save_checklist_button)

        self.add_widget(self.preview_status_button)
        self.add_widget(self.save_status_button)

        self.add_widget(self.save_bundle_button)
        self.add_widget(self.output_box)
        self.add_widget(self.status_box)

        self.status_box.title_widget.text = "Hazır"
        self.status_box.set_message("Repo dosyalari oluşturulmaya hazır.")

    def _get_form_data(self) -> dict:
        project_data = {}
        github_data = {}

        if self.project_screen is not None and hasattr(self.project_screen, "get_form_data"):
            project_data = self.project_screen.get_form_data()

        if self.github_screen is not None and hasattr(self.github_screen, "get_form_data"):
            github_data = self.github_screen.get_form_data()
            github_data.pop("token", None)

        return merge_dicts(project_data, github_data)

    def on_preview_gitignore(self, _instance) -> None:
        self.output_box.text = generate_gitignore_content()
        self.status_box.title_widget.text = "Önizleme"
        self.status_box.set_message(".gitignore içeriği üretildi.")

    def on_save_gitignore(self, _instance) -> None:
        ok, message = save_gitignore(self.project_root_input.text.strip())
        self.status_box.title_widget.text = "Tamam" if ok else "Hata"
        self.status_box.set_message(message)

    def on_preview_commands(self, _instance) -> None:
        self.output_box.text = generate_build_commands_content(self._get_form_data())
        self.status_box.title_widget.text = "Önizleme"
        self.status_box.set_message("Build komutlari üretildi.")

    def on_save_commands(self, _instance) -> None:
        ok, message = save_build_commands(self.project_root_input.text.strip(), self._get_form_data())
        self.status_box.title_widget.text = "Tamam" if ok else "Hata"
        self.status_box.set_message(message)

    def on_preview_push(self, _instance) -> None:
        self.output_box.text = generate_push_commands_content(self._get_form_data())
        self.status_box.title_widget.text = "Önizleme"
        self.status_box.set_message("Push komutlari üretildi.")

    def on_save_push(self, _instance) -> None:
        ok, message = save_push_commands(self.project_root_input.text.strip(), self._get_form_data())
        self.status_box.title_widget.text = "Tamam" if ok else "Hata"
        self.status_box.set_message(message)

    def on_preview_checklist(self, _instance) -> None:
        self.output_box.text = generate_release_checklist_content(self._get_form_data())
        self.status_box.title_widget.text = "Önizleme"
        self.status_box.set_message("Yayin checklist içeriği üretildi.")

    def on_save_checklist(self, _instance) -> None:
        ok, message = save_release_checklist(self.project_root_input.text.strip(), self._get_form_data())
        self.status_box.title_widget.text = "Tamam" if ok else "Hata"
        self.status_box.set_message(message)

    def on_preview_status(self, _instance) -> None:
        self.output_box.text = generate_build_status_content(self._get_form_data())
        self.status_box.title_widget.text = "Önizleme"
        self.status_box.set_message("Build status içeriği üretildi.")

    def on_save_status(self, _instance) -> None:
        ok, message = save_build_status(self.project_root_input.text.strip(), self._get_form_data())
        self.status_box.title_widget.text = "Tamam" if ok else "Hata"
        self.status_box.set_message(message)

    def on_save_bundle(self, _instance) -> None:
        ok, message = save_repo_bundle(self.project_root_input.text.strip(), self._get_form_data())
        self.status_box.title_widget.text = "Tamam" if ok else "Hata"
        self.status_box.set_message(message)