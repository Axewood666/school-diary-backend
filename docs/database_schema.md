# 🗄️ Схема базы данных школьного дневника

## 📊 ER-диаграмма

```mermaid
erDiagram
    %% ===== ПОЛЬЗОВАТЕЛИ И РОЛИ =====
    users {
        int id PK
        string email UK
        string username UK
        string hashed_password
        enum role "admin|teacher|student"
        string full_name
        boolean is_active
        datetime created_at
        datetime updated_at
    }
    
    students {
        int user_id PK,FK
        int class_id FK
        int admission_year
        string parent_phone
        string parent_email
        string parent_fio
    }
    
    teachers {
        int user_id PK,FK
        int class_id FK
        string degree
        int experience
        string bio
    }
    
    user_invites {
        int id PK
        string email
        string full_name
        string token
        datetime expires_at
        enum role "admin|teacher|student"
        datetime used_at
        datetime created_at
        boolean is_sent
    }

    %% ===== АКАДЕМИЧЕСКИЕ ЦИКЛЫ =====
    academic_years {
        int id PK
        string name
        datetime start_date
        datetime end_date
        boolean is_current
        datetime created_at
    }
    
    academic_periods {
        int id PK
        int year_id FK
        string name
        int order_num
        datetime start_date
        datetime end_date
        boolean is_current
        datetime created_at
    }
    
    academic_weeks {
        int id PK
        int period_id FK
        int week_num
        string name
        datetime start_date
        datetime end_date
        datetime created_at
        boolean is_holiday
    }

    %% ===== КЛАССЫ И ИСТОРИЯ =====
    classes {
        int id PK
        string name
        int grade_level
        string letter
        string specialization
        int year_id FK
        datetime created_at
    }
    
    student_class_history {
        int id PK
        int student_id FK
        int class_id FK
        datetime start_date
        datetime end_date
        enum reason "admission|transfer|return"
        boolean is_active
        datetime created_at
    }
    
    class_promotions {
        int id PK
        int from_class_id FK
        int to_class_id FK
        datetime promotion_date
        datetime created_at
    }

    %% ===== ПРЕДМЕТЫ И УЧИТЕЛЯ =====
    subjects {
        int id PK
        string name
        datetime created_at
        string back_ground_color
        string border_color
        string text_color
        string icon
    }
    
    teacher_subjects {
        int id PK
        int teacher_id FK
        int subject_id FK
        boolean is_main
        datetime created_at
    }

    %% ===== РАСПИСАНИЕ =====
    lesson_times {
        int id PK
        int period_id FK
        int lesson_num
        time start_time
        time end_time
        datetime created_at
    }
    
    schedule {
        int id PK
        int week_id FK
        int lesson_time_id FK
        int class_id FK
        int teacher_id FK
        int subject_id FK
        datetime created_at
        int day_of_week
        string location
        string description
        boolean is_replacement
        boolean is_cancelled
        int original_teacher_id FK
    }

    %% ===== ДОМАШНИЕ ЗАДАНИЯ И ОЦЕНКИ =====
    files {
        int id PK
        string filename
        string original_filename
        string bucket_name
        string object_name UK
        string content_type
        int size
        datetime created_at
        datetime updated_at
    }
    
    homework {
        int id PK
        int schedule_id FK
        int teacher_id FK
        int student_id FK
        int subject_id FK
        string description
        datetime assignment_at
        datetime due_date
        boolean is_done
        datetime created_at
        int file_id FK
    }
    
    grades {
        int id PK
        int schedule_id FK
        int student_id FK
        int subject_id FK
        int teacher_id FK
        int homework_id FK
        text comment
        int score
        datetime created_at
    }

    %% ===== СВЯЗИ МЕЖДУ ТАБЛИЦАМИ =====
    
    %% Пользователи
    users ||--o| students : "1:1"
    users ||--o| teachers : "1:1"
    
    %% Академические циклы
    academic_years ||--o{ academic_periods : "1:N"
    academic_periods ||--o{ academic_weeks : "1:N"
    academic_periods ||--o{ lesson_times : "1:N"
    
    %% Классы
    academic_years ||--o{ classes : "1:N"
    classes ||--o{ students : "1:N"
    classes ||--o| teachers : "1:1 (классный руководитель)"
    classes ||--o{ student_class_history : "1:N"
    classes ||--o{ class_promotions : "1:N (from_class)"
    classes ||--o{ class_promotions : "1:N (to_class)"
    
    %% Предметы
    teachers ||--o{ teacher_subjects : "1:N"
    subjects ||--o{ teacher_subjects : "1:N"
    
    %% Расписание
    academic_weeks ||--o{ schedule : "1:N"
    lesson_times ||--o{ schedule : "1:N"
    classes ||--o{ schedule : "1:N"
    teachers ||--o{ schedule : "1:N"
    teachers ||--o{ schedule : "1:N (original_teacher)"
    subjects ||--o{ schedule : "1:N"
    
    %% Домашние задания и оценки
    schedule ||--o{ homework : "1:N"
    teachers ||--o{ homework : "1:N"
    students ||--o{ homework : "1:N"
    subjects ||--o{ homework : "1:N"
    files ||--o{ homework : "1:N"
    
    schedule ||--o{ grades : "1:N"
    students ||--o{ grades : "1:N"
    subjects ||--o{ grades : "1:N"
    teachers ||--o{ grades : "1:N"
    homework ||--o{ grades : "1:N"
    
    %% История классов
    students ||--o{ student_class_history : "1:N"
```

## 📋 Описание основных сущностей

### 👥 **Пользователи и роли**
- **`users`** - Основная таблица пользователей (админы, учителя, студенты)
- **`students`** - Профили студентов с контактами родителей
- **`teachers`** - Профили учителей с квалификацией
- **`user_invites`** - Приглашения для регистрации

### 📅 **Академические циклы**
- **`academic_years`** - Учебные годы (2024-2025, 2025-2026)
- **`academic_periods`** - Четверти/семестры
- **`academic_weeks`** - Учебные недели
- **`lesson_times`** - Время уроков (1-й урок: 8:00-8:45)

### 🏫 **Классы и история**
- **`classes`** - Классы (10А, 11Б) с уровнем и специализацией
- **`student_class_history`** - История зачислений и переводов студентов
- **`class_promotions`** - История переводов классов на следующий год

### 📚 **Предметы и преподавание**
- **`subjects`** - Учебные предметы с настройками отображения
- **`teacher_subjects`** - Связь учителей с предметами

### 📅 **Расписание**
- **`schedule`** - Основное расписание уроков
- Поддержка замещений (`is_replacement`, `original_teacher_id`)
- Отмены уроков (`is_cancelled`)

### 📝 **Учебный процесс**
- **`homework`** - Домашние задания с прикрепленными файлами
- **`grades`** - Оценки с комментариями
- **`files`** - Файлы для домашних заданий

## 🔗 Ключевые особенности схемы

### ✅ **Преимущества:**
1. **Гибкость переводов** - полная история изменений классов
2. **Временная структура** - четкая иерархия академических периодов  
3. **Замещения** - поддержка замещающих учителей
4. **Файлы** - прикрепление материалов к заданиям
5. **Роли** - разграничение доступа по ролям

### 🎯 **Основные связи:**
- Один учитель может вести несколько предметов
- Один класс привязан к одному учебному году
- Студент может иметь историю в нескольких классах
- Домашние задания привязаны к конкретному уроку в расписании
- Оценки могут быть как за домашние задания, так и за работу на уроке 