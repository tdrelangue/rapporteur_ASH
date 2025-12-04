@echo off
REM Compilation de l'application APA_Email en .exe
python -m PyInstaller -F -w -n "Rapporteur ASH" --icon "assets/icon.ico" --add-data "assets;assets" ASH_Email.py

REM Copie des fichiers de configuration modifiables
xcopy templates dist\templates\ /E /I /Y

echo.
echo === Build terminé ===
pause
