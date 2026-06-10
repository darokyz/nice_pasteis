@echo off
cd /d %~dp0
call .venv\Scripts\activate
python backup.py
waitress-serve --port=8000 --threads=4 core.wsgi:application
pause