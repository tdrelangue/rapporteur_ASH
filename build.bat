@echo off
REM Compilation de l'application APA_Email en .exe
pyinstaller -F -w -n "Rapporteur ASH" --icon "assets/icon.ico" --add-data "assets;assets" ASH_Email.py

REM Copie des fichiers de configuration modifiables
xcopy .env dist\ASH_Email\ /Y
xcopy templates dist\ASH_Email\templates\ /E /I /Y

echo.
echo === Build terminé ===
pause
