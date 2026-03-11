# -*- coding: utf-8 -*-
"""
DOSYA: main.py
ROL:
- Uygulama giris noktasi
- Ana ekran / Proje / GitHub / Build / Repo / Tracker sekmelerini barindirir
- Uzun ekranlari ScrollView ile kaydirilabilir yapar
SURUM: 7
TARIH: 2026-03-11
"""

from __future__ import annotations

from kivy.app import App
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.uix.scrollview import ScrollView

from app.core.config import APP_NAME
from app.ui.build_screen import BuildScreen
from app.ui.build_tracker_screen import BuildTrackerScreen
from app.ui.github_screen import GithubScreen
from app.ui.home_screen import HomeScreen
from app.ui.project_screen import ProjectScreen
from app.ui.repo_screen import RepoScreen


class RootContainer(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.spacing = dp(8)
        self.padding = dp(8)

        self.screen_manager = ScreenManager()

        self.project_screen_widget = ProjectScreen()
        self.github_screen_widget = GithubScreen()
        self.home_screen_widget = HomeScreen()
        self.build_screen_widget = BuildScreen(
            project_screen=self.project_screen_widget,
            github_screen=self.github_screen_widget,
        )
        self.repo_screen_widget = RepoScreen(
            project_screen=self.project_screen_widget,
            github_screen=self.github_screen_widget,
        )
        self.build_tracker_screen_widget = BuildTrackerScreen(
            github_screen=self.github_screen_widget,
        )

        self._build_navbar()
        self._build_screens()

    def _build_navbar(self) -> None:
        nav = BoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(48),
            spacing=dp(8),
        )

        home_button = Button(text="Ana")
        project_button = Button(text="Proje")
        github_button = Button(text="GitHub")
        build_button = Button(text="Build")
        repo_button = Button(text="Repo")
        tracker_button = Button(text="Takip")

        home_button.bind(on_press=lambda *_: self._switch_to("home"))
        project_button.bind(on_press=lambda *_: self._switch_to("project"))
        github_button.bind(on_press=lambda *_: self._switch_to("github"))
        build_button.bind(on_press=lambda *_: self._switch_to("build"))
        repo_button.bind(on_press=lambda *_: self._switch_to("repo"))
        tracker_button.bind(on_press=lambda *_: self._switch_to("tracker"))

        nav.add_widget(home_button)
        nav.add_widget(project_button)
        nav.add_widget(github_button)
        nav.add_widget(build_button)
        nav.add_widget(repo_button)
        nav.add_widget(tracker_button)

        self.add_widget(nav)

    def _wrap_scroll(self, widget):
        scroll = ScrollView(do_scroll_x=False, do_scroll_y=True)
        widget.size_hint_y = None
        widget.bind(minimum_height=widget.setter("height"))
        scroll.add_widget(widget)
        return scroll

    def _build_screens(self) -> None:
        home_screen = Screen(name="home")
        project_screen = Screen(name="project")
        github_screen = Screen(name="github")
        build_screen = Screen(name="build")
        repo_screen = Screen(name="repo")
        tracker_screen = Screen(name="tracker")

        home_screen.add_widget(self.home_screen_widget)
        project_screen.add_widget(self._wrap_scroll(self.project_screen_widget))
        github_screen.add_widget(self._wrap_scroll(self.github_screen_widget))
        build_screen.add_widget(self._wrap_scroll(self.build_screen_widget))
        repo_screen.add_widget(self._wrap_scroll(self.repo_screen_widget))
        tracker_screen.add_widget(self._wrap_scroll(self.build_tracker_screen_widget))

        self.screen_manager.add_widget(home_screen)
        self.screen_manager.add_widget(project_screen)
        self.screen_manager.add_widget(github_screen)
        self.screen_manager.add_widget(build_screen)
        self.screen_manager.add_widget(repo_screen)
        self.screen_manager.add_widget(tracker_screen)

        self.add_widget(self.screen_manager)

    def _switch_to(self, name: str) -> None:
        self.screen_manager.current = name


class ApkKurucuApp(App):
    def build(self):
        self.title = APP_NAME
        return RootContainer()


if __name__ == "__main__":
    ApkKurucuApp().run()