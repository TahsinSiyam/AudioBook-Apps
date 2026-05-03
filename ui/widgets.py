"""
Custom UI Widgets — Mobile Optimized
"""

from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.graphics import Color, RoundedRectangle, Rectangle
from kivy.metrics import dp, sp
from kivy.utils import platform
from kivy.logger import Logger
from kivy.app import App


# ── Rounded Button ──────────────────────────────────────────────────────────────
class RoundedButton(Button):
    """
    Mobile-friendly button:
    - 52dp default height (exceeds 48dp Material minimum)
    - Darkens on press for tactile feedback
    - Rounded corners
    """
    def __init__(self, bg_color=(0.2, 0.5, 0.9, 1), radius=dp(12), **kwargs):
        self.bg_color_val = bg_color
        self.bg_press_val = tuple(max(0, c - 0.12) if i < 3 else c
                                   for i, c in enumerate(bg_color))
        self.radius_val   = radius
        self._pressed     = False

        kwargs.setdefault("background_color", (0, 0, 0, 0))
        kwargs.setdefault("background_normal", "")
        kwargs.setdefault("background_down", "")
        kwargs.setdefault("color", (1, 1, 1, 1))
        kwargs.setdefault("font_size", sp(15))
        kwargs.setdefault("size_hint_y", None)
        kwargs.setdefault("height", dp(52))
        super().__init__(**kwargs)

        self.bind(
            size=lambda *a: self._draw_bg(),
            pos=lambda *a: self._draw_bg(),
            on_press=lambda *a: self._set_pressed(True),
            on_release=lambda *a: self._set_pressed(False),
        )
        self._draw_bg()

    def _set_pressed(self, val):
        self._pressed = val
        self._draw_bg()

    def _draw_bg(self):
        self.canvas.before.clear()
        color = self.bg_press_val if self._pressed else self.bg_color_val
        with self.canvas.before:
            Color(*color)
            RoundedRectangle(size=self.size, pos=self.pos, radius=[self.radius_val])


# ── Card Box ────────────────────────────────────────────────────────────────────
class CardBox(BoxLayout):
    """Vertical layout with a dark rounded card background. Auto-sizes to content."""

    def __init__(self, **kwargs):
        kwargs.setdefault("orientation", "vertical")
        kwargs.setdefault("size_hint_y", None)
        kwargs.setdefault("padding", dp(16))
        kwargs.setdefault("spacing", dp(10))
        super().__init__(**kwargs)
        self.bind(minimum_height=self.setter("height"))
        self.bind(size=lambda *a: self._draw_bg(), pos=lambda *a: self._draw_bg())

    def _draw_bg(self):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(0.13, 0.13, 0.20, 1)
            RoundedRectangle(size=self.size, pos=self.pos, radius=[dp(14)])


# ── WrapLabel ───────────────────────────────────────────────────────────────────
class WrapLabel(Label):
    """
    Label that properly wraps text on mobile.
    Automatically adjusts height to fit wrapped content.
    """
    def __init__(self, **kwargs):
        kwargs.setdefault("halign", "left")
        kwargs.setdefault("valign", "top")
        kwargs.setdefault("size_hint_y", None)
        kwargs.setdefault("font_size", sp(13))
        kwargs.setdefault("color", (0.75, 0.75, 0.85, 1))
        super().__init__(**kwargs)
        self.bind(width=self._update_text_size, texture_size=self._update_height)

    def _update_text_size(self, *args):
        self.text_size = (self.width, None)

    def _update_height(self, *args):
        self.height = max(self.texture_size[1] + dp(6), dp(20))


# ── Section Title ───────────────────────────────────────────────────────────────
class SectionTitle(Label):
    def __init__(self, text, **kwargs):
        kwargs.setdefault("font_size", sp(15))
        kwargs.setdefault("bold", True)
        kwargs.setdefault("color", (0.88, 0.88, 1.0, 1))
        kwargs.setdefault("size_hint_y", None)
        kwargs.setdefault("height", dp(32))
        kwargs.setdefault("halign", "left")
        kwargs.setdefault("valign", "middle")
        super().__init__(text=text, **kwargs)
        self.bind(width=lambda *a: setattr(self, "text_size", (self.width, None)))


# ── Status Label ────────────────────────────────────────────────────────────────
class StatusLabel(Label):
    """Auto-height label for status messages. Wraps and grows with content."""
    def __init__(self, text="", **kwargs):
        kwargs.setdefault("font_size", sp(13))
        kwargs.setdefault("color", (0.7, 0.75, 0.85, 1))
        kwargs.setdefault("size_hint_y", None)
        kwargs.setdefault("halign", "left")
        kwargs.setdefault("valign", "top")
        super().__init__(text=text, **kwargs)
        self.height = dp(40)
        self.bind(width=self._on_width, texture_size=self._on_texture)

    def _on_width(self, *args):
        self.text_size = (self.width, None)

    def _on_texture(self, *args):
        self.height = max(self.texture_size[1] + dp(8), dp(36))


# ── Divider ─────────────────────────────────────────────────────────────────────
class Divider(Widget):
    def __init__(self, **kwargs):
        kwargs.setdefault("size_hint_y", None)
        kwargs.setdefault("height", dp(1))
        super().__init__(**kwargs)
        with self.canvas:
            Color(0.22, 0.22, 0.32, 1)
            self._line = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=lambda *a: setattr(self._line, "size", self.size))
        self.bind(pos=lambda *a: setattr(self._line, "pos", self.pos))


# ── IconLabel (unused but kept for compatibility) ────────────────────────────────
class IconLabel(BoxLayout):
    def __init__(self, icon: str, text: str, **kwargs):
        kwargs.setdefault("orientation", "horizontal")
        kwargs.setdefault("size_hint_y", None)
        kwargs.setdefault("height", dp(32))
        kwargs.setdefault("spacing", dp(8))
        super().__init__(**kwargs)
        self.add_widget(Label(
            text=icon, font_size=sp(18),
            size_hint=(None, 1), width=dp(30),
        ))
        lbl = WrapLabel(text=text, font_size=sp(13))
        self.add_widget(lbl)


# ── Banner Ad Widget ─────────────────────────────────────────────────────────────
class BannerAdWidget(BoxLayout):
    """
    Native AdMob Banner wrapper.
    Android : embeds the real AdView.
    Desktop : shows a styled dev placeholder.
    """
    AD_HEIGHT = dp(52)

    def __init__(self, **kwargs):
        kwargs["orientation"] = "vertical"
        kwargs["size_hint_y"] = None
        kwargs["height"] = self.AD_HEIGHT
        super().__init__(**kwargs)

        with self.canvas.before:
            Color(0.05, 0.05, 0.09, 1)
            self._bg = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=lambda *a: setattr(self._bg, "size", self.size))
        self.bind(pos=lambda *a: setattr(self._bg, "pos", self.pos))

        if platform != "android":
            self.add_widget(Label(
                text="[ AdMob Banner Ad ]",
                font_size=sp(11),
                color=(0.4, 0.4, 0.55, 0.8),
                halign="center",
            ))

    def load(self):
        if platform != "android":
            return
        try:
            app = App.get_running_app()
            ad_view = app.admob.create_banner_ad()
            if ad_view:
                self._embed_android_view(ad_view)
        except Exception as e:
            Logger.error(f"BannerAdWidget: {e}")

    def _embed_android_view(self, java_view):
        try:
            from android.runnable import run_on_ui_thread

            @run_on_ui_thread
            def _add():
                from jnius import autoclass
                PythonActivity = autoclass("org.kivy.android.PythonActivity")
                activity = PythonActivity.mActivity
                activity.addContentView(java_view, java_view.getLayoutParams())
            _add()
        except Exception as e:
            Logger.error(f"BannerAdWidget embed: {e}")
