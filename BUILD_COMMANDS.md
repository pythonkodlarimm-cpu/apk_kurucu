# BUILD COMMANDS

## Proje
APK Kurucu

## Yerelde calistirma
python main.py

## Test
pytest

## Buildozer ilk hazirlik
buildozer init

## Debug APK derleme
buildozer android debug

## Derlenen dosyalar
bin/

## Git islemleri
git init
git add .
git commit -m "ilk surum"

## GitHub'a gonderme
git branch -M main
git remote add origin REPO_URL
git push -u origin main

## GitHub Actions
- Repo'ya push yap
- Actions sekmesinden workflow calistir
- Artifact icinden APK indir
