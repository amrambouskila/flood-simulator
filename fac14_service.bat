@echo off
setlocal enabledelayedexpansion

REM ============================================================
REM              CONFIGURATION (EDIT THESE ONLY)
REM ============================================================
set "SERVICE_PREFIX=flood_simulator_dev"
set "COMPOSE_FILE=docker-compose.yml"
if "%PORT%"=="" set "PORT=8501"

set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%"

REM ============================================================
REM                  PARSE ARGUMENTS
REM ============================================================
:parse_args
if "%~1"=="" goto :done_args
if /I "%~1"=="--help" goto :show_help
if /I "%~1"=="-h" goto :show_help
shift
goto :parse_args

:show_help
echo Usage: %~nx0 [OPTIONS]
echo.
echo Options:
echo   -h, --help      Show this help
echo.
echo Environment:
echo   PORT              Server port (default: 8501)
exit /b 0

:done_args

REM ============================================================
REM               CHECK DOCKER
REM ============================================================
where docker >nul 2>&1
if errorlevel 1 (
    echo ERROR: Docker is not installed or not on PATH.
    echo   Install Docker Desktop: https://www.docker.com/products/docker-desktop/
    exit /b 1
)

docker info >nul 2>&1
if errorlevel 1 (
    echo ERROR: Docker daemon is not running. Please start Docker Desktop.
    exit /b 1
)

REM ============================================================
REM                     RUN DOCKER COMPOSE
REM ============================================================
echo ==^> Starting FAC14 - Flood-Adjusted Carbon-14 Simulator...
docker compose -f "%COMPOSE_FILE%" up --build -d

echo.
echo ==============================
echo FAC14 running at http://localhost:%PORT%
echo.
echo   k = stop (keep image)
echo   q = stop + remove image
echo   v = stop + remove image + volumes
echo   r = full restart (stop, remove, rebuild, relaunch)
echo ==============================

REM Auto-open browser
timeout /t 2 /nobreak >nul
start http://localhost:%PORT%

:wait_choice
set /p "CHOICE=Enter selection (k/q/v/r): "
if /I "%CHOICE%"=="k" goto stop_only
if /I "%CHOICE%"=="q" goto full_cleanup
if /I "%CHOICE%"=="v" goto full_cleanup_with_volumes
if /I "%CHOICE%"=="r" goto full_reset
echo Invalid selection. Enter k, q, v, or r.
goto wait_choice

REM ============================================================
REM            k = STOP BUT KEEP IMAGE
REM ============================================================
:stop_only
echo.
echo Stopping containers but keeping images...
docker compose -f "%COMPOSE_FILE%" down
goto end_script

REM ============================================================
REM            q = STOP + REMOVE IMAGES
REM ============================================================
:full_cleanup
echo.
echo Stopping and removing all containers...
docker compose -f "%COMPOSE_FILE%" down --remove-orphans
call :remove_images
goto end_script

REM ============================================================
REM            v = STOP + REMOVE IMAGES + VOLUMES
REM ============================================================
:full_cleanup_with_volumes
echo.
echo Stopping and removing all containers and volumes...
docker compose -f "%COMPOSE_FILE%" down --volumes --remove-orphans
call :remove_images
goto end_script

REM ============================================================
REM            r = FULL RESTART (keep volumes)
REM ============================================================
:full_reset
echo.
echo === FULL RESTART ===
echo Stopping containers...
docker compose -f "%COMPOSE_FILE%" down --remove-orphans
call :remove_images

echo ==^> Rebuilding Docker image...
docker compose -f "%COMPOSE_FILE%" up --build -d

echo.
echo ==============================
echo FAC14 restarted at http://localhost:%PORT%
echo.
echo   k = stop (keep image)
echo   q = stop + remove image
echo   v = stop + remove image + volumes
echo   r = full restart (stop, remove, rebuild, relaunch)
echo ==============================

timeout /t 2 /nobreak >nul
start http://localhost:%PORT%

REM Loop back to wait for next selection
goto wait_choice

REM ============================================================
REM                     SUBROUTINES
REM ============================================================

:remove_images
echo.
echo Searching for images starting with "%SERVICE_PREFIX%"...
set "TARGET_IMAGE="
for /f "delims=" %%I in ('
    docker images --format "{{.Repository}}:{{.Tag}}" ^| findstr /I "^%SERVICE_PREFIX%"
') do (
    set "TARGET_IMAGE=%%I"
    echo Found image: %%I
    echo Removing image %%I...
    docker rmi -f "%%I" 2>nul
)
if not defined TARGET_IMAGE (
    echo No images found matching prefix "%SERVICE_PREFIX%".
)
goto :eof

REM ============================================================
REM                            END
REM ============================================================
:end_script
exit /B
