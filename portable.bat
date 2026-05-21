@echo off
echo ==========================================
echo   Подготовка портабельной версии
echo   Latent Persona Memory
echo ==========================================
echo.

set PORTABLE_DIR=.\portable_version

REM 1. Очистка старой папки
if exist "%PORTABLE_DIR%" (
    echo Удаление старой portable-версии...
    rmdir /s /q "%PORTABLE_DIR%"
)

REM 2. Создание структуры папок
echo Создание структуры папок...
mkdir "%PORTABLE_DIR%"
mkdir "%PORTABLE_DIR%\data"

REM 3. Копирование файлов проекта
echo Копирование файлов проекта...
copy .env.example "%PORTABLE_DIR%\.env.example"
copy docker-compose.yml "%PORTABLE_DIR%\docker-compose.yml"

REM 4. Сохранение Docker-образа
echo Сохранение Docker-образа persona-project:latest...
echo Это может занять несколько минут...
docker save persona-project:latest -o "%PORTABLE_DIR%\persona_memory_image.tar"

if errorlevel 1 (
    echo [ОШИБКА] Не удалось сохранить Docker-образ.
    echo Убедитесь, что образ persona-project:latest существует.
    echo Проверьте: docker images persona-project:latest
    pause
    exit /b 1
)

REM 5. Создание setup.bat для получателя
echo Создание скрипта установки для получателя...
(
echo @echo off
echo echo ==========================================
echo echo   Установка Latent Persona Memory
echo echo ==========================================
echo echo.
echo echo [1/4] Проверка Docker...
echo docker info ^>nul 2^>^&1
echo if errorlevel 1 (
echo     echo [ОШИБКА] Docker не установлен или не запущен.
echo     echo Установите Docker Desktop с https://www.docker.com/products/docker-desktop/
echo     pause
echo     exit /b 1
echo )
echo echo Docker найден.
echo echo.
echo echo [2/4] Загрузка образа...
echo echo Это может занять несколько минут...
echo docker load -i persona_memory_image.tar
echo if errorlevel 1 (
echo     echo [ОШИБКА] Не удалось загрузить образ.
echo     pause
echo     exit /b 1
echo )
echo echo Образ загружен.
echo echo.
echo echo [3/4] Настройка окружения...
echo if not exist ".env" (
echo     copy .env.example .env
echo     echo Создан файл .env из шаблона.
echo     echo.
echo     echo [ВНИМАНИЕ] Сейчас откроется редактор .env файла.
echo     echo Вставьте свои ключи Yandex Cloud и сохраните файл.
echo     pause
echo     start notepad .env
echo     echo.
echo     echo После заполнения .env нажмите любую клавишу для продолжения...
echo     pause ^>nul
echo )
echo echo.
echo echo [4/4] Запуск приложения...
echo docker compose up -d
echo if errorlevel 1 (
echo     echo [ОШИБКА] Не удалось запустить приложение.
echo     pause
echo     exit /b 1
echo )
echo echo.
echo echo ==========================================
echo echo   Приложение запущено!
echo echo   Откройте в браузере: http://localhost:8501
echo echo.
echo echo   Для остановки выполните:
echo echo   docker compose down
echo echo ==========================================
echo pause
) > "%PORTABLE_DIR%\setup.bat"

REM 6. Копирование docker-compose для portable
(
echo services:
echo   persona:
echo     image: persona-project:latest
echo     pull_policy: never
echo     ports:
echo       - "8501:8501"
echo     env_file:
echo       - .env
echo     volumes:
echo       - ./data:/app/data
echo     restart: unless-stopped
) > "%PORTABLE_DIR%\docker-compose.yml"

echo.
echo ==========================================
echo   Портабельная версия готова!
echo   Папка: %PORTABLE_DIR%
echo.
echo   Размер: 
dir "%PORTABLE_DIR%\persona_memory_image.tar" | find "persona_memory_image.tar"
echo.
echo   Для переноса на другой компьютер:
echo   1. Скопируйте папку portable_version на флешку
echo   2. На целевом компьютере запустите setup.bat
echo.
echo   ВАЖНО: Не копируйте .env с вашими ключами!
echo   В portable_version лежит только .env.example
echo ==========================================
pause