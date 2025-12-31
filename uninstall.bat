@echo off
powershell -Command "iwr -Uri 'https://raw.githubusercontent.com/Nurali033004/server-manager/main/uninstall.ps1' -OutFile $env:TEMP\uninstall.ps1; & $env:TEMP\uninstall.ps1"
