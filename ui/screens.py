"""
UI Screens for PDF AudioBook App
Screens:  SplashScreen → HomeScreen → GenerateScreen
"""

import os
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.progressbar import ProgressBar
from kivy.uix.scrollview import ScrollView
from kivy.uix.image import AsyncImage
from kivy.clock import Clock
from kivy.utils import platform
from kivy.metrics import dp, sp
from kivy.graphics import Color, RoundedRectangle, Rectangle
from kivy.logger import Logger
from kivy.app import App

from core.pdf_extractor import PDFExtractor
from core.tts_engine import TTSEngine
from core.file_picker import FilePicker
from ui.widgets import (
    RoundedButton, CardBox, BannerAdWidget, StatusLabel,
    SectionTitle, IconLabel, Divider
)


# ═══════════════════════════════════════════════════════════════════════════════
# SPLASH SCREEN
# ═══════════════════════════════════════════════════════════════════════════════
class SplashScreen(Screen):
    def on_enter(self):
        Clock.schedule_once(self._go_home, 2.5)

    def _go_home(self, dt):
        self.manager.current = "home"
        self.manager.transition = FadeTransition(duration=0.4)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = FloatLayout()
        with layout.canvas.before:
            Color(0.08, 0.08, 0.12, 1)
            self._bg = Rectangle(size=layout.size, pos=layout.pos)
        layout.bind(size=lambda *a: setattr(self._bg, "size", layout.size))
        layout.bind(pos=lambda *a: setattr(self._bg, "pos", layout.pos))

        # App icon / emoji label
        icon = Label(
            text="🎧",
            font_size=sp(72),
            pos_hint={"center_x": 0.5, "center_y": 0.6},
            size_hint=(None, None),
            size=(dp(100), dp(100)),
        )
        layout.add_widget(icon)

        title = Label(
            text="PDF AudioBook",
            font_size=sp(28),
            bold=True,
            color=(1, 1, 1, 1),
            pos_hint={"center_x": 0.5, "center_y": 0.48},
        )
        layout.add_widget(title)

        sub = Label(
            text="Turn any PDF into speech",
            font_size=sp(14),
            color=(0.7, 0.7, 0.8, 1),
            pos_hint={"center_x": 0.5, "center_y": 0.41},
        )
        layout.add_widget(sub)

        loading = Label(
            text="Loading...",
            font_size=sp(12),
            color=(0.5, 0.5, 0.6, 1),
            pos_hint={"center_x": 0.5, "center_y": 0.15},
        )
        layout.add_widget(loading)

        self.add_widget(layout)


# ═══════════════════════════════════════════════════════════════════════════════
# HOME SCREEN — PDF Selection
# ═══════════════════════════════════════════════════════════════════════════════
class HomeScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.extractor = PDFExtractor()
        self.picker = FilePicker()
        self.selected_pdf = None
        self._build_ui()

    def _build_ui(self):
        root = BoxLayout(orientation="vertical", spacing=0)

        # ── Background
        with root.canvas.before:
            Color(0.08, 0.08, 0.12, 1)
            self._bg = Rectangle(size=root.size, pos=root.pos)
        root.bind(size=lambda *a: setattr(self._bg, "size", root.size))
        root.bind(pos=lambda *a: setattr(self._bg, "pos", root.pos))

        # ── Header
        header = BoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(60),
            padding=[dp(16), dp(8)],
        )
        with header.canvas.before:
            Color(0.12, 0.12, 0.18, 1)
            self._hbg = Rectangle(size=header.size, pos=header.pos)
        header.bind(size=lambda *a: setattr(self._hbg, "size", header.size))
        header.bind(pos=lambda *a: setattr(self._hbg, "pos", header.pos))

        header.add_widget(Label(
            text="🎧  PDF AudioBook",
            font_size=sp(20),
            bold=True,
            color=(1, 1, 1, 1),
            halign="left",
            text_size=(None, None),
        ))
        root.add_widget(header)

        # ── Scrollable Body
        scroll = ScrollView(do_scroll_x=False)
        body = BoxLayout(
            orientation="vertical",
            padding=dp(16),
            spacing=dp(16),
            size_hint_y=None,
        )
        body.bind(minimum_height=body.setter("height"))

        # Welcome card
        welcome_card = CardBox(padding=dp(20), spacing=dp(10))
        welcome_card.add_widget(Label(
            text="Welcome! 👋",
            font_size=sp(20),
            bold=True,
            color=(1, 1, 1, 1),
            size_hint_y=None,
            height=dp(30),
            halign="left",
            text_size=(None, None),
        ))
        welcome_card.add_widget(Label(
            text=(
                "Select a PDF file from your device and we'll convert it "
                "into a full AudioBook MP3 you can listen to or download."
            ),
            font_size=sp(13),
            color=(0.75, 0.75, 0.85, 1),
            size_hint_y=None,
            height=dp(55),
            halign="left",
            valign="top",
            text_size=(self.width - dp(64), None),
        ))
        body.add_widget(welcome_card)

        # PDF picker card
        picker_card = CardBox(padding=dp(20), spacing=dp(14))
        picker_card.add_widget(SectionTitle("📄  Select PDF File"))

        # Selected file display
        self.file_label = Label(
            text="No file selected",
            font_size=sp(13),
            color=(0.55, 0.55, 0.65, 1),
            size_hint_y=None,
            height=dp(48),
            halign="left",
            valign="middle",
            text_size=(None, None),
        )
        picker_card.add_widget(self.file_label)

        pick_btn = RoundedButton(
            text="📂  Browse & Select PDF",
            size_hint_y=None,
            height=dp(50),
            bg_color=(0.18, 0.42, 0.82, 1),
        )
        pick_btn.bind(on_release=self._on_pick_pdf)
        picker_card.add_widget(pick_btn)

        body.add_widget(picker_card)

        # Info card
        info_card = CardBox(padding=dp(16), spacing=dp(8))
        info_card.add_widget(SectionTitle("ℹ️  How It Works"))
        steps = [
            "1. Select a text-based PDF from your device",
            "2. Tap Generate AudioBook (free with ads)",
            "3. Wait while we convert the text to speech",
            "4. Download or share your MP3 AudioBook",
        ]
        for step in steps:
            info_card.add_widget(Label(
                text=step,
                font_size=sp(12),
                color=(0.7, 0.7, 0.8, 1),
                size_hint_y=None,
                height=dp(22),
                halign="left",
                text_size=(None, None),
            ))
        body.add_widget(info_card)

        # Generate button
        self.gen_btn = RoundedButton(
            text="🎙  Generate AudioBook",
            size_hint_y=None,
            height=dp(58),
            bg_color=(0.1, 0.6, 0.35, 1),
            font_size=sp(16),
        )
        self.gen_btn.bind(on_release=self._on_generate)
        body.add_widget(self.gen_btn)

        body.add_widget(Label(size_hint_y=None, height=dp(8)))  # spacer

        scroll.add_widget(body)
        root.add_widget(scroll)

        # ── Banner Ad (always visible at bottom)
        self.banner_ad = BannerAdWidget()
        root.add_widget(self.banner_ad)

        self.add_widget(root)

    def on_enter(self):
        self.banner_ad.load()

    def _on_pick_pdf(self, *args):
        self.picker.pick_pdf(callback=self._on_pdf_selected)

    def _on_pdf_selected(self, path):
        if path and os.path.isfile(path):
            self.selected_pdf = path
            name = os.path.basename(path)
            pages = self.extractor.get_page_count(path)
            self.file_label.text = f"✅  {name}\n     {pages} pages"
            self.file_label.color = (0.4, 0.85, 0.55, 1)
        else:
            self.file_label.text = "❌  No file selected"
            self.file_label.color = (0.55, 0.55, 0.65, 1)

    def _on_generate(self, *args):
        if not self.selected_pdf:
            self.file_label.text = "⚠️  Please select a PDF first!"
            self.file_label.color = (1.0, 0.75, 0.2, 1)
            return

        # Show interstitial ad THEN navigate to generate screen
        app = App.get_running_app()
        app.admob.show_interstitial_ad(on_dismissed=self._go_to_generate)

    def _go_to_generate(self, *args):
        generate_screen = self.manager.get_screen("generate")
        generate_screen.set_pdf(self.selected_pdf)
        self.manager.transition = FadeTransition(duration=0.3)
        self.manager.current = "generate"


# ═══════════════════════════════════════════════════════════════════════════════
# GENERATE SCREEN — Progress, Player, Download
# ═══════════════════════════════════════════════════════════════════════════════
class GenerateScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.extractor = PDFExtractor()
        self.tts = TTSEngine()
        self.pdf_path = None
        self.output_path = None
        self._build_ui()

    def set_pdf(self, path: str):
        self.pdf_path = path
        self.pdf_name = os.path.basename(path)
        self.status_label.text = f"Ready: {self.pdf_name}"
        self.progress_bar.value = 0
        self.output_path = None
        self._set_stage("idle")

    def _build_ui(self):
        root = BoxLayout(orientation="vertical", spacing=0)

        with root.canvas.before:
            Color(0.08, 0.08, 0.12, 1)
            self._bg = Rectangle(size=root.size, pos=root.pos)
        root.bind(size=lambda *a: setattr(self._bg, "size", root.size))
        root.bind(pos=lambda *a: setattr(self._bg, "pos", root.pos))

        # ── Header
        header = BoxLayout(
            size_hint_y=None, height=dp(56),
            padding=[dp(8), dp(4)], spacing=dp(8),
        )
        with header.canvas.before:
            Color(0.12, 0.12, 0.18, 1)
            self._hbg = Rectangle(size=header.size, pos=header.pos)
        header.bind(size=lambda *a: setattr(self._hbg, "size", header.size))
        header.bind(pos=lambda *a: setattr(self._hbg, "pos", header.pos))

        back_btn = RoundedButton(
            text="← Back",
            size_hint=(None, None),
            size=(dp(80), dp(38)),
            bg_color=(0.25, 0.25, 0.35, 1),
            font_size=sp(12),
        )
        back_btn.bind(on_release=self._go_back)
        header.add_widget(back_btn)

        header.add_widget(Label(
            text="Generate AudioBook",
            font_size=sp(18),
            bold=True,
            color=(1, 1, 1, 1),
        ))
        root.add_widget(header)

        # ── Scrollable body
        scroll = ScrollView(do_scroll_x=False)
        body = BoxLayout(
            orientation="vertical",
            padding=dp(16),
            spacing=dp(14),
            size_hint_y=None,
        )
        body.bind(minimum_height=body.setter("height"))

        # Status card
        status_card = CardBox(padding=dp(18), spacing=dp(12))
        status_card.add_widget(SectionTitle("📊  Conversion Status"))

        self.status_label = StatusLabel("Select a PDF from the previous screen")
        status_card.add_widget(self.status_label)

        self.progress_bar = ProgressBar(
            max=100,
            value=0,
            size_hint_y=None,
            height=dp(18),
        )
        status_card.add_widget(self.progress_bar)

        self.progress_label = Label(
            text="0%",
            font_size=sp(12),
            color=(0.6, 0.6, 0.7, 1),
            size_hint_y=None,
            height=dp(20),
            halign="center",
        )
        status_card.add_widget(self.progress_label)
        body.add_widget(status_card)

        # Controls card
        controls_card = CardBox(padding=dp(16), spacing=dp(10))
        controls_card.add_widget(SectionTitle("🎛  Controls"))

        self.start_btn = RoundedButton(
            text="▶  Start Conversion",
            size_hint_y=None, height=dp(50),
            bg_color=(0.1, 0.6, 0.35, 1),
            font_size=sp(15),
        )
        self.start_btn.bind(on_release=self._on_start)
        controls_card.add_widget(self.start_btn)

        self.cancel_btn = RoundedButton(
            text="⏹  Cancel",
            size_hint_y=None, height=dp(44),
            bg_color=(0.7, 0.2, 0.2, 1),
            font_size=sp(14),
            disabled=True,
            opacity=0.4,
        )
        self.cancel_btn.bind(on_release=self._on_cancel)
        controls_card.add_widget(self.cancel_btn)
        body.add_widget(controls_card)

        # Download card (hidden until done)
        self.download_card = CardBox(padding=dp(16), spacing=dp(10))
        self.download_card.add_widget(SectionTitle("💾  Your AudioBook is Ready!"))

        self.file_size_label = Label(
            text="",
            font_size=sp(13),
            color=(0.7, 0.85, 0.7, 1),
            size_hint_y=None,
            height=dp(24),
            halign="center",
        )
        self.download_card.add_widget(self.file_size_label)

        self.download_btn = RoundedButton(
            text="⬇  Download / Save MP3",
            size_hint_y=None, height=dp(50),
            bg_color=(0.18, 0.42, 0.82, 1),
            font_size=sp(15),
        )
        self.download_btn.bind(on_release=self._on_download)
        self.download_card.add_widget(self.download_btn)

        self.share_btn = RoundedButton(
            text="📤  Share AudioBook",
            size_hint_y=None, height=dp(44),
            bg_color=(0.55, 0.25, 0.75, 1),
            font_size=sp(14),
        )
        self.share_btn.bind(on_release=self._on_share)
        self.download_card.add_widget(self.share_btn)

        self.download_card.opacity = 0
        body.add_widget(self.download_card)
        body.add_widget(Label(size_hint_y=None, height=dp(8)))

        scroll.add_widget(body)
        root.add_widget(scroll)

        # Banner Ad (always visible)
        self.banner_ad = BannerAdWidget()
        root.add_widget(self.banner_ad)

        self.add_widget(root)

    def on_enter(self):
        self.banner_ad.load()

    # ── Stage management ───────────────────────────────────────────────────────
    def _set_stage(self, stage: str):
        """idle | converting | done | error"""
        if stage == "idle":
            self.start_btn.disabled = False
            self.start_btn.opacity = 1
            self.cancel_btn.disabled = True
            self.cancel_btn.opacity = 0.4
            self.download_card.opacity = 0
        elif stage == "converting":
            self.start_btn.disabled = True
            self.start_btn.opacity = 0.4
            self.cancel_btn.disabled = False
            self.cancel_btn.opacity = 1
            self.download_card.opacity = 0
        elif stage == "done":
            self.start_btn.disabled = False
            self.start_btn.opacity = 1
            self.cancel_btn.disabled = True
            self.cancel_btn.opacity = 0.4
            self.download_card.opacity = 1
        elif stage == "error":
            self.start_btn.disabled = False
            self.start_btn.opacity = 1
            self.cancel_btn.disabled = True
            self.cancel_btn.opacity = 0.4

    # ── Handlers ───────────────────────────────────────────────────────────────
    def _on_start(self, *args):
        if not self.pdf_path:
            self.status_label.text = "⚠️  No PDF selected. Go back and choose one."
            self.status_label.color = (1, 0.75, 0.2, 1)
            return

        self._set_stage("converting")
        self.status_label.text = "📖  Extracting text from PDF..."
        self.status_label.color = (0.6, 0.85, 1.0, 1)
        self.progress_bar.value = 0

        import threading
        threading.Thread(target=self._run_conversion, daemon=True).start()

    def _run_conversion(self):
        try:
            # Step 1: Extract text
            from kivy.clock import Clock

            Clock.schedule_once(lambda dt: setattr(
                self.status_label, "text", "📖  Extracting text (step 1/2)..."
            ), 0)

            def extract_progress(pct, page, total):
                Clock.schedule_once(lambda dt: self._update_progress(
                    int(pct * 0.4), f"Extracting page {page}/{total}..."
                ), 0)

            text = self.extractor.extract_text(
                self.pdf_path, progress_callback=extract_progress
            )

            # Step 2: TTS
            Clock.schedule_once(lambda dt: setattr(
                self.status_label, "text", "🎙  Converting text to speech (step 2/2)..."
            ), 0)

            base = os.path.splitext(os.path.basename(self.pdf_path))[0]
            output_dir = self._get_output_dir()
            os.makedirs(output_dir, exist_ok=True)
            out_path = os.path.join(output_dir, f"{base}_audiobook.mp3")

            def tts_progress(pct):
                Clock.schedule_once(lambda dt: self._update_progress(
                    40 + int(pct * 0.6), f"Converting speech: {pct}%"
                ), 0)

            self.tts.convert(
                text=text,
                output_path=out_path,
                lang="en",
                progress_cb=tts_progress,
                done_cb=self._on_tts_done,
                error_cb=self._on_tts_error,
            )
        except Exception as e:
            from kivy.clock import Clock
            err_msg = str(e)
            Clock.schedule_once(lambda dt, m=err_msg: self._on_error(m), 0)

    def _get_output_dir(self) -> str:
        if platform == "android":
            from android.storage import primary_external_storage_path
            return os.path.join(
                primary_external_storage_path(), "Music", "PDFAudioBook"
            )
        else:
            return os.path.join(os.path.expanduser("~"), "Downloads", "PDFAudioBook")

    def _update_progress(self, pct: int, msg: str):
        self.progress_bar.value = pct
        self.progress_label.text = f"{pct}%"
        if msg:
            self.status_label.text = msg

    def _on_tts_done(self, path: str):
        self.output_path = path
        size_mb = os.path.getsize(path) / (1024 * 1024) if os.path.exists(path) else 0
        self.progress_bar.value = 100
        self.progress_label.text = "100%"
        self.status_label.text = "✅  AudioBook ready!"
        self.status_label.color = (0.3, 0.95, 0.5, 1)
        self.file_size_label.text = f"📁  {os.path.basename(path)}  ({size_mb:.1f} MB)"
        self._set_stage("done")

    def _on_tts_error(self, error):
        self._on_error(str(error))

    def _on_error(self, msg: str):
        self.status_label.text = f"❌  Error: {msg}"
        self.status_label.color = (1, 0.4, 0.4, 1)
        self._set_stage("error")

    def _on_cancel(self, *args):
        self.tts.cancel()
        self.status_label.text = "⏹  Conversion cancelled."
        self.status_label.color = (1, 0.75, 0.2, 1)
        self._set_stage("idle")

    def _on_download(self, *args):
        if not self.output_path or not os.path.exists(self.output_path):
            return
        # Show interstitial ad before download
        app = App.get_running_app()
        app.admob.show_interstitial_ad(on_dismissed=self._do_download)

    def _do_download(self, *args):
        if platform == "android":
            self._android_share(self.output_path)
        else:
            import subprocess, sys
            if sys.platform == "darwin":
                subprocess.Popen(["open", os.path.dirname(self.output_path)])
            elif sys.platform.startswith("linux"):
                subprocess.Popen(["xdg-open", os.path.dirname(self.output_path)])
            self.status_label.text = f"✅  Saved to: {self.output_path}"

    def _on_share(self, *args):
        if self.output_path and os.path.exists(self.output_path):
            self._android_share(self.output_path)

    def _android_share(self, path: str):
        if platform != "android":
            return
        try:
            from jnius import autoclass, cast
            PythonActivity = autoclass("org.kivy.android.PythonActivity")
            Intent         = autoclass("android.content.Intent")
            File           = autoclass("java.io.File")
            Uri            = autoclass("android.net.Uri")
            FileProvider   = autoclass("androidx.core.content.FileProvider")

            context = PythonActivity.mActivity
            file    = File(path)
            uri     = FileProvider.getUriForFile(
                context, context.getPackageName() + ".provider", file
            )
            intent = Intent(Intent.ACTION_SEND)
            intent.setType("audio/mpeg")
            intent.putExtra(Intent.EXTRA_STREAM, cast("android.os.Parcelable", uri))
            intent.addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION)
            context.startActivity(Intent.createChooser(intent, "Save / Share AudioBook"))
        except Exception as e:
            Logger.error(f"Share: {e}")

    def _go_back(self, *args):
        self.manager.transition = FadeTransition(duration=0.3)
        self.manager.current = "home"
