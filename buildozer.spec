[app]
title = Chekyar Aghsatban
package.name = chekyaraghstban
package.domain = ir.farhadnorouzi
source.dir = .
source.include_exts = py,kv,png,jpg,ttf,json,txt
version = 0.1.0
requirements = python3,kivy,arabic-reshaper,python-bidi
orientation = portrait
fullscreen = 0
android.api = 35
android.minapi = 23
android.archs = arm64-v8a, armeabi-v7a
android.allow_backup = True

# (bool) Indicate if you accept the Android SDK License
android.accept_sdk_license = True

[buildozer]
log_level = 2
warn_on_root = 1
