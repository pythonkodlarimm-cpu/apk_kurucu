[app]

title = APK Kurucu
package.name = apk_kurucu
package.domain = org.example

source.dir = .
source.include_exts = py,png,jpg,jpeg,kv,atlas,txt,md,json
source.include_patterns = assets/*,app/*

version = 0.7.0

requirements = python3,kivy,pyjnius,android

orientation = portrait
fullscreen = 0

icon.filename = assets/icons/app_icon.png

android.api = 33
android.minapi = 24
android.ndk = 25b
android.archs = arm64-v8a, armeabi-v7a

android.permissions = REQUEST_INSTALL_PACKAGES,READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE

android.add_compile_options = "-Wno-error=format-security"

presplash.filename =
log_level = 2
warn_on_root = 1
entrypoint = main.py


[buildozer]

log_level = 2
warn_on_root = 1
