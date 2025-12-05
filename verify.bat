@echo off
echo Checking required files...
echo.

set files=docker-compose.yml Dockerfile nginx.conf init.sql prometheus.yml src\utils\logger.py src\utils\metrics.py src\utils\__init__.py .env

for %%f in (%files%) do (
    if exist "%%f" (
        echo [OK] %%f
    ) else (
        echo [MISSING] %%f
    )
)

echo.
echo Done!
pause