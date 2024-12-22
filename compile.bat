@echo off
title Novodo - Compiler

set ICONS_DIR=src/icons/
set ICON_ICO=%ICONS_DIR%icon.ico

echo Converting icons to .ico format

magick %ICONS_DIR%16.png %ICONS_DIR%32.png %ICONS_DIR%48.png %ICONS_DIR%128.png %ICONS_DIR%256.png -colors 256 %ICON_ICO% >nul 2>&1

echo Converted icons to .ico format

if exist nov.exe del nov.exe >nul 2>&1

echo Compiling runner.py to nov.exe

pyinstaller --onefile --icon=%ICON_ICO% runner.py >nul 2>&1

move dist\runner.exe . >nul 2>&1

rename runner.exe nov.exe >nul 2>&1

rmdir /s /q build >nul 2>&1
rmdir /s /q dist >nul 2>&1
del runner.spec >nul 2>&1

echo Compilation complete. nov.exe is ready.

pause