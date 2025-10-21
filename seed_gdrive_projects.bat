@echo off
REM Quick wrapper for seed_projects_from_gdrive management command
REM Usage: seed_gdrive_projects.bat [OPTIONS]

cd /d "%~dp0"
.\myenv\Scripts\python.exe manage.py seed_projects_from_gdrive %*

