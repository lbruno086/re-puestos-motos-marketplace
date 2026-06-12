@echo off
title Re-Puestos MDP
echo.
echo  ================================================
echo    Re-Puestos MDP - Repuestos de Motos
echo  ================================================
echo.

set PYTHON=
if exist "%USERPROFILE%\anaconda3\python.exe"  set PYTHON=%USERPROFILE%\anaconda3\python.exe
if exist "%USERPROFILE%\miniconda3\python.exe" set PYTHON=%USERPROFILE%\miniconda3\python.exe
if "%PYTHON%"=="" (
    py      --version >nul 2>&1 && set PYTHON=py
    python  --version >nul 2>&1 && set PYTHON=python
)
if "%PYTHON%"=="" ( echo [ERROR] No se encontro Python. & pause & exit /b 1 )

echo  [OK] Python: %PYTHON%
echo.
echo  Instalando dependencias...
set PYTHONUTF8=1
"%PYTHON%" -m pip install tornado bcrypt jinja2 --quiet --disable-pip-version-check
echo  [OK] Dependencias listas
echo.
echo  ================================================
echo    http://localhost:8889
echo  ================================================
echo.
echo  Tienda 1: tienda1@repuestos.com.ar / Demo1234!
echo  Comprador: comprador@repuestos.com.ar / Demo1234!
echo.
echo  Ctrl+C para detener
echo.
timeout /t 2 /nobreak >nul
start "" http://localhost:8889
set PYTHONUTF8=1
"%PYTHON%" app.py
pause
