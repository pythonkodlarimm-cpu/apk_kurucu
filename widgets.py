# -*- coding: utf-8 -*-
"""
DOSYA: app/ui/widgets.py
MODUL: app.ui.widgets
ROL:
- Ortak UI bilesenleri
SURUM: 3
TARIH: 2026-03-10
"""

from __future__ import annotations

from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label


class SectionTitle(Label):
    def __init__(self, text: str = "", **kwargs):
        super().__init__(**kwargs)
        self.text = text
        self.font_size = "26sp"
        self.bold = True
        self.size_hint_y = None
        self.height = dp(42)
        self.halign = "left"
        self.valign = "middle"
        self.text_size = (0, None)
        self.bind(size=self._update_text_size)

    def _update_text_size(self, *_args):
        self.text_size = (self.width, None)


class SectionSubtitle(Label):
    def __init__(self, text: str = "", **kwargs):
        super().__init__(**kwargs)
        self.text = text
        self.font_size = "14sp"
        self.size_hint_y = None
        self.height = dp(50)
        self.halign = "left"
        self.valign = "middle"
        self.text_size = (0, None)
        self.bind(size=self._update_text_size)

    def _update_text_size(self, *_args):
        self.text_size = (self.width, None)


class InfoRow(BoxLayout):
    def __init__(self, label_text: str, value_text: str = "", **kwargs):
        super().__init__(**kwargs)
        self.orientation = "horizontal"
        self.size_hint_y = None
        self.height = dp(34)
        self.spacing = dp(8)

        self.label_widget = Label(
            text=label_text,
            size_hint_x=0.32,
            halign="left",
            valign="middle",
            text_size=(0, None),
        )
        self.label_widget.bind(size=self._sync_label)

        self.value_widget = Label(
            text=value_text,
            size_hint_x=0.68,
            halign="left",
            valign="middle",
            text_size=(0, None),
        )
        self.value_widget.bind(size=self._sync_value)

        self.add_widget(self.label_widget)
        self.add_widget(self.value_widget)

    def _sync_label(self, *_args):
        self.label_widget.text_size = (self.label_widget.width, None)

    def _sync_value(self, *_args):
        self.value_widget.text_size = (self.value_widget.width, None)

    def set_value(self, value: str) -> None:
        self.value_widget.text = str(value)


class InfoCard(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.spacing = dp(6)
        self.padding = dp(12)
        self.size_hint_y = None
        self.height = dp(210)

        self.title_widget = Label(
            text="Dosya Bilgisi",
            bold=True,
            size_hint_y=None,
            height=dp(30),
            halign="left",
            valign="middle",
            text_size=(0, None),
        )
        self.title_widget.bind(size=self._sync_title)

        self.row_name = InfoRow("Dosya Adı:", "-")
        self.row_path = InfoRow("Dosya Yolu:", "-")
        self.row_size = InfoRow("Boyut:", "-")
        self.row_status = InfoRow("Durum:", "-")

        self.add_widget(self.title_widget)
        self.add_widget(self.row_name)
        self.add_widget(self.row_path)
        self.add_widget(self.row_size)
        self.add_widget(self.row_status)

    def _sync_title(self, *_args):
        self.title_widget.text_size = (self.title_widget.width, None)

    def update_info(self, *, name: str, path: str, size_text: str, status: str) -> None:
        self.row_name.set_value(name or "-")
        self.row_path.set_value(path or "-")
        self.row_size.set_value(size_text or "-")
        self.row_status.set_value(status or "-")


class StatusBox(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.spacing = dp(4)
        self.size_hint_y = None
        self.height = dp(100)

        self.title_widget = Label(
            text="Mesaj",
            bold=True,
            size_hint_y=None,
            height=dp(24),
            halign="left",
            valign="middle",
            text_size=(0, None),
        )
        self.title_widget.bind(size=self._sync_title)

        self.message_widget = Label(
            text="Hazır",
            halign="left",
            valign="top",
            text_size=(0, None),
        )
        self.message_widget.bind(size=self._sync_message)

        self.add_widget(self.title_widget)
        self.add_widget(self.message_widget)

    def _sync_title(self, *_args):
        self.title_widget.text_size = (self.title_widget.width, None)

    def _sync_message(self, *_args):
        self.message_widget.text_size = (self.message_widget.width, None)

    def set_message(self, message: str) -> None:
        self.message_widget.text = str(message)


class PrimaryButton(Button):
    def __init__(self, text: str = "", **kwargs):
        super().__init__(**kwargs)
        self.text = text
        self.size_hint_y = None
        self.height = dp(48)
        self.font_size = "16sp"


class SecondaryButton(Button):
    def __init__(self, text: str = "", **kwargs):
        super().__init__(**kwargs)
        self.text = text
        self.size_hint_y = None
        self.height = dp(44)
        self.font_size = "15sp"
