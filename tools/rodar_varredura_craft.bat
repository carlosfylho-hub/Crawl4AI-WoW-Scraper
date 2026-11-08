@echo off
REM Varredura de volume dos itens craftados R5 (P-10/P-13), com log em arquivo.
REM Uso: start /b tools\rodar_varredura_craft.bat
setlocal
set PYTHONIOENCODING=utf-8
cd /d "%~dp0.."

set LOG=data\_diagnostico\varredura_craft.log
echo === INICIO %DATE% %TIME% === > "%LOG%"
python scraper_season2.py --max-itens 120 --max-detalhes 100 --qualidade-craft 5 --exigir-craft >> "%LOG%" 2>&1
echo === FIM %DATE% %TIME% EXIT %ERRORLEVEL% === >> "%LOG%"
endlocal
