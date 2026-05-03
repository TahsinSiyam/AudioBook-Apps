"""
Text-to-Speech Engine
Primary:  gTTS (Google TTS) — natural sounding, requires internet
Fallback: pyttsx3                — offline, robotic but works anywhere

On Android, gTTS saves to an MP3 file which is then played/exported.
"""

import os
import threading
from kivy.logger import Logger
from kivy.utils import platform


class TTSEngine:
    """
    Converts text to audio (MP3) file.

    Usage:
        engine = TTSEngine()
        engine.convert(text, output_path, lang="en",
                        progress_cb=lambda p: ...,
                        done_cb=lambda path: ...,
                        error_cb=lambda e: ...)
    """

    SUPPORTED_LANGUAGES = {
        "English":    "en",
        "Bengali":    "bn",
        "Hindi":      "hi",
        "Arabic":     "ar",
        "Spanish":    "es",
        "French":     "fr",
        "German":     "de",
        "Chinese":    "zh",
        "Japanese":   "ja",
        "Portuguese": "pt",
    }

    def __init__(self):
        self._gtts_available   = self._check_gtts()
        self._pyttsx_available = self._check_pyttsx3()
        self._cancel_flag = threading.Event()

    def _check_gtts(self):
        try:
            import gtts
            return True
        except ImportError:
            return False

    def _check_pyttsx3(self):
        try:
            import pyttsx3
            return True
        except ImportError:
            return False

    def convert(
        self,
        text: str,
        output_path: str,
        lang: str = "en",
        speed: float = 1.0,
        progress_cb=None,
        done_cb=None,
        error_cb=None,
    ):
        """
        Kick off TTS conversion in a background thread.
        Calls done_cb(output_path) on success, error_cb(Exception) on failure.
        """
        self._cancel_flag.clear()
        t = threading.Thread(
            target=self._convert_thread,
            args=(text, output_path, lang, speed, progress_cb, done_cb, error_cb),
            daemon=True,
        )
        t.start()

    def cancel(self):
        self._cancel_flag.set()

    # ── Internal ────────────────────────────────────────────────────────────────
    def _convert_thread(self, text, output_path, lang, speed, progress_cb, done_cb, error_cb):
        try:
            os.makedirs(os.path.dirname(output_path), exist_ok=True)

            if self._gtts_available:
                self._convert_gtts(text, output_path, lang, speed, progress_cb)
            elif self._pyttsx_available:
                self._convert_pyttsx3(text, output_path, progress_cb)
            else:
                raise ImportError(
                    "No TTS library found. Install gTTS:\n  pip install gTTS"
                )

            if done_cb:
                from kivy.clock import Clock
                Clock.schedule_once(lambda dt, p=output_path: done_cb(p), 0)

        except Exception as e:
            Logger.error(f"TTSEngine: {e}")
            if error_cb:
                from kivy.clock import Clock
                err = e
                Clock.schedule_once(lambda dt, err=err: error_cb(err), 0)

    def _convert_gtts(self, text, output_path, lang, speed, progress_cb):
        from gtts import gTTS

        # gTTS doesn't support native progress, so we chunk large texts
        CHUNK_SIZE = 4000   # characters per chunk
        chunks = self._split_text(text, CHUNK_SIZE)
        total  = len(chunks)

        if total == 1:
            if progress_cb:
                progress_cb(10)
            tts = gTTS(text=text, lang=lang, slow=(speed < 0.9))
            tts.save(output_path)
            if progress_cb:
                progress_cb(100)
        else:
            # Convert chunks to MP3s, merge with pydub
            import tempfile
            chunk_files = []
            for i, chunk in enumerate(chunks):
                if self._cancel_flag.is_set():
                    raise InterruptedError("Conversion cancelled by user")
                tmp = tempfile.mktemp(suffix=".mp3")
                tts = gTTS(text=chunk, lang=lang, slow=(speed < 0.9))
                tts.save(tmp)
                chunk_files.append(tmp)
                if progress_cb:
                    progress_cb(int(((i + 1) / total) * 90))

            # Merge all chunks
            self._merge_mp3s(chunk_files, output_path)
            # Clean up temp files
            for f in chunk_files:
                try:
                    os.remove(f)
                except:
                    pass
            if progress_cb:
                progress_cb(100)

    def _convert_pyttsx3(self, text, output_path, progress_cb):
        import pyttsx3
        engine = pyttsx3.init()
        engine.setProperty("rate", 150)
        engine.save_to_file(text, output_path)
        if progress_cb:
            progress_cb(50)
        engine.runAndWait()
        if progress_cb:
            progress_cb(100)

    def _merge_mp3s(self, files, output_path):
        """
        Merge MP3 files via raw binary concat.
        gTTS outputs standard MP3 frames so this works in all players
        without ffmpeg or pydub.
        """
        from kivy.logger import Logger
        Logger.info(f"TTSEngine: Merging {len(files)} chunks")
        with open(output_path, "wb") as out:
            for f in files:
                with open(f, "rb") as inp:
                    out.write(inp.read())
        Logger.info("TTSEngine: Merge complete")

    def _split_text(self, text: str, chunk_size: int) -> list:
        """Split text into chunks at sentence boundaries."""
        import re
        sentences = re.split(r"(?<=[.!?])\s+", text)
        chunks, current = [], ""
        for sentence in sentences:
            if len(current) + len(sentence) < chunk_size:
                current += " " + sentence
            else:
                if current:
                    chunks.append(current.strip())
                current = sentence
        if current:
            chunks.append(current.strip())
        return chunks or [text]

    @property
    def engine_name(self) -> str:
        if self._gtts_available:
            return "Google TTS (Online)"
        elif self._pyttsx_available:
            return "pyttsx3 (Offline)"
        return "No TTS Engine"

    @property
    def is_available(self) -> bool:
        return self._gtts_available or self._pyttsx_available
