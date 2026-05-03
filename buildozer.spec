[app]

# App metadata
title = PDF AudioBook
package.name = pdfaudiobook
package.domain = com.yourname
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,mp3,json

version = 1.0.0
requirements = python3,kivy==2.3.0,kivymd,pymupdf,pypdf,gtts,pyttsx3,pydub,requests,certifi,android

# Android settings
orientation = portrait
fullscreen = 0
android.api = 33
android.minapi = 24
android.ndk = 25c
android.sdk = 33
android.arch = arm64-v8a

# Permissions
android.permissions = INTERNET,READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE,ACCESS_NETWORK_STATE

# ── AdMob / Google Play Services ──────────────────────────────────────────────
# These gradle dependencies pull in the AdMob SDK automatically
android.gradle_dependencies = com.google.android.gms:play-services-ads:22.6.0

# AdMob App ID must be declared in AndroidManifest — set via meta-data below
# IMPORTANT: Replace with your REAL AdMob App ID before publishing!
android.meta_data = com.google.android.gms.ads.APPLICATION_ID=ca-app-pub-2897970554214470~6328839892

# FileProvider for sharing MP3 output
android.add_src =

# ── p4a (Python for Android) ─────────────────────────────────────────────────
p4a.branch = master

# Icon & presplash
# icon.filename = %(source.dir)s/assets/icon.png
# presplash.filename = %(source.dir)s/assets/splash.png

# ── Build ──────────────────────────────────────────────────────────────────────
[buildozer]
log_level = 2
warn_on_root = 1
