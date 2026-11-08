@echo off
chcp 65001 >nul
title Sistema WoWhead Midnight Scraper

echo ========================================
echo    SISTEMA WOWHEAD MIDNIGHT SCRAPER
echo ========================================
echo.

echo Iniciando sistema via menu interativo...
echo O terminal permanecera aberto durante a execucao.
echo.

python iniciar_sistema.py

echo.
echo ========================================
echo    SISTEMA ENCERRADO
echo ========================================
echo.
pause
