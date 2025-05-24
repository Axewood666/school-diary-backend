#!/usr/bin/env python3
"""
Скрипт для создания тестового администратора
"""

import asyncio
import asyncpg
import os
from passlib.context import CryptContext

# Настройки базы данных (измените по необходимости)
DATABASE_URL = os.getenv("TEST_DATABASE_URL", "postgresql://postgres:axewood@localhost:5432/diary_db")

# Настройка хеширования паролей
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def create_test_admin():
    """Создает тестового администратора в базе данных"""
    
    print("🔐 Создание тестового администратора...")
    
    try:
        # Подключаемся к базе данных
        conn = await asyncpg.connect(DATABASE_URL)
        print("✅ Подключение к базе данных установлено")
        
        # Хешируем пароль
        hashed_password = pwd_context.hash("admin123")
        
        # Проверяем, существует ли уже такой пользователь
        existing_user = await conn.fetchrow(
            "SELECT id FROM users WHERE username = $1 OR email = $2",
            "test_admin", "test_admin@example.com"
        )
        
        if existing_user:
            print("⚠️  Тестовый администратор уже существует")
            
            # Обновляем пароль
            await conn.execute(
                """
                UPDATE users 
                SET hashed_password = $1, is_active = true 
                WHERE username = $2 OR email = $3
                """,
                hashed_password, "test_admin", "test_admin@example.com"
            )
            print("✅ Пароль тестового администратора обновлен")
            
        else:
            # Создаем нового пользователя
            user_id = await conn.fetchval(
                """
                INSERT INTO users (email, username, hashed_password, role, full_name, is_active)
                VALUES ($1, $2, $3, $4, $5, $6)
                RETURNING id
                """,
                "test_admin@example.com",
                "test_admin", 
                hashed_password,
                "ADMIN",
                "Test Administrator",
                True
            )
            
            print(f"✅ Тестовый администратор создан с ID: {user_id}")
        
        await conn.close()
        
        print("\n📋 Данные для входа:")
        print("   Username: test_admin")
        print("   Password: admin123")
        print("   Email: test_admin@example.com")
        
    except Exception as e:
        print(f"❌ Ошибка при создании администратора: {e}")
        print("💡 Проверьте:")
        print("   - Правильность DATABASE_URL")
        print("   - Доступность базы данных")
        print("   - Выполнены ли миграции")

async def create_test_data():
    """Создает тестовые данные для полноценного тестирования"""
    
    print("\n📚 Создание дополнительных тестовых данных...")
    
    try:
        conn = await asyncpg.connect(DATABASE_URL)
        
        # Создаем тестового студента
        student_password = pwd_context.hash("student123")
        student_id = await conn.fetchval(
            """
            INSERT INTO users (email, username, hashed_password, role, full_name, is_active)
            VALUES ($1, $2, $3, $4, $5, $6)
            ON CONFLICT (username) DO UPDATE SET
                hashed_password = EXCLUDED.hashed_password,
                is_active = EXCLUDED.is_active
            RETURNING id
            """,
            "test_student@example.com",
            "test_student",
            student_password,
            "STUDENT",
            "Test Student",
            True
        )
        
        if student_id:
            # Добавляем запись в таблицу students
            await conn.execute(
                """
                INSERT INTO students (user_id, parent_phone, parent_email, parent_fio)
                VALUES ($1, $2, $3, $4)
                ON CONFLICT (user_id) DO UPDATE SET
                    parent_phone = EXCLUDED.parent_phone,
                    parent_email = EXCLUDED.parent_email,
                    parent_fio = EXCLUDED.parent_fio
                """,
                student_id,
                "+7123456789",
                "parent@example.com",
                "Родитель Тестовый"
            )
            print(f"✅ Тестовый студент создан с ID: {student_id}")
        
        # Создаем тестового учителя
        teacher_password = pwd_context.hash("teacher123")
        teacher_id = await conn.fetchval(
            """
            INSERT INTO users (email, username, hashed_password, role, full_name, is_active)
            VALUES ($1, $2, $3, $4, $5, $6)
            ON CONFLICT (username) DO UPDATE SET
                hashed_password = EXCLUDED.hashed_password,
                is_active = EXCLUDED.is_active
            RETURNING id
            """,
            "test_teacher@example.com",
            "test_teacher",
            teacher_password,
            "TEACHER",
            "Test Teacher",
            True
        )
        
        if teacher_id:
            # Добавляем запись в таблицу teachers
            await conn.execute(
                """
                INSERT INTO teachers (user_id, degree, experience, bio)
                VALUES ($1, $2, $3, $4)
                ON CONFLICT (user_id) DO UPDATE SET
                    degree = EXCLUDED.degree,
                    experience = EXCLUDED.experience,
                    bio = EXCLUDED.bio
                """,
                teacher_id,
                "Магистр",
                5,
                "Тестовый учитель для проверки API"
            )
            print(f"✅ Тестовый учитель создан с ID: {teacher_id}")
        
        await conn.close()
        
        print("\n📋 Дополнительные тестовые аккаунты:")
        print("   Student - Username: test_student, Password: student123")
        print("   Teacher - Username: test_teacher, Password: teacher123")
        
    except Exception as e:
        print(f"❌ Ошибка при создании тестовых данных: {e}")

async def main():
    """Главная функция"""
    print("🧪 Подготовка тестовой среды для School Diary API\n")
    
    await create_test_admin()
    await create_test_data()
    
    print("\n🎉 Тестовая среда готова!")
    print("📝 Теперь можно запускать тесты:")
    print("   python tests/test_integration.py")
    print("   или")
    print("   pytest tests/test_integration.py -v")

if __name__ == "__main__":
    asyncio.run(main()) 