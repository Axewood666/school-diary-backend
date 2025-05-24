#!/usr/bin/env python3
"""
Скрипт для запуска всех тестов School Diary API
"""

import asyncio
import subprocess
import sys
import os
import httpx

async def check_server():
    """Проверяет доступность сервера"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get("http://localhost:8000/", timeout=5.0)
            if response.status_code == 200:
                print("✅ Сервер доступен на localhost:8000")
                return True
    except Exception as e:
        print(f"❌ Сервер недоступен: {e}")
        return False

def install_test_dependencies():
    """Устанавливает зависимости для тестов"""
    print("📦 Установка зависимостей для тестов...")
    try:
        subprocess.run([
            sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
        ], check=True, capture_output=True)
        print("✅ Зависимости установлены")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Ошибка установки зависимостей: {e}")
        return False

def run_pytest():
    """Запускает pytest"""
    print("🧪 Запуск тестов через pytest...")
    try:
        result = subprocess.run([
            sys.executable, "-m", "pytest", "test_integration.py", "-v"
        ], check=False)
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Ошибка запуска pytest: {e}")
        return False

async def run_direct_tests():
    """Запускает тесты напрямую"""
    print("🧪 Запуск тестов напрямую...")
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        sys.path.insert(0, current_dir)
        
        from tests.test_integration import run_all_tests
        await run_all_tests()
        return True
    except Exception as e:
        print(f"❌ Ошибка при прямом запуске тестов: {e}")
        return False

async def main():
    """Главная функция"""
    print("🚀 School Diary API Test Runner")
    print("=" * 40)
    
    server_available = await check_server()
    if not server_available:
        print("\n💡 Убедитесь что сервер запущен:")
        print("   uvicorn app.main:app --host 0.0.0.0 --port 8000")
        print("   или")
        print("   python -m app.main")
        return
    
    deps_installed = install_test_dependencies()
    
    print("\n" + "=" * 40)
    
    if deps_installed:
        print("🔄 Пробуем запустить pytest...")
        pytest_success = run_pytest()
        
        if not pytest_success:
            print("\n🔄 Pytest не сработал, запускаем тесты напрямую...")
            await run_direct_tests()
    else:
        print("🔄 Запускаем тесты напрямую без pytest...")
        await run_direct_tests()
    
    print("\n🎉 Тестирование завершено!")
    print("\n💡 Дополнительные команды:")
    print("   python create_test_admin.py  # Создать тестовых пользователей")
    print("   python tests/test_integration.py  # Запустить тесты напрямую")
    print("   pytest tests/test_integration.py -v  # Запустить через pytest")

if __name__ == "__main__":
    asyncio.run(main()) 