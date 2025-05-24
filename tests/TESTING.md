# 🧪 Тестирование School Diary API

## Обзор

Данный набор тестов проверяет все действующие эндпоинты API в новом стандартизированном формате ответов `{result: true/false, response: {...}, message: "..."}`.

## 🚀 Быстрый старт

### 1. Подготовка среды

```bash
# Убедитесь что сервер запущен
uvicorn app.main:app --host 0.0.0.0 --port 8000

# Создайте тестовых пользователей
python create_test_admin.py

# Запустите все тесты
python run_tests.py
```

### 2. Альтернативные способы запуска

```bash
# Напрямую через pytest (если установлен)
pytest tests/test_integration.py -v

# Напрямую через Python
python tests/test_integration.py

# Установка зависимостей вручную
pip install -r tests/requirements.txt
```

## 📋 Структура тестов

### 🏥 Health Check Tests
- ✅ Корневой эндпоинт `/`

### 🔐 Auth Tests  
- ✅ `POST /auth/login` - логин с неверными данными
- ✅ `POST /auth/login` - логин без данных (валидация)
- ✅ `GET /auth/invite/{token}` - несуществующее приглашение
- ✅ `GET /auth/invite/list` - без авторизации (401)
- ✅ `GET /auth/invite/list` - с авторизацией админа

### 👥 User Tests
- ✅ `GET /users/me` - без авторизации (401)
- ✅ `GET /users/me` - с авторизацией
- ✅ `GET /users/` - без авторизации (401)
- ✅ `GET /users/` - список пользователей с пагинацией
- ✅ `GET /users/{id}` - несуществующий пользователь
- ✅ `GET /users/students` - список студентов
- ✅ `GET /users/teachers` - список учителей  
- ✅ `GET /users/admins` - список администраторов

### 📁 File Tests
- ✅ `GET /files/{id}` - без авторизации (401)
- ✅ `GET /files/{id}` - несуществующий файл
- ✅ `POST /files/` - недопустимый тип файла
- ✅ `POST /files/` - загрузка валидного файла
- ✅ `GET /files/{id}` - получение загруженного файла

## 🔑 Тестовые аккаунты

Скрипт `create_test_admin.py` создает следующих пользователей:

### Администратор
- **Username:** `test_admin`
- **Password:** `admin123`
- **Email:** `test_admin@example.com`
- **Role:** `admin`

### Студент
- **Username:** `test_student`
- **Password:** `student123`
- **Email:** `test_student@example.com`
- **Role:** `student`

### Учитель
- **Username:** `test_teacher`
- **Password:** `teacher123`
- **Email:** `test_teacher@example.com`
- **Role:** `teacher`

## 📊 Ожидаемые результаты

### ✅ Успешные тесты
- Корневой эндпоинт возвращает welcome message
- Неавторизованные запросы возвращают 401
- Неверные данные возвращают структурированные ошибки
- Авторизованные запросы возвращают данные в правильном формате
- Пагинация работает корректно
- Валидация файлов работает

### 🔍 Проверяемые форматы

**Успешный ответ:**
```json
{
  "result": true,
  "response": {
    "data": "...",
    "pagination": {"skip": 0, "limit": 10, "total": 100}
  },
  "message": "Success message"
}
```

**Ответ с ошибкой:**
```json
{
  "result": false,
  "message": "Error description", 
  "error_code": "ERROR_CODE"
}
```

## 🛠️ Настройка окружения

### Переменные окружения для тестов

```bash
# База данных (для create_test_admin.py)
export TEST_DATABASE_URL="postgresql://user:password@localhost:5432/school_diary"

# API URL (по умолчанию localhost:8000)
export API_BASE_URL="http://localhost:8000"
```

### Требования
- Python 3.8+
- Запущенный сервер School Diary API
- Доступная PostgreSQL база данных
- MinIO сервис (для файловых тестов)

## 🐛 Troubleshooting

### Ошибка подключения к серверу
```
❌ Сервер недоступен: ConnectError
```
**Решение:** Убедитесь что сервер запущен на `localhost:8000`

### Ошибка базы данных
```
❌ Ошибка при создании администратора: connection failed
```
**Решение:** Проверьте `DATABASE_URL` и доступность PostgreSQL

### Тесты пропускаются
```
⚠️  Не удалось получить токен администратора
```
**Решение:** Запустите `python create_test_admin.py` для создания тестовых пользователей

### Ошибки файловых тестов
```
❌ File upload failed
```
**Решение:** Убедитесь что MinIO сервис запущен и доступен

## 📈 Расширение тестов

Для добавления новых тестов:

1. Добавьте новый метод в соответствующий класс в `tests/test_integration.py`
2. Используйте `test_client.request()` для авторизованных запросов
3. Проверяйте формат ответа `{result, response, message}`
4. Добавьте вызов в функцию `run_all_tests()`

## 🎯 Цели тестирования

- ✅ Проверка нового формата ответов API
- ✅ Валидация авторизации и аутентификации
- ✅ Тестирование пагинации
- ✅ Проверка обработки ошибок
- ✅ Валидация структуры данных
- ✅ Интеграционное тестирование файлового API

## 📝 Отчетность

Тесты выводят детальную информацию о каждом шаге:
- ✅ Успешные операции
- ❌ Ошибки с описанием
- ⚠️ Предупреждения
- 📊 Статистика (количество записей, пагинация) 