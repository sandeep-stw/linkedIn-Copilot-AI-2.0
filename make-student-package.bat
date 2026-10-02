@echo off
REM Double-click to build a clean Student Kit (+ plugin) into the dist folder.
REM Release a new version instead:  make-student-package.bat patch   (or minor / major)
setlocal
cd /d "%~dp0"
set ENGINE=%USERPROFILE%\.claude\skills\package-product\scripts\build_package.py
if not exist "%ENGINE%" (
  echo Build engine not found: %ENGINE%
  pause & exit /b 1
)
if not "%~1"=="" python "%ENGINE%" bump %1 --project . || (pause & exit /b 1)
python "%ENGINE%" check --project . > dist-check.log 2>&1
if errorlevel 1 (
  type dist-check.log
  echo.
  echo Pre-check found problems. Fix them ^(or ask Claude: /student-package^) and try again.
  pause & exit /b 1
)
del dist-check.log
python "%ENGINE%" build --project . > NUL
if errorlevel 1 (
  echo BUILD FAILED - see dist\build-report.json, or ask Claude: /student-package
  pause & exit /b 1
)
echo Clean package built. Opening the dist folder...
start "" "%~dp0dist"
endlocal
