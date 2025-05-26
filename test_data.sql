-- Очистка таблиц
TRUNCATE TABLE grades CASCADE;
TRUNCATE TABLE homework CASCADE;
TRUNCATE TABLE schedule CASCADE;
TRUNCATE TABLE teacher_subjects CASCADE;
TRUNCATE TABLE lesson_times CASCADE;
TRUNCATE TABLE files CASCADE;
TRUNCATE TABLE students CASCADE;
TRUNCATE TABLE teachers CASCADE;
TRUNCATE TABLE classes CASCADE;
TRUNCATE TABLE subjects CASCADE;
TRUNCATE TABLE users CASCADE;
TRUNCATE TABLE user_invites CASCADE;
TRUNCATE TABLE academic_weeks CASCADE;
TRUNCATE TABLE academic_periods CASCADE;
TRUNCATE TABLE academic_years CASCADE;

-- Учебные годы
INSERT INTO academic_years (id, name, start_date, end_date, is_current, created_at) VALUES
(1, '2024-2025', '2024-09-01', '2025-06-30', true, NOW()),
(2, '2023-2024', '2023-09-01', '2024-06-30', false, NOW());

-- Учебные периоды
INSERT INTO academic_periods (id, year_id, name, order_num, start_date, end_date, is_current, created_at) VALUES
(1, 1, '1 четверть', 1, '2024-09-01', '2024-10-31', true, NOW()),
(2, 1, '2 четверть', 2, '2024-11-01', '2024-12-31', false, NOW()),
(3, 1, '3 четверть', 3, '2025-01-09', '2025-03-31', false, NOW()),
(4, 1, '4 четверть', 4, '2025-04-01', '2025-06-30', false, NOW());

-- Учебные недели
INSERT INTO academic_weeks (id, period_id, week_num, name, start_date, end_date, created_at, is_holiday) VALUES
(1, 1, 1, 'Неделя 1', '2024-09-01', '2024-09-07', NOW(), false),
(2, 1, 2, 'Неделя 2', '2024-09-08', '2024-09-14', NOW(), false),
(3, 1, 3, 'Неделя 3', '2024-09-15', '2024-09-21', NOW(), false),
(4, 1, 4, 'Неделя 4', '2024-09-22', '2024-09-28', NOW(), false),
(5, 1, 5, 'Неделя 5', '2024-09-29', '2024-10-05', NOW(), false),
(6, 1, 6, 'Неделя 6', '2024-10-06', '2024-10-12', NOW(), false),
(7, 1, 7, 'Неделя 7', '2024-10-13', '2024-10-19', NOW(), false),
(8, 1, 8, 'Неделя 8', '2024-10-20', '2024-10-26', NOW(), false);

-- Время уроков
INSERT INTO lesson_times (id, period_id, lesson_num, start_time, end_time, created_at) VALUES
(1, 1, 1, '08:00', '08:45', NOW()),
(2, 1, 2, '08:55', '09:40', NOW()),
(3, 1, 3, '09:50', '10:35', NOW()),
(4, 1, 4, '10:55', '11:40', NOW()),
(5, 1, 5, '11:50', '12:35', NOW()),
(6, 1, 6, '12:45', '13:30', NOW()),
(7, 1, 7, '13:40', '14:25', NOW());

-- Предметы
INSERT INTO subjects (id, name, created_at) VALUES
(1, 'Математика', NOW()),
(2, 'Русский язык', NOW()),
(3, 'Литература', NOW()),
(4, 'История', NOW()),
(5, 'География', NOW()),
(6, 'Биология', NOW()),
(7, 'Физика', NOW()),
(8, 'Химия', NOW()),
(9, 'Английский язык', NOW()),
(10, 'Физическая культура', NOW()),
(11, 'Информатика', NOW()),
(12, 'ОБЖ', NOW());

-- Пользователи
INSERT INTO users (id, email, username, hashed_password, role, full_name, is_active, created_at, updated_at) VALUES
(1, 'admin@school.ru', 'admin', '$2b$12$FiEKBoCh/8BBWMrqyR8BA.WMPcUUK776wlrCLsHzRur5wz9IM9ZoS', 'ADMIN', 'Администратор Системы', true, NOW(), NOW()),
(2, 'ivanov@school.ru', 'ivanov_teacher', '$2b$12$FiEKBoCh/8BBWMrqyR8BA.WMPcUUK776wlrCLsHzRur5wz9IM9ZoS', 'TEACHER', 'Иванов Иван Иванович', true, NOW(), NOW()),
(3, 'petrov@school.ru', 'petrov_teacher', '$2b$12$FiEKBoCh/8BBWMrqyR8BA.WMPcUUK776wlrCLsHzRur5wz9IM9ZoS', 'TEACHER', 'Петров Петр Петрович', true, NOW(), NOW()),
(4, 'sidorova@school.ru', 'sidorova_teacher', '$2b$12$FiEKBoCh/8BBWMrqyR8BA.WMPcUUK776wlrCLsHzRur5wz9IM9ZoS', 'TEACHER', 'Сидорова Мария Александровна', true, NOW(), NOW()),
(5, 'kozlov@school.ru', 'kozlov_teacher', '$2b$12$FiEKBoCh/8BBWMrqyR8BA.WMPcUUK776wlrCLsHzRur5wz9IM9ZoS', 'TEACHER', 'Козлов Алексей Викторович', true, NOW(), NOW()),
(6, 'student1@school.ru', 'student1', '$2b$12$FiEKBoCh/8BBWMrqyR8BA.WMPcUUK776wlrCLsHzRur5wz9IM9ZoS', 'STUDENT', 'Смирнов Алексей Дмитриевич', true, NOW(), NOW()),
(7, 'student2@school.ru', 'student2', '$2b$12$FiEKBoCh/8BBWMrqyR8BA.WMPcUUK776wlrCLsHzRur5wz9IM9ZoS', 'STUDENT', 'Козлова Анна Сергеевна', true, NOW(), NOW()),
(8, 'student3@school.ru', 'student3', '$2b$12$FiEKBoCh/8BBWMrqyR8BA.WMPcUUK776wlrCLsHzRur5wz9IM9ZoS', 'STUDENT', 'Волков Дмитрий Андреевич', true, NOW(), NOW()),
(9, 'student4@school.ru', 'student4', '$2b$12$FiEKBoCh/8BBWMrqyR8BA.WMPcUUK776wlrCLsHzRur5wz9IM9ZoS', 'STUDENT', 'Морозова Елена Игоревна', true, NOW(), NOW()),
(10, 'student5@school.ru', 'student5', '$2b$12$FiEKBoCh/8BBWMrqyR8BA.WMPcUUK776wlrCLsHzRur5wz9IM9ZoS', 'STUDENT', 'Новиков Сергей Владимирович', true, NOW(), NOW()),
(11, 'student6@school.ru', 'student6', '$2b$12$FiEKBoCh/8BBWMrqyR8BA.WMPcUUK776wlrCLsHzRur5wz9IM9ZoS', 'STUDENT', 'Федорова Ольга Петровна', true, NOW(), NOW());

-- Классы
INSERT INTO classes (id, name, grade_level, letter, specialization, year_id, created_at) VALUES
(1, '10А', 10, 'А', 'Математический профиль', 1, NOW()),
(2, '10Б', 10, 'Б', 'Гуманитарный профиль', 1, NOW()),
(3, '11А', 11, 'А', 'Физико-математический профиль', 1, NOW());

-- Учителя
INSERT INTO teachers (user_id, class_id, degree, experience, bio) VALUES
(2, 1, 'Кандидат педагогических наук', 15, 'Учитель математики высшей категории'),
(3, 2, 'Магистр филологии', 8, 'Учитель русского языка и литературы'),
(4, NULL, 'Магистр истории', 12, 'Учитель истории и обществознания'),
(5, 3, 'Кандидат физико-математических наук', 20, 'Учитель физики и информатики');

-- Ученики
INSERT INTO students (user_id, class_id, parent_phone, parent_email, parent_fio) VALUES
(6, 1, '+7(999)123-45-67', 'parent1@mail.ru', 'Смирнов Дмитрий Владимирович'),
(7, 1, '+7(999)234-56-78', 'parent2@mail.ru', 'Козлова Елена Михайловна'),
(8, 2, '+7(999)345-67-89', 'parent3@mail.ru', 'Волков Андрей Петрович'),
(9, 2, '+7(999)456-78-90', 'parent4@mail.ru', 'Морозова Татьяна Сергеевна'),
(10, 3, '+7(999)567-89-01', 'parent5@mail.ru', 'Новиков Владимир Алексеевич'),
(11, 3, '+7(999)678-90-12', 'parent6@mail.ru', 'Федоров Петр Иванович');

-- Связи учитель-предмет
INSERT INTO teacher_subjects (id, teacher_id, subject_id, is_main, created_at) VALUES
(1, 2, 1, true, NOW()),
(2, 2, 7, false, NOW()),
(3, 3, 2, true, NOW()),
(4, 3, 3, true, NOW()),
(5, 4, 4, true, NOW()),
(6, 4, 5, false, NOW()),
(7, 5, 7, true, NOW()),
(8, 5, 11, true, NOW());

-- Файлы
INSERT INTO files (id, filename, original_filename, bucket_name, object_name, content_type, size, created_at) VALUES
(1, 'homework_math.pdf', 'Задание по математике.pdf', 'homework-files', 'files/2024/homework_math_001.pdf', 'application/pdf', 256000, NOW()),
(2, 'homework_russian.docx', 'Сочинение.docx', 'homework-files', 'files/2024/homework_russian_001.docx', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 128000, NOW()),
(3, 'homework_physics.pdf', 'Лабораторная работа.pdf', 'homework-files', 'files/2024/homework_physics_001.pdf', 'application/pdf', 512000, NOW());

-- Расписание
INSERT INTO schedule (id, week_id, lesson_time_id, class_id, teacher_id, subject_id, created_at, day_of_week, location, description, is_replacement, is_cancelled, original_teacher_id) VALUES
-- Понедельник 10А
(1, 1, 1, 1, 2, 1, NOW(), 1, 'Кабинет 101', 'Алгебра', false, false, NULL),
(2, 1, 2, 1, 3, 2, NOW(), 1, 'Кабинет 201', 'Русский язык', false, false, NULL),
(3, 1, 3, 1, 4, 4, NOW(), 1, 'Кабинет 301', 'История России', false, false, NULL),
(4, 1, 4, 1, 5, 7, NOW(), 1, 'Кабинет 401', 'Физика', false, false, NULL),
-- Вторник 10А
(5, 1, 1, 1, 3, 3, NOW(), 2, 'Кабинет 201', 'Литература', false, false, NULL),
(6, 1, 2, 1, 2, 1, NOW(), 2, 'Кабинет 101', 'Геометрия', false, false, NULL),
(7, 1, 3, 1, 5, 11, NOW(), 2, 'Кабинет 501', 'Информатика', false, false, NULL),
-- Понедельник 10Б
(8, 1, 1, 2, 3, 2, NOW(), 1, 'Кабинет 202', 'Русский язык', false, false, NULL),
(9, 1, 2, 2, 2, 1, NOW(), 1, 'Кабинет 102', 'Алгебра', false, false, NULL),
(10, 1, 3, 2, 4, 4, NOW(), 1, 'Кабинет 302', 'История России', false, false, NULL),
-- Вторник 10Б
(11, 1, 1, 2, 2, 1, NOW(), 2, 'Кабинет 102', 'Геометрия', false, false, NULL),
(12, 1, 2, 2, 5, 7, NOW(), 2, 'Кабинет 402', 'Физика', false, false, NULL),
-- Понедельник 11А
(13, 1, 1, 3, 2, 1, NOW(), 1, 'Кабинет 103', 'Алгебра', false, false, NULL),
(14, 1, 2, 3, 3, 2, NOW(), 1, 'Кабинет 203', 'Русский язык', false, false, NULL),
(15, 1, 3, 3, 5, 7, NOW(), 1, 'Кабинет 403', 'Физика', false, false, NULL),
-- Замещение урока
(16, 1, 4, 1, 4, 4, NOW(), 1, 'Кабинет 301', 'История (замещение)', true, false, 3);

-- Домашние задания
INSERT INTO homework (id, schedule_id, teacher_id, student_id, subject_id, description, assignment_at, due_date, is_done, created_at, file_id) VALUES
(1, 1, 2, 6, 1, 'Решить задачи №15-20 из учебника', NOW(), NOW() + INTERVAL '2 days', false, NOW(), 1),
(2, 1, 2, 7, 1, 'Решить задачи №15-20 из учебника', NOW(), NOW() + INTERVAL '2 days', true, NOW(), 1),
(3, 2, 3, 6, 2, 'Написать сочинение на тему "Осень"', NOW(), NOW() + INTERVAL '3 days', true, NOW(), 2),
(4, 2, 3, 7, 2, 'Написать сочинение на тему "Осень"', NOW(), NOW() + INTERVAL '3 days', false, NOW(), 2),
(5, 4, 5, 6, 7, 'Выполнить лабораторную работу №1', NOW(), NOW() + INTERVAL '1 week', false, NOW(), 3),
(6, 4, 5, 7, 7, 'Выполнить лабораторную работу №1', NOW(), NOW() + INTERVAL '1 week', false, NOW(), 3),
(7, 8, 3, 8, 2, 'Выучить стихотворение Пушкина', NOW(), NOW() + INTERVAL '2 days', true, NOW(), NULL),
(8, 9, 2, 8, 1, 'Решить уравнения №25-30', NOW(), NOW() + INTERVAL '1 day', false, NOW(), NULL),
(9, 9, 2, 9, 1, 'Решить уравнения №25-30', NOW(), NOW() + INTERVAL '1 day', true, NOW(), NULL);

-- Оценки
INSERT INTO grades (id, schedule_id, student_id, subject_id, teacher_id, homework_id, comment, score, created_at) VALUES
(1, 1, 6, 1, 2, 1, 'Хорошо решены все задачи', 4, NOW()),
(2, 1, 7, 1, 2, 2, 'Отличная работа', 5, NOW()),
(3, 2, 6, 2, 3, 3, 'Отличное сочинение, грамотно написано', 5, NOW()),
(4, 2, 7, 2, 3, 4, 'Есть ошибки в орфографии', 3, NOW()),
(5, 3, 6, 4, 4, NULL, 'Контрольная работа по истории', 4, NOW()),
(6, 3, 7, 4, 4, NULL, 'Контрольная работа по истории', 3, NOW()),
(7, 4, 6, 7, 5, 5, 'Лабораторная работа выполнена частично', 3, NOW()),
(8, 8, 8, 2, 3, 7, 'Стихотворение выучено хорошо', 4, NOW()),
(9, 9, 8, 1, 2, 8, 'Не все уравнения решены', 3, NOW()),
(10, 9, 9, 1, 2, 9, 'Все уравнения решены правильно', 5, NOW()),
(11, 13, 10, 1, 2, NULL, 'Самостоятельная работа', 4, NOW()),
(12, 14, 10, 2, 3, NULL, 'Диктант', 5, NOW()),
(13, 15, 11, 7, 5, NULL, 'Устный ответ', 4, NOW());

-- Приглашения пользователей
INSERT INTO user_invites (id, email, full_name, token, expires_at, role, used_at, created_at, is_sent) VALUES
(1, 'newteacher@school.ru', 'Новиков Сергей Владимирович', 'invite_token_123', NOW() + INTERVAL '7 days', 'TEACHER', NULL, NOW(), true),
(2, 'newstudent@school.ru', 'Морозова Анастасия Игоревна', 'invite_token_456', NOW() + INTERVAL '7 days', 'STUDENT', NULL, NOW(), false),
(3, 'usedteacher@school.ru', 'Использованный Учитель Тестович', 'invite_token_789', NOW() + INTERVAL '7 days', 'TEACHER', NOW(), NOW(), true);

-- Обновление последовательностей
SELECT setval('academic_years_id_seq', (SELECT MAX(id) FROM academic_years));
SELECT setval('academic_periods_id_seq', (SELECT MAX(id) FROM academic_periods));
SELECT setval('academic_weeks_id_seq', (SELECT MAX(id) FROM academic_weeks));
SELECT setval('lesson_times_id_seq', (SELECT MAX(id) FROM lesson_times));
SELECT setval('subjects_id_seq', (SELECT MAX(id) FROM subjects));
SELECT setval('users_id_seq', (SELECT MAX(id) FROM users));
SELECT setval('classes_id_seq', (SELECT MAX(id) FROM classes));
SELECT setval('teacher_subjects_id_seq', (SELECT MAX(id) FROM teacher_subjects));
SELECT setval('files_id_seq', (SELECT MAX(id) FROM files));
SELECT setval('schedule_id_seq', (SELECT MAX(id) FROM schedule));
SELECT setval('homework_id_seq', (SELECT MAX(id) FROM homework));
SELECT setval('grades_id_seq', (SELECT MAX(id) FROM grades));
SELECT setval('user_invites_id_seq', (SELECT MAX(id) FROM user_invites)); 