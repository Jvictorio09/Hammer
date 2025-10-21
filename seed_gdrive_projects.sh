#!/bin/bash
# Quick wrapper for seed_projects_from_gdrive management command
# Usage: ./seed_gdrive_projects.sh [OPTIONS]

cd "$(dirname "$0")"
./myenv/Scripts/python.exe manage.py seed_projects_from_gdrive "$@"

