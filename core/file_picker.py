"""
File Picker Utility
On Android: uses native Intent to let user pick a PDF from storage.
On Desktop: uses Kivy filechooser as fallback for development.
"""

from kivy.utils import platform
from kivy.logger import Logger


class FilePicker:
    """
    Opens a native file picker for PDF selection.

    Usage:
        picker = FilePicker()
        picker.pick_pdf(callback=lambda path: print(path))
    """

    def __init__(self):
        self._callback = None

    def pick_pdf(self, callback):
        """
        Open file picker. On completion calls callback(path) or callback(None).
        """
        self._callback = callback

        if platform == "android":
            self._android_pick()
        else:
            self._desktop_pick()

    # ── Android Native Intent ────────────────────────────────────────────────
    def _android_pick(self):
        try:
            from jnius import autoclass, cast
            from android import activity

            Intent    = autoclass("android.content.Intent")
            PythonActivity = autoclass("org.kivy.android.PythonActivity")

            intent = Intent(Intent.ACTION_GET_CONTENT)
            intent.setType("application/pdf")
            intent.addCategory(Intent.CATEGORY_OPENABLE)
            intent.putExtra(Intent.EXTRA_LOCAL_ONLY, True)

            # Register result handler BEFORE starting activity
            activity.bind(on_activity_result=self._on_android_result)
            PythonActivity.mActivity.startActivityForResult(
                Intent.createChooser(intent, "Select PDF File"), 1001
            )
        except Exception as e:
            Logger.error(f"FilePicker Android: {e}")
            if self._callback:
                self._callback(None)

    def _on_android_result(self, requestCode, resultCode, intent):
        from android import activity
        activity.unbind(on_activity_result=self._on_android_result)

        RESULT_OK = -1  # Activity.RESULT_OK
        if requestCode == 1001 and resultCode == RESULT_OK and intent:
            try:
                real_path = self._resolve_uri(intent.getData())
                if self._callback:
                    self._callback(real_path)
                return
            except Exception as e:
                Logger.error(f"FilePicker resolve URI: {e}")

        if self._callback:
            self._callback(None)

    def _resolve_uri(self, uri) -> str:
        """Convert a content:// URI to a real filesystem path."""
        from jnius import autoclass, cast
        ContentResolver = autoclass("android.content.ContentResolver")
        PythonActivity  = autoclass("org.kivy.android.PythonActivity")
        context = PythonActivity.mActivity

        # Try MediaStore cursor first
        try:
            Cursor  = autoclass("android.database.Cursor")
            columns = ["_data"]
            cursor  = context.getContentResolver().query(uri, columns, None, None, None)
            if cursor and cursor.moveToFirst():
                col_index = cursor.getColumnIndexOrThrow("_data")
                path = cursor.getString(col_index)
                cursor.close()
                if path:
                    return path
        except Exception:
            pass

        # Fallback: copy to cache dir and return that path
        return self._copy_uri_to_cache(uri, context)

    def _copy_uri_to_cache(self, uri, context) -> str:
        """Copy a content:// stream to local cache and return path."""
        from jnius import autoclass
        import os

        cache_dir = context.getCacheDir().getAbsolutePath()
        dest_path = os.path.join(cache_dir, "selected_input.pdf")

        InputStream = context.getContentResolver().openInputStream(uri)
        with open(dest_path, "wb") as f:
            buffer = bytearray(8192)
            while True:
                n = InputStream.read(buffer)
                if n == -1:
                    break
                f.write(buffer[:n])
        InputStream.close()
        return dest_path

    # ── Desktop Fallback (Dev/Testing) ────────────────────────────────────────
    def _desktop_pick(self):
        from kivy.uix.popup import Popup
        from kivy.uix.boxlayout import BoxLayout
        from kivy.uix.filechooser import FileChooserListView
        from kivy.uix.button import Button
        from kivy.uix.label import Label

        layout = BoxLayout(orientation="vertical", spacing=5, padding=10)

        chooser = FileChooserListView(
            filters=["*.pdf", "*.PDF"],
            path=self._get_start_path(),
        )
        layout.add_widget(chooser)

        btn_row = BoxLayout(size_hint_y=None, height=44, spacing=8)
        cancel_btn = Button(text="Cancel", background_color=(0.6, 0.6, 0.6, 1))
        select_btn = Button(text="Select", background_color=(0.2, 0.6, 1, 1))
        btn_row.add_widget(cancel_btn)
        btn_row.add_widget(select_btn)
        layout.add_widget(btn_row)

        popup = Popup(
            title="Select a PDF File",
            content=layout,
            size_hint=(0.95, 0.9),
        )

        def on_select(inst):
            if chooser.selection:
                popup.dismiss()
                if self._callback:
                    self._callback(chooser.selection[0])

        def on_cancel(inst):
            popup.dismiss()
            if self._callback:
                self._callback(None)

        select_btn.bind(on_release=on_select)
        cancel_btn.bind(on_release=on_cancel)
        popup.open()

    def _get_start_path(self) -> str:
        import os
        for candidate in [
            os.path.expanduser("~/Downloads"),
            os.path.expanduser("~/Documents"),
            os.path.expanduser("~"),
        ]:
            if os.path.isdir(candidate):
                return candidate
        return "/"
