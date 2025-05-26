# API Документация - Школьный дневник

## Обзор

Это API для системы школьного дневника, которое предоставляет функциональность для управления классами, предметами, расписанием, домашними заданиями и оценками.

## Аутентификация

Все endpoints требуют аутентификации через JWT токен, который должен быть передан в заголовке `Authorization: Bearer <token>`.

## Роли пользователей

- **ADMIN** - Полный доступ ко всем функциям
- **TEACHER** - Доступ к своим классам, предметам и расписанию
- **STUDENT** - Доступ к своему расписанию, домашним заданиям и оценкам

## Endpoints

### Аутентификация (`/auth`)

- `POST /auth/login` - Вход в систему
- `POST /auth/register` - Регистрация (только по приглашению)
- `POST /auth/refresh` - Обновление токена

### Пользователи (`/users`)

- `GET /users/` - Получить список пользователей (ADMIN)
- `GET /users/me` - Получить информацию о текущем пользователе
- `POST /users/invite` - Пригласить пользователя (ADMIN)

### Классы (`/class`)

- `GET /class/` - Получить список классов
- `POST /class/` - Создать класс (ADMIN)
- `POST /class/{class_id}/students` - Добавить/удалить студентов из класса (ADMIN)

### Предметы (`/subjects`)

- `GET /subjects/` - Получить список предметов
- `POST /subjects/` - Создать предмет (ADMIN)
- `GET /subjects/{subject_id}` - Получить предмет по ID
- `PATCH /subjects/{subject_id}` - Обновить предмет (ADMIN)
- `DELETE /subjects/{subject_id}` - Удалить предмет (ADMIN)
- `POST /subjects/{subject_id}/teachers` - Назначить учителя на предмет (ADMIN)
- `DELETE /subjects/{subject_id}/teachers/{teacher_id}` - Убрать учителя с предмета (ADMIN)
- `GET /subjects/teacher/{teacher_id}` - Получить предметы учителя

### Расписание (`/schedule`)

#### Время уроков
- `GET /schedule/lesson-times` - Получить время уроков
- `POST /schedule/lesson-times` - Создать время урока (ADMIN)

#### Расписание
- `GET /schedule/` - Получить расписание
  - Параметры: `week_id`, `class_id`, `teacher_id`, `start_week_id`, `end_week_id`
- `POST /schedule/` - Создать элемент расписания (ADMIN)
- `PATCH /schedule/{schedule_id}` - Обновить элемент расписания (ADMIN)
- `DELETE /schedule/{schedule_id}` - Удалить элемент расписания (ADMIN)

#### Домашние задания
- `GET /schedule/homework` - Получить домашние задания
  - Параметры: `student_id`, `teacher_id`, `class_id`, `subject_id`, `is_done`
- `POST /schedule/homework` - Создать домашнее задание (ADMIN, TEACHER)

#### Оценки
- `GET /schedule/grades` - Получить оценки
  - Параметры: `student_id`, `teacher_id`, `class_id`, `subject_id`
- `POST /schedule/grades` - Создать оценку (ADMIN, TEACHER)

### Академические циклы (`/academic-cycles`)

#### Учебные годы
- `GET /academic-cycles/years` - Получить список учебных годов
- `POST /academic-cycles/years` - Создать учебный год (ADMIN)
- `GET /academic-cycles/current-year` - Получить текущий учебный год

#### Учебные периоды
- `GET /academic-cycles/periods` - Получить список учебных периодов
- `GET /academic-cycles/current-period` - Получить текущий учебный период

#### Учебные недели
- `GET /academic-cycles/weeks` - Получить список учебных недель
- `GET /academic-cycles/current-week` - Получить текущую учебную неделю

### Файлы (`/files`)

- `POST /files/upload` - Загрузить файл
- `GET /files/{file_id}` - Скачать файл

## Модели данных

### Subject (Предмет)
```json
{
  "id": 1,
  "name": "Математика",
  "back_ground_color": "#FF5733",
  "border_color": "#C70039",
  "text_color": "#FFFFFF",
  "icon": "math",
  "created_at": "2024-01-01T00:00:00Z"
}
```

### Schedule (Расписание)
```json
{
  "id": 1,
  "week_id": 1,
  "lesson_time_id": 1,
  "class_id": 1,
  "class_name": "10А",
  "teacher_id": 1,
  "teacher_name": "Иванов Иван Иванович",
  "subject_id": 1,
  "subject_name": "Математика",
  "day_of_week": 1,
  "location": "Кабинет 101",
  "description": "Алгебра",
  "is_replacement": false,
  "is_cancelled": false,
  "original_teacher_id": null,
  "original_teacher_name": null,
  "lesson_num": 1,
  "start_time": "08:00:00",
  "end_time": "08:45:00",
  "created_at": "2024-01-01T00:00:00Z"
}
```

### Homework (Домашнее задание)
```json
{
  "id": 1,
  "schedule_id": 1,
  "teacher_id": 1,
  "teacher_name": "Иванов Иван Иванович",
  "student_id": 1,
  "student_name": "Петров Петр Петрович",
  "subject_id": 1,
  "subject_name": "Математика",
  "description": "Решить задачи 1-10 на странице 45",
  "assignment_at": "2024-01-01T10:00:00Z",
  "due_date": "2024-01-03T23:59:59Z",
  "is_done": false,
  "file_id": null,
  "created_at": "2024-01-01T10:00:00Z"
}
```

### Grade (Оценка)
```json
{
  "id": 1,
  "schedule_id": 1,
  "student_id": 1,
  "student_name": "Петров Петр Петрович",
  "subject_id": 1,
  "subject_name": "Математика",
  "teacher_id": 1,
  "teacher_name": "Иванов Иван Иванович",
  "homework_id": 1,
  "comment": "Отличная работа",
  "score": 5,
  "created_at": "2024-01-01T12:00:00Z"
}
```

## Коды ошибок

- `INSUFFICIENT_PERMISSIONS` - Недостаточно прав доступа
- `SUBJECT_NOT_FOUND` - Предмет не найден
- `TEACHER_NOT_FOUND` - Учитель не найден
- `STUDENT_NOT_FOUND` - Студент не найден
- `CLASS_NOT_FOUND` - Класс не найден
- `SCHEDULE_ITEM_NOT_FOUND` - Элемент расписания не найден
- `LESSON_TIME_NOT_FOUND` - Время урока не найдено
- `CURRENT_PERIOD_NOT_FOUND` - Текущий учебный период не найден
- `CURRENT_YEAR_NOT_FOUND` - Текущий учебный год не найден
- `CURRENT_WEEK_NOT_FOUND` - Текущая учебная неделя не найдена
- `TEACHER_ALREADY_ASSIGNED` - Учитель уже назначен на этот предмет
- `LESSON_TIME_ALREADY_EXISTS` - Время урока с таким номером уже существует
- `STUDENT_NOT_ASSIGNED_TO_CLASS` - Студент не привязан к классу
- `INVALID_PARAMETERS` - Неверные параметры запроса

## Примеры использования

### Получить расписание класса на неделю
```bash
GET /schedule/?week_id=1&class_id=1
```

### Получить домашние задания студента
```bash
GET /schedule/homework?student_id=1&is_done=false
```

### Создать оценку
```bash
POST /schedule/grades
{
  "schedule_id": 1,
  "student_id": 1,
  "subject_id": 1,
  "teacher_id": 1,
  "score": 5,
  "comment": "Отличная работа"
}
```

### Назначить учителя на предмет
```bash
POST /subjects/1/teachers?teacher_id=1&is_main=true
``` 