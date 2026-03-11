# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/build_screen.py
MODUL: app.ui.build_screen
ROL:
- buildozer.spec / README / requirements / workflow onizleme ve kaydetme
SURUM: 3
TARIH: 2026-03-10
"""

from __future__ import annotations

from pathlib import Path

from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput

from app.services.build_service import (
    generate_buildozer_spec_content,
    generate_readme_content,
    generate_requirements_content,
    save_all_project_files,
    save_buildozer_spec,
    save_readme,
    save_requirements_txt,
)
from app.services.github_service import generate_workflow_content, save_github_workflow
from app.ui.widgets import PrimaryButton, SectionSubtitle, SectionTitle, StatusBox


class BuildScreen(BoxLayout):
    def __init__(self, project_screen=None, github_screen=None, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.padding = dp(16)
        self.spacing = dp(10)

        self.project_screen = project_screen
        self.github_screen = github_screen

        self._build_ui()

    def _build_ui(self) -> None:
        self.title_widget = SectionTitle("Build Hazırlığı")
        self.subtitle_widget = SectionSubtitle(
            "buildozer.spec, README, requirements ve GitHub workflow üret."
        )

        self.project_root_input = TextInput(
            hint_text="Proje kök yolu",
            multiline=False,
            size_hint_y=None,
            height=dp(44),
            text=str(Path.cwd()),
        )

        self.preview_buildozer_button = PrimaryButton("buildozer.spec Önizleme")
        self.save_buildozer_button = PrimaryButton("buildozer.spec Kaydet")

        self.preview_readme_button = PrimaryButton("README Önizleme")
        self.save_readme_button = PrimaryButton("README Kaydet")

        self.preview_requirements_button = PrimaryButton("requirements Önizleme")
        self.save_requirements_button = PrimaryButton("requirements Kaydet")

        self.preview_github_button = PrimaryButton("Workflow Önizleme")
        self.save_github_button = PrimaryButton("Workflow Kaydet")

        self.save_all_button = PrimaryButton("Tümünü Kaydet")

        self.output_box = TextInput(
            hint_text="Üretilen içerik burada görünür",
            multiline=True,
            readonly=True,
        )

        self.status_box = StatusBox()

        self.preview_buildozer_button.bind(on_press=self.on_preview_buildozer)
        self.save_buildozer_button.bind(on_press=self.on_save_buildozer)

        self.preview_readme_button.bind(on_press=self.on_preview_readme)
        self.save_readme_button.bind(on_press=self.on_save_readme)

        self.preview_requirements_button.bind(on_press=self.on_preview_requirements)
        self.save_requirements_button.bind(on_press=self.on_save_requirements)

        self.preview_github_button.bind(on_press=self.on_preview_github)
        self.save_github_button.bind(on_press=self.on_save_github)

        self.save_all_button.bind(on_press=self.on_save_all)

        self.add_widget(self.title_widget)
        self.add_widget(self.subtitle_widget)
        self.add_widget(self.project_root_input)
        self.add_widget(self.preview_buildozer_button)
        self.add_widget(self.save_buildozer_button)
        self.add_widget(self.preview_readme_button)
        self.add_widget(self.save_readme_button)
        self.add_widget(self.preview_requirements_button)
        self.add_widget(self.save_requirements_button)
        self.add_widget(self.preview_github_button)
        self.add_widget(self.save_github_button)
        self.add_widget(self.save_all_button)
        self.add_widget(self.output_box)
        self.add_widget(self.status_box)

        self.status_box.title_widget.text = "Hazır"
        self.status_box.set_message("Build dosyaları oluşturulmaya hazır.")

    def _get_build_form_data(self) -> dict:
        if self.project_screen is None or not hasattr(self.project_screen, "get_form_data"):
            return {}
        return self.project_screen.get_form_data()

    def _get_github_form_data(self) -> dict:
        if self.github_screen is None or not hasattr(self.github_screen, "get_form_data"):
            return {}
        return self.github_screen.get_form_data()

    def on_preview_buildozer(self, _instance) -> None:
        raw = self._get_build_form_data()
        self.output_box.text = generate_buildozer_spec_content(raw)
        self.status_box.title_widget.text = "Önizleme"
        self.status_box.set_message("buildozer.spec içeriği üretildi.")

    def on_save_buildozer(self, _instance) -> None:
        ok, message = save_buildozer_spec(self.project_root_input.text.strip(), self._get_build_form_data())
        self.status_box.title_widget.text = "Tamam" if ok else "Hata"
        self.status_box.set_message(message)

    def on_preview_readme(self, _instance) -> None:
        raw = self._get_build_form_data()
        self.output_box.text = generate_readme_content(raw)
        self.status_box.title_widget.text = "Önizleme"
        self.status_box.set_message("README içeriği üretildi.")

    def on_save_readme(self, _instance) -> None:
        ok, message = save_readme(self.project_root_input.text.strip(), self._get_build_form_data())
        self.status_box.title_widget.text = "Tamam" if ok else "Hata"
        self.status_box.set_message(message)

    def on_preview_requirements(self, _instance) -> None:
        raw = self._get_build_form_data()
        self.output_box.text = generate_requirements_content(raw)
        self.status_box.title_widget.text = "Önizleme"
        self.status_box.set_message("requirements içeriği üretildi.")

    def on_save_requirements(self, _instance) -> None:
        ok, message = save_requirements_txt(self.project_root_input.text.strip(), self._get_build_form_data())
        self.status_box.title_widget.text = "Tamam" if ok else "Hata"
        self.status_box.set_message(message)

    def on_preview_github(self, _instance) -> None:
        self.output_box.text = generate_workflow_content(self._get_github_form_data())
        self.status_box.title_widget.text = "Önizleme"
        self.status_box.set_message("GitHub workflow içeriği üretildi.")

    def on_save_github(self, _instance) -> None:
        ok, message = save_github_workflow(
            self.project_root_input.text.strip(),
            self._get_github_form_data(),
        )
        self.status_box.title_widget.text = "Tamam" if ok else "Hata"
        self.status_box.set_message(message)

    def on_save_all(self, _instance) -> None:
        root = self.project_root_input.text.strip()

        ok1, msg1 = save_all_project_files(root, self._get_build_form_data())
        ok2, msg2 = save_github_workflow(root, self._get_github_form_data())

        message = msg1 + "\n" + msg2
        self.status_box.title_widget.text = "Tamam" if (ok1 and ok2) else "Hata"
        self.status_box.set_message(message)