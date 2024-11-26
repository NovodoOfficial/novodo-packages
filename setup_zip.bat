@echo off

del /f /q setup.zip

powershell Compress-Archive -Path setup\* -DestinationPath setup.zip
