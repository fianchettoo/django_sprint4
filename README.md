# django_sprint4

Проект сайта-блога на Django с пользователями, публикациями и комментариями.

---

## Требования

- **Python 3.9.x**
- `pip`
- встроенный `venv`
- ОС: Windows / Linux / macOS

> Проект **не гарантирует** корректную работу на Python 3.10+ / 3.12 (из-за версии Pillow).

---

### 1. Клонирование репозитория

```bash
git clone git@github.com:fianchettoo/django_sprint4.git
cd <ваш_путь_к_проекту>
```

### 2. Создание виртуального окружения

Windows
```bash
python -m venv venv
```

Linux / macOS
```bash
python3 -m venv venv
```

### 3. Активация виртуального окружения

Windows
```bash
source venv\Scripts\activate
```

Linux / macOS
```bash
source venv/bin/activate
```

### 4. Обновление pip

```bash
python -m pip install --upgrade pip
```

### 5. Установка зависимостей

```bash
pip install -r requirements.txt
```

### 6. Инициализация базы данных

```bash
cd blogicum
python manage.py migrate
```

### 7. Запуск сервера

```bash
python manage.py runserver
```

