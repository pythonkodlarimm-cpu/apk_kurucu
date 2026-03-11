# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/github_screen.py
MODUL: app.ui.github_screen

ROL:
- GitHub repo bilgileri, token ve API hazırlık ekranı
- JSON dosyasındaki config'i otomatik yükleyebilir
- Hata durumunda çözüm metni gösterir
- Repo içeriğini listeleyebilir
- Dosyaları tıklayarak silebilir
- Yeni token'i config/github_token.json dosyasına yazabilir
"""

from __future__ import annotations

from pathlib import Path

from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput

from app.core.helpers import merge_dicts, pretty_json
from app.services.github_api_service import (
    build_artifacts_api_url,
    build_repo_api_url,
    build_safe_auth_headers,
    build_workflow_dispatch_api_url,
    build_workflow_dispatch_payload,
    build_workflow_runs_api_url,
    delete_repo_file,
    dispatch_workflow,
    explain_github_api_error,
    fetch_artifacts,
    fetch_repo_info,
    fetch_workflow_runs,
    generate_github_api_info_content,
    get_default_github_api_config,
    is_github_api_config_ready,
    list_repo_path,
)
from app.services.github_service import (
    generate_repo_info_content,
    generate_workflow_content,
    get_default_github_config,
    save_github_workflow,
    save_repo_info,
)
from app.services.state_service import load_state, merge_state
from app.services.token_service import (
    get_token_file_path,
    load_github_file_config,
    update_github_token,
)
from app.ui.widgets import PrimaryButton, SectionSubtitle, SectionTitle, StatusBox


class GithubScreen(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.padding = dp(16)
        self.spacing = dp(10)
        self.size_hint_y = None

        self.github_config = get_default_github_config()
        self.github_api_config = get_default_github_api_config()
        self.current_repo_path = ""

        self._build_ui()
        self._load_defaults()
        self._load_from_token_file()

        self.bind(minimum_height=self.setter("height"))

    def _build_ui(self) -> None:
        self.title_widget = SectionTitle("GitHub Ayarları")
        self.subtitle_widget = SectionSubtitle(
            "Owner, repo, branch, token, workflow ve repo dosyalarını burada yönet."
        )

        self.help_label = Label(
            text=(
                "Kullanim:\n"
                "1) Token JSON Yükle\n"
                "2) API Hazır mı?\n"
                "3) Repo Bilgisi Çek\n"
                "4) İçerik Listele\n"
                "5) Klasöre dokun, dosyayı silmek için Sil butonunu kullan\n"
                "6) Yeni token girip Token JSON'a Yaz ile token dosyasını güncelle"
            ),
            size_hint_y=None,
            height=dp(130),
            halign="left",
            valign="middle",
        )
        self.help_label.bind(size=self._update_help_text_size)

        self.owner_input = self._make_input("GitHub owner")
        self.repo_input = self._make_input("Repo adı")
        self.branch_input = self._make_input("Branch")
        self.remote_name_input = self._make_input("Remote adı")
        self.artifact_name_input = self._make_input("Artifact adı")
        self.actions_url_input = self._make_input("Actions URL")
        self.artifact_url_input = self._make_input("Artifact URL")

        self.api_base_url_input = self._make_input("GitHub API Base URL")
        self.workflow_file_name_input = self._make_input("Workflow dosya adı")
        self.timeout_input = self._make_input("HTTP timeout (sn)", "20")

        self.token_input = TextInput(
            hint_text="GitHub token (aktif form alanı)",
            multiline=False,
            password=True,
            size_hint_y=None,
            height=dp(44),
        )

        self.new_token_input = TextInput(
            hint_text="Yeni token yaz ve JSON'a kaydet",
            multiline=False,
            password=True,
            size_hint_y=None,
            height=dp(44),
        )

        self.project_root_input = self._make_input("Proje kök yolu", str(Path.cwd()))
        self.delete_commit_message_input = self._make_input(
            "Silme commit mesajı",
            "remove file from repo",
        )

        self.preview_workflow_button = PrimaryButton("Workflow Önizleme")
        self.save_workflow_button = PrimaryButton("Workflow Kaydet")
        self.preview_repo_info_button = PrimaryButton("Repo Info Önizleme")
        self.save_repo_info_button = PrimaryButton("Repo Info Kaydet")
        self.preview_api_info_button = PrimaryButton("API Info Önizleme")
        self.check_api_ready_button = PrimaryButton("API Hazır mı?")
        self.preview_endpoints_button = PrimaryButton("Endpoint Önizleme")
        self.load_json_button = PrimaryButton("Token JSON Yükle")
        self.save_token_json_button = PrimaryButton("Token JSON'a Yaz")

        self.fetch_repo_button = PrimaryButton("Repo Bilgisi Çek")
        self.fetch_runs_button = PrimaryButton("Workflow Run Listesi Çek")
        self.fetch_artifacts_button = PrimaryButton("Artifact Listesi Çek")
        self.dispatch_button = PrimaryButton("Workflow Dispatch Gönder")
        self.fetch_file_button = PrimaryButton("Dosya Bilgisi Çek")
        self.delete_file_button = PrimaryButton("GitHub Dosyasını Sil")
        self.list_root_button = PrimaryButton("Repo Kökünü Listele")
        self.go_parent_button = PrimaryButton("Üst Klasöre Çık")

        self.save_state_safe_button = PrimaryButton("Duruma Kaydet (Tokensiz)")
        self.save_state_full_button = PrimaryButton("Duruma Kaydet (Tokenli)")
        self.load_state_button = PrimaryButton("Durumdan Yükle")

        self.path_info_label = Label(
            text="Geçerli yol: /",
            size_hint_y=None,
            height=dp(36),
            halign="left",
            valign="middle",
        )
        self.path_info_label.bind(size=self._update_path_text_size)

        self.repo_list_container = BoxLayout(
            orientation="vertical",
            size_hint_y=None,
            spacing=dp(6),
            padding=(0, dp(4), 0, dp(4)),
        )
        self.repo_list_container.bind(
            minimum_height=self.repo_list_container.setter("height")
        )

        self.output_box = TextInput(
            hint_text="Üretilen içerik burada görünür",
            multiline=True,
            readonly=True,
            size_hint_y=None,
            height=dp(220),
        )

        self.status_box = StatusBox()

        self.preview_workflow_button.bind(on_press=self.on_preview_workflow)
        self.save_workflow_button.bind(on_press=self.on_save_workflow)
        self.preview_repo_info_button.bind(on_press=self.on_preview_repo_info)
        self.save_repo_info_button.bind(on_press=self.on_save_repo_info)
        self.preview_api_info_button.bind(on_press=self.on_preview_api_info)
        self.check_api_ready_button.bind(on_press=self.on_check_api_ready)
        self.preview_endpoints_button.bind(on_press=self.on_preview_endpoints)
        self.load_json_button.bind(on_press=self.on_load_json)
        self.save_token_json_button.bind(on_press=self.on_save_token_json)

        self.fetch_repo_button.bind(on_press=self.on_fetch_repo)
        self.fetch_runs_button.bind(on_press=self.on_fetch_runs)
        self.fetch_artifacts_button.bind(on_press=self.on_fetch_artifacts)
        self.dispatch_button.bind(on_press=self.on_dispatch_workflow)
        self.fetch_file_button.bind(on_press=self.on_fetch_file)
        self.delete_file_button.bind(on_press=self.on_delete_file)
        self.list_root_button.bind(on_press=self.on_list_root)
        self.go_parent_button.bind(on_press=self.on_go_parent)

        self.save_state_safe_button.bind(on_press=self.on_save_state_safe)
        self.save_state_full_button.bind(on_press=self.on_save_state_full)
        self.load_state_button.bind(on_press=self.on_load_state)

        self.add_widget(self.title_widget)
        self.add_widget(self.subtitle_widget)
        self.add_widget(self.help_label)

        self.add_widget(self.owner_input)
        self.add_widget(self.repo_input)
        self.add_widget(self.branch_input)
        self.add_widget(self.remote_name_input)
        self.add_widget(self.artifact_name_input)
        self.add_widget(self.actions_url_input)
        self.add_widget(self.artifact_url_input)
        self.add_widget(self.api_base_url_input)
        self.add_widget(self.workflow_file_name_input)
        self.add_widget(self.timeout_input)
        self.add_widget(self.token_input)
        self.add_widget(self.new_token_input)
        self.add_widget(self.project_root_input)
        self.add_widget(self.delete_commit_message_input)

        self.add_widget(self.preview_workflow_button)
        self.add_widget(self.save_workflow_button)
        self.add_widget(self.preview_repo_info_button)
        self.add_widget(self.save_repo_info_button)
        self.add_widget(self.preview_api_info_button)
        self.add_widget(self.check_api_ready_button)
        self.add_widget(self.preview_endpoints_button)
        self.add_widget(self.load_json_button)
        self.add_widget(self.save_token_json_button)

        self.add_widget(self.fetch_repo_button)
        self.add_widget(self.fetch_runs_button)
        self.add_widget(self.fetch_artifacts_button)
        self.add_widget(self.dispatch_button)
        self.add_widget(self.fetch_file_button)
        self.add_widget(self.delete_file_button)
        self.add_widget(self.list_root_button)
        self.add_widget(self.go_parent_button)

        self.add_widget(self.path_info_label)
        self.add_widget(self.repo_list_container)

        self.add_widget(self.save_state_safe_button)
        self.add_widget(self.save_state_full_button)
        self.add_widget(self.load_state_button)

        self.add_widget(self.output_box)
        self.add_widget(self.status_box)

        self.status_box.title_widget.text = "Hazır"
        self.status_box.set_message("GitHub ayarları ve API çağrıları hazır.")

    def _make_input(self, hint_text: str, text: str = "") -> TextInput:
        return TextInput(
            hint_text=hint_text,
            text=text,
            multiline=False,
            size_hint_y=None,
            height=dp(44),
        )

    def _update_help_text_size(self, instance, _value) -> None:
        instance.text_size = (instance.width - dp(12), None)

    def _update_path_text_size(self, instance, _value) -> None:
        instance.text_size = (instance.width - dp(12), None)

    def _load_defaults(self) -> None:
        self.owner_input.text = self.github_config.get("owner", "")
        self.repo_input.text = self.github_config.get("repo", "")
        self.branch_input.text = self.github_config.get("branch", "")
        self.remote_name_input.text = self.github_config.get("remote_name", "")
        self.artifact_name_input.text = self.github_config.get("artifact_name", "")
        self.actions_url_input.text = self.github_config.get("actions_url", "")
        self.artifact_url_input.text = self.github_config.get("artifact_url", "")

        self.api_base_url_input.text = self.github_api_config.get("api_base_url", "")
        self.workflow_file_name_input.text = self.github_api_config.get(
            "workflow_file_name",
            "",
        )
        self.timeout_input.text = self.github_api_config.get("timeout", "20")
        self.token_input.text = self.github_api_config.get("token", "")

    def _apply_form_data(self, data: dict) -> None:
        self.owner_input.text = data.get("owner", "")
        self.repo_input.text = data.get("repo", "")
        self.branch_input.text = data.get("branch", "")
        self.remote_name_input.text = data.get("remote_name", "")
        self.artifact_name_input.text = data.get("artifact_name", "")
        self.actions_url_input.text = data.get("actions_url", "")
        self.artifact_url_input.text = data.get("artifact_url", "")
        self.api_base_url_input.text = data.get("api_base_url", "")
        self.workflow_file_name_input.text = data.get("workflow_file_name", "")
        self.timeout_input.text = data.get("timeout", "20")
        self.token_input.text = data.get("token", "")

    def _load_from_token_file(self) -> None:
        file_data = load_github_file_config()
        if not file_data:
            return

        merged = merge_dicts(self.get_form_data(), file_data)
        self._apply_form_data(merged)
        self.status_box.title_widget.text = "Dosya"
        self.status_box.set_message(
            f"JSON config yüklendi: {get_token_file_path()}"
        )

    def get_form_data(self) -> dict:
        return {
            "owner": self.owner_input.text.strip(),
            "repo": self.repo_input.text.strip(),
            "branch": self.branch_input.text.strip(),
            "remote_name": self.remote_name_input.text.strip(),
            "artifact_name": self.artifact_name_input.text.strip(),
            "actions_url": self.actions_url_input.text.strip(),
            "artifact_url": self.artifact_url_input.text.strip(),
            "api_base_url": self.api_base_url_input.text.strip(),
            "workflow_file_name": self.workflow_file_name_input.text.strip(),
            "timeout": self.timeout_input.text.strip(),
            "token": self.token_input.text.strip(),
        }

    def _get_safe_form_data(self) -> dict:
        data = dict(self.get_form_data())
        data.pop("token", None)
        return data

    def _get_solution_text(self, payload: object) -> str:
        if isinstance(payload, dict):
            solution = str(payload.get("solution", "")).strip()
            if solution:
                return solution
        return explain_github_api_error(payload if isinstance(payload, dict) else None)

    def _set_current_path(self, repo_path: str) -> None:
        clean = str(repo_path or "").strip().strip("/")
        self.current_repo_path = clean
        self.path_info_label.text = f"Geçerli yol: /{clean}" if clean else "Geçerli yol: /"

    def _clear_repo_list(self) -> None:
        self.repo_list_container.clear_widgets()

    def _render_repo_items(self, items: list) -> None:
        self._clear_repo_list()

        if not items:
            empty_label = Label(
                text="Bu klasörde öğe yok.",
                size_hint_y=None,
                height=dp(36),
                halign="left",
                valign="middle",
            )
            empty_label.bind(
                size=lambda inst, _v: setattr(inst, "text_size", (inst.width - dp(12), None))
            )
            self.repo_list_container.add_widget(empty_label)
            return

        sorted_items = sorted(
            items,
            key=lambda x: (
                0 if str(x.get("type", "")) == "dir" else 1,
                str(x.get("name", "")).lower(),
            ),
        )

        for item in sorted_items:
            item_type = str(item.get("type", "")).strip()
            name = str(item.get("name", "")).strip()
            path = str(item.get("path", "")).strip()

            row = BoxLayout(
                orientation="horizontal",
                size_hint_y=None,
                height=dp(46),
                spacing=dp(6),
            )

            title = f"[Klasör] {name}" if item_type == "dir" else f"[Dosya] {name}"
            open_button = Button(text=title)

            if item_type == "dir":
                open_button.bind(on_press=lambda _btn, p=path: self._open_repo_path(p))
            else:
                open_button.bind(on_press=lambda _btn, p=path: self._show_selected_file(p))

            row.add_widget(open_button)

            if item_type == "file":
                delete_button = Button(
                    text="Sil",
                    size_hint_x=None,
                    width=dp(80),
                )
                delete_button.bind(
                    on_press=lambda _btn, p=path: self._delete_selected_file(p)
                )
                row.add_widget(delete_button)

            self.repo_list_container.add_widget(row)

    def _open_repo_path(self, repo_path: str) -> None:
        ok, payload = list_repo_path(self.get_form_data(), repo_path)
        self.output_box.text = pretty_json(payload)

        if not ok:
            solution = self._get_solution_text(payload)
            self.status_box.title_widget.text = "Hata"
            self.status_box.set_message("Klasör listelenemedi.\n" + solution)
            return

        data = payload.get("data", [])
        if isinstance(data, dict):
            data = [data]

        self._set_current_path(repo_path)
        self._render_repo_items(data)
        self.status_box.title_widget.text = "Tamam"
        self.status_box.set_message("Repo içeriği listelendi.")

    def _show_selected_file(self, file_path: str) -> None:
        self.output_box.text = f"Seçilen dosya: {file_path}"
        self.status_box.title_widget.text = "Dosya"
        self.status_box.set_message(f"Dosya seçildi: {file_path}")

    def _delete_selected_file(self, file_path: str) -> None:
        commit_message = self.delete_commit_message_input.text.strip()
        ok, payload = delete_repo_file(
            self.get_form_data(),
            file_path,
            commit_message,
        )
        self.output_box.text = pretty_json(payload)

        if ok:
            self.status_box.title_widget.text = "Tamam"
            self.status_box.set_message(f"Silindi: {file_path}")
            self._open_repo_path(self.current_repo_path)
            return

        solution = self._get_solution_text(payload)
        self.status_box.title_widget.text = "Hata"
        self.status_box.set_message("GitHub dosyası silinemedi.\n" + solution)

    def on_load_json(self, _instance) -> None:
        self._load_from_token_file()

    def on_save_token_json(self, _instance) -> None:
        new_token = self.new_token_input.text.strip()
        ok, message = update_github_token(new_token)

        self.status_box.title_widget.text = "Tamam" if ok else "Hata"
        self.status_box.set_message(message)

        if ok:
            self.token_input.text = new_token
            self.new_token_input.text = ""

    def on_preview_workflow(self, _instance) -> None:
        self.output_box.text = generate_workflow_content(self.get_form_data())
        self.status_box.title_widget.text = "Önizleme"
        self.status_box.set_message("Workflow içeriği üretildi.")

    def on_save_workflow(self, _instance) -> None:
        ok, message = save_github_workflow(
            self.project_root_input.text.strip(),
            self.get_form_data(),
        )
        self.status_box.title_widget.text = "Tamam" if ok else "Hata"
        self.status_box.set_message(message)

    def on_preview_repo_info(self, _instance) -> None:
        self.output_box.text = generate_repo_info_content(self.get_form_data())
        self.status_box.title_widget.text = "Önizleme"
        self.status_box.set_message("Repo info içeriği üretildi.")

    def on_save_repo_info(self, _instance) -> None:
        ok, message = save_repo_info(
            self.project_root_input.text.strip(),
            self.get_form_data(),
        )
        self.status_box.title_widget.text = "Tamam" if ok else "Hata"
        self.status_box.set_message(message)

    def on_preview_api_info(self, _instance) -> None:
        self.output_box.text = generate_github_api_info_content(
            self.get_form_data()
        )
        self.status_box.title_widget.text = "Önizleme"
        self.status_box.set_message("GitHub API info içeriği üretildi.")

    def on_check_api_ready(self, _instance) -> None:
        ok, message = is_github_api_config_ready(self.get_form_data())
        self.status_box.title_widget.text = "Hazır" if ok else "Eksik"
        self.status_box.set_message(message)

    def on_preview_endpoints(self, _instance) -> None:
        data = self.get_form_data()
        text = (
            "REPO API:\n"
            + build_repo_api_url(data)
            + "\n\nWORKFLOW RUNS API:\n"
            + build_workflow_runs_api_url(data)
            + "\n\nARTIFACTS API:\n"
            + build_artifacts_api_url(data)
            + "\n\nDISPATCH API:\n"
            + build_workflow_dispatch_api_url(data)
            + "\n\nHEADERS:\n"
            + pretty_json(build_safe_auth_headers(data))
            + "\n\nDISPATCH PAYLOAD:\n"
            + pretty_json(build_workflow_dispatch_payload(data))
        )
        self.output_box.text = text
        self.status_box.title_widget.text = "Önizleme"
        self.status_box.set_message(
            "API endpoint ve header önizlemesi üretildi."
        )

    def on_fetch_repo(self, _instance) -> None:
        ok, payload = fetch_repo_info(self.get_form_data())
        self.output_box.text = pretty_json(payload)

        if ok:
            self.status_box.title_widget.text = "Tamam"
            self.status_box.set_message("Repo bilgisi çekildi.")
            return

        solution = self._get_solution_text(payload)
        self.status_box.title_widget.text = "Hata"
        self.status_box.set_message("Repo bilgisi çekilemedi.\n" + solution)

    def on_fetch_runs(self, _instance) -> None:
        ok, payload = fetch_workflow_runs(self.get_form_data())
        self.output_box.text = pretty_json(payload)

        if ok:
            self.status_box.title_widget.text = "Tamam"
            self.status_box.set_message("Workflow run listesi çekildi.")
            return

        solution = self._get_solution_text(payload)
        self.status_box.title_widget.text = "Hata"
        self.status_box.set_message("Workflow run listesi çekilemedi.\n" + solution)

    def on_fetch_artifacts(self, _instance) -> None:
        ok, payload = fetch_artifacts(self.get_form_data())
        self.output_box.text = pretty_json(payload)

        if ok:
            self.status_box.title_widget.text = "Tamam"
            self.status_box.set_message("Artifact listesi çekildi.")
            return

        solution = self._get_solution_text(payload)
        self.status_box.title_widget.text = "Hata"
        self.status_box.set_message("Artifact listesi çekilemedi.\n" + solution)

    def on_dispatch_workflow(self, _instance) -> None:
        ok, payload = dispatch_workflow(self.get_form_data())
        self.output_box.text = pretty_json(payload)

        if ok:
            self.status_box.title_widget.text = "Tamam"
            self.status_box.set_message("Workflow dispatch gönderildi.")
            return

        solution = self._get_solution_text(payload)
        self.status_box.title_widget.text = "Hata"
        self.status_box.set_message("Workflow dispatch gönderilemedi.\n" + solution)

    def on_fetch_file(self, _instance) -> None:
        self.output_box.text = (
            "Elle dosya yolu yazmak yerine liste kullan.\n"
            "Repo Kökünü Listele → klasöre gir → dosya seç veya sil."
        )
        self.status_box.title_widget.text = "Bilgi"
        self.status_box.set_message("Dosya işlemleri için liste görünümünü kullan.")

    def on_delete_file(self, _instance) -> None:
        self.output_box.text = (
            "Silmek için önce repo listesinden dosyanın yanındaki Sil butonunu kullan."
        )
        self.status_box.title_widget.text = "Bilgi"
        self.status_box.set_message("Liste görünümünden silme yap.")

    def on_list_root(self, _instance) -> None:
        self._open_repo_path("")

    def on_go_parent(self, _instance) -> None:
        current = str(self.current_repo_path or "").strip().strip("/")
        if not current:
            self._open_repo_path("")
            return

        parts = current.split("/")
        parent = "/".join(parts[:-1]).strip("/")
        self._open_repo_path(parent)

    def on_save_state_safe(self, _instance) -> None:
        payload = {"github": self._get_safe_form_data()}
        ok, message = merge_state(
            self.project_root_input.text.strip(),
            payload,
        )
        self.status_box.title_widget.text = "Tamam" if ok else "Hata"
        self.status_box.set_message(message)

    def on_save_state_full(self, _instance) -> None:
        payload = {"github": self.get_form_data()}
        ok, message = merge_state(
            self.project_root_input.text.strip(),
            payload,
        )
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

        github_data = payload.get("github", {})
        if isinstance(github_data, dict):
            merged = merge_dicts(self.get_form_data(), github_data)
            self._apply_form_data(merged)
            self.status_box.title_widget.text = "Tamam"
            self.status_box.set_message(
                "GitHub ayarları durum dosyasından yüklendi."
            )
            return

        self.status_box.title_widget.text = "Hata"
        self.status_box.set_message("GitHub verisi bulunamadı.")