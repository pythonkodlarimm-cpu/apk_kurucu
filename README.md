# APK Kurucu

Surum: 0.7.0

## Proje Ozeti

Bu proje Python + Kivy tabanli Android APK uretim altyapisi icin hazirlanmistir.

## Paket Bilgileri

- package.name: apk_kurucu
- package.domain: org.example

## Android Ayarlari

- android.api: 34
- android.minapi: 24

## Requirements

python3,kivy==2.3.0,pyjnius==1.6.1

## Yerelde Calistirma

python main.py

## APK Derleme

buildozer android debug

## GitHub Actions

Workflow dosyasi:
.github/workflows/android-build.yml

## Notlar

- Cikti genelde bin/ klasorune duser.
- Ilk build uzun surebilir.
- GitHub Actions workflow dosyasi ile bulutta build alinabilir.
