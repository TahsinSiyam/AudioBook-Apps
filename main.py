"""
PDF to AudioBook Android App
Built with Kivy + KivyMD + pyttsx3/gTTS + AdMob
"""

import os
import threading
from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.utils import platform
from kivy.logger import Logger

from ui.screens import ScreenManager, SplashScreen, HomeScreen, GenerateScreen
from ads.admob_manager import AdMobManager

# Android-only imports (guarded)
if platform == "android":
    from android.permissions import request_permissions, Permission
    from android import activity


class PDFAudioBookApp(App):
    """Main Application Class"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.admob = AdMobManager()
        self.title = "PDF AudioBook"

    def build(self):
        Window.clearcolor = (0.08, 0.08, 0.12, 1)

        # Request Android permissions
        if platform == "android":
            self._request_permissions()

        # Build screen manager
        sm = ScreenManager()
        sm.add_widget(SplashScreen(name="splash"))
        sm.add_widget(HomeScreen(name="home"))
        sm.add_widget(GenerateScreen(name="generate"))

        return sm

    def on_start(self):
        # Initialize AdMob and show interstitial (video) ad on app open
        self.admob.initialize()
        Clock.schedule_once(self._show_open_ad, 2.0)

    def _show_open_ad(self, dt):
        self.admob.show_interstitial_ad(on_dismissed=None)

    def _request_permissions(self):
        request_permissions([
            Permission.READ_EXTERNAL_STORAGE,
            Permission.WRITE_EXTERNAL_STORAGE,
            Permission.INTERNET,
            Permission.ACCESS_NETWORK_STATE,
        ])


if __name__ == "__main__":
    PDFAudioBookApp().run()
