@echo off
REM Active l'environnement virtuel de FREYA
call "C:\Users\Apprenant\Desktop\Freya_personal_agent\.venv\Scripts\activate.bat"

REM Lance FREYA depuis n'importe quel répertoire
REM (FREYA peut accéder à tous les chemins, pas juste le dossier du projet)
python "C:\Users\Apprenant\Desktop\Freya_personal_agent\main.py"
pause