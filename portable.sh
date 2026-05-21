#!/bin/bash
echo "=========================================="
echo "  Подготовка портабельной версии"
echo "  Latent Persona Memory"
echo "=========================================="
echo ""

PORTABLE_DIR="./portable_version"

# 1. Очистка
if [ -d "$PORTABLE_DIR" ]; then
    echo "Удаление старой portable-версии..."
    rm -rf "$PORTABLE_DIR"
fi

# 2. Создание структуры
echo "Создание структуры папок..."
mkdir -p "$PORTABLE_DIR/data"

# 3. Копирование файлов
echo "Копирование файлов проекта..."
cp .env.example "$PORTABLE_DIR/"
cp docker-compose.yml "$PORTABLE_DIR/"

# 4. Сохранение образа
echo "Сохранение Docker-образа persona-project:latest..."
echo "Это может занять несколько минут..."
docker save persona-project:latest -o "$PORTABLE_DIR/persona_memory_image.tar"

if [ $? -ne 0 ]; then
    echo "[ОШИБКА] Не удалось сохранить Docker-образ."
    exit 1
fi

# 5. Создание setup.sh для получателя
cat > "$PORTABLE_DIR/setup.sh" << 'SETUPEOF'
#!/bin/bash
echo "=========================================="
echo "  Установка Latent Persona Memory"
echo "=========================================="
echo ""

echo "[1/4] Проверка Docker..."
if ! docker info > /dev/null 2>&1; then
    echo "[ОШИБКА] Docker не установлен или не запущен."
    exit 1
fi
echo "Docker найден."
echo ""

echo "[2/4] Загрузка образа..."
echo "Это может занять несколько минут..."
docker load -i persona_memory_image.tar
if [ $? -ne 0 ]; then
    echo "[ОШИБКА] Не удалось загрузить образ."
    exit 1
fi
echo "Образ загружен."
echo ""

echo "[3/4] Настройка окружения..."
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "Создан файл .env из шаблона."
    echo "[ВНИМАНИЕ] Отредактируйте .env и вставьте свои ключи Yandex Cloud."
    echo "Затем перезапустите этот скрипт."
    exit 0
fi
echo ""

echo "[4/4] Запуск приложения..."
docker compose up -d
if [ $? -ne 0 ]; then
    echo "[ОШИБКА] Не удалось запустить приложение."
    exit 1
fi

echo ""
echo "=========================================="
echo "  Приложение запущено!"
echo "  Откройте в браузере: http://localhost:8501"
echo "  Для остановки: docker compose down"
echo "=========================================="
SETUPEOF

chmod +x "$PORTABLE_DIR/setup.sh"

# 6. Обновление docker-compose.yml для portable
cat > "$PORTABLE_DIR/docker-compose.yml" << 'COMPOSEEOF'
services:
  persona:
    image: persona-project:latest
    pull_policy: never
    ports:
      - "8501:8501"
    env_file:
      - .env
    volumes:
      - ./data:/app/data
    restart: unless-stopped
COMPOSEEOF

echo ""
echo "=========================================="
echo "  Портабельная версия готова!"
echo "  Папка: $PORTABLE_DIR"
echo ""
echo "  Размер архива:"
ls -lh "$PORTABLE_DIR/persona_memory_image.tar"
echo ""
echo "  Для переноса на другой компьютер:"
echo "  1. Скопируйте папку portable_version"
echo "  2. На целевом компьютере запустите setup.sh"
echo "=========================================="

