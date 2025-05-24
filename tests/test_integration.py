import pytest
import asyncio
import httpx
import traceback
import sys
from typing import Dict, Optional
import io
from datetime import datetime

# Конфигурация тестов
BASE_URL = "http://localhost:8000"
API_V1 = f"{BASE_URL}/api/v1"

class Colors:
    """ANSI цвета для терминала"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    END = '\033[0m'

class TestLogger:
    """Класс для логирования тестов"""
    
    def __init__(self):
        self.test_count = 0
        self.passed_count = 0
        self.failed_count = 0
        self.skipped_count = 0
        
    def log_test_start(self, test_name: str, description: str = ""):
        """Логирует начало теста"""
        self.test_count += 1
        print(f"\n{Colors.BLUE}🧪 Тест #{self.test_count}: {test_name}{Colors.END}")
        if description:
            print(f"   📝 {description}")
    
    def log_success(self, message: str, data: dict = None):
        """Логирует успешный результат"""
        self.passed_count += 1
        print(f"   {Colors.GREEN}✅ {message}{Colors.END}")
        if data:
            print(f"   📊 Данные: {data}")
    
    def log_error(self, message: str, error: Exception = None, response_data: dict = None):
        """Логирует ошибку"""
        self.failed_count += 1
        print(f"   {Colors.RED}❌ {message}{Colors.END}")
        if response_data:
            print(f"   📄 Ответ сервера: {response_data}")
        if error:
            print(f"   🔍 Ошибка: {str(error)}")
            print(f"   📋 Traceback: {traceback.format_exc()}")
    
    def log_skip(self, message: str):
        """Логирует пропуск теста"""
        self.skipped_count += 1
        print(f"   {Colors.YELLOW}⏭️  {message}{Colors.END}")
    
    def log_info(self, message: str):
        """Логирует информацию"""
        print(f"   {Colors.CYAN}ℹ️  {message}{Colors.END}")
    
    def log_warning(self, message: str):
        """Логирует предупреждение"""
        print(f"   {Colors.YELLOW}⚠️  {message}{Colors.END}")
    
    def print_summary(self):
        """Выводит итоговую статистику"""
        total = self.passed_count + self.failed_count + self.skipped_count
        print(f"\n{Colors.BOLD}{'='*60}{Colors.END}")
        print(f"{Colors.BOLD}📊 ИТОГИ ТЕСТИРОВАНИЯ{Colors.END}")
        print(f"{'='*60}")
        print(f"🧪 Всего тестов: {total}")
        print(f"{Colors.GREEN}✅ Пройдено: {self.passed_count}{Colors.END}")
        print(f"{Colors.RED}❌ Провалено: {self.failed_count}{Colors.END}")
        print(f"{Colors.YELLOW}⏭️  Пропущено: {self.skipped_count}{Colors.END}")
        
        if self.failed_count == 0:
            print(f"\n{Colors.GREEN}{Colors.BOLD}🎉 ВСЕ ТЕСТЫ ПРОШЛИ УСПЕШНО!{Colors.END}")
        else:
            print(f"\n{Colors.RED}{Colors.BOLD}⚠️  ЕСТЬ ПРОВАЛЕННЫЕ ТЕСТЫ{Colors.END}")

# Глобальный логгер
logger = TestLogger()

class TestClient:
    """Улучшенный клиент для тестирования API"""
    
    def __init__(self):
        self.token: Optional[str] = None
        self.headers: Dict[str, str] = {}
    
    def set_token(self, token: str):
        """Устанавливает токен авторизации"""
        self.token = token
        self.headers = {"Authorization": f"Bearer {token}"}
        logger.log_info(f"Токен установлен: {token[:20]}...")
    
    async def request(self, method: str, url: str, expected_status: int = None, **kwargs):
        """Выполняет HTTP запрос с детальным логированием"""
        try:
            # Подготавливаем заголовки
            if self.token and "headers" not in kwargs:
                kwargs["headers"] = self.headers
            elif self.token and "headers" in kwargs:
                kwargs["headers"].update(self.headers)
            
            # Логируем запрос
            logger.log_info(f"→ {method} {url}")
            if kwargs.get("data"):
                logger.log_info(f"  Данные: {kwargs['data']}")
            if kwargs.get("files"):
                logger.log_info(f"  Файлы: {list(kwargs['files'].keys())}")
            
            # Выполняем запрос
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.request(method, url, **kwargs)
                
                # Логируем ответ
                logger.log_info(f"← Статус: {response.status_code}")
                
                # Проверяем ожидаемый статус
                if expected_status and response.status_code != expected_status:
                    logger.log_error(f"Неожиданный статус! Ожидался {expected_status}, получен {response.status_code}")
                
                # Пытаемся распарсить JSON
                try:
                    response_data = response.json()
                    logger.log_info(f"  JSON: {response_data}")
                except:
                    logger.log_info(f"  Тело ответа (не JSON): {response.text[:200]}...")
                
                return response
                
        except Exception as e:
            logger.log_error(f"Ошибка выполнения запроса {method} {url}", e)
            raise

# Глобальный клиент для тестов
test_client = TestClient()

class TestHealthCheck:
    """Тестирует базовую работоспособность API"""
    
    async def test_root_endpoint(self):
        """Тест корневого эндпоинта"""
        logger.log_test_start("test_root_endpoint", "Проверка доступности корневого эндпоинта")
        
        try:
            response = await test_client.request("GET", BASE_URL + "/", expected_status=200)
            
            if response.status_code != 200:
                logger.log_error(f"Неверный статус код: {response.status_code}")
                return False
            
            data = response.json()
            if "message" not in data:
                logger.log_error("Отсутствует поле 'message' в ответе", response_data=data)
                return False
            
            logger.log_success(f"Корневой эндпоинт работает", {"message": data["message"]})
            return True
            
        except Exception as e:
            logger.log_error("Ошибка при обращении к корневому эндпоинту", e)
            return False

class TestAuthEndpoints:
    """Тестирует эндпоинты аутентификации"""
    
    async def test_login_invalid_credentials(self):
        """Тест логина с неверными данными"""
        logger.log_test_start("test_login_invalid_credentials", "Проверка ответа на неверные учетные данные")
        
        try:
            response = await test_client.request(
                "POST", 
                f"{API_V1}/auth/login",
                data={"username": "invalid_user", "password": "wrong_password"},
                expected_status=200
            )
            
            if response.status_code != 200:
                logger.log_error(f"Неожиданный статус: {response.status_code}")
                return False
            
            data = response.json()
            
            # Проверяем формат ответа
            if not isinstance(data.get("result"), bool):
                logger.log_error("Поле 'result' отсутствует или не boolean", response_data=data)
                return False
            
            if data["result"] is not False:
                logger.log_error("Ожидался result=false для неверных данных", response_data=data)
                return False
            
            if "error_code" not in data:
                logger.log_error("Отсутствует error_code", response_data=data)
                return False
            
            logger.log_success("Неверные данные корректно обработаны", {
                "error_code": data["error_code"],
                "message": data.get("message", "")
            })
            return True
            
        except Exception as e:
            logger.log_error("Ошибка при тестировании неверных учетных данных", e)
            return False
    
    async def test_login_missing_data(self):
        """Тест логина без данных"""
        logger.log_test_start("test_login_missing_data", "Проверка валидации при отсутствии данных")
        
        try:
            response = await test_client.request(
                "POST", 
                f"{API_V1}/auth/login",
                data={},
                expected_status=422
            )
            
            if response.status_code == 422:
                logger.log_success("Валидация работает корректно - 422 статус")
                return True
            else:
                logger.log_error(f"Ожидался статус 422, получен {response.status_code}")
                return False
                
        except Exception as e:
            logger.log_error("Ошибка при тестировании валидации", e)
            return False
    
    async def test_invite_token_invalid(self):
        """Тест проверки несуществующего приглашения"""
        logger.log_test_start("test_invite_token_invalid", "Проверка несуществующего токена приглашения")
        
        try:
            response = await test_client.request(
                "GET", 
                f"{API_V1}/auth/invite/fake-token-12345",
                expected_status=200
            )
            
            if response.status_code != 200:
                logger.log_error(f"Неожиданный статус: {response.status_code}")
                return False
            
            data = response.json()
            
            if data.get("result") is not False:
                logger.log_error("Ожидался result=false для несуществующего токена", response_data=data)
                return False
            
            if data.get("error_code") != "INVITE_NOT_FOUND":
                logger.log_error("Ожидался error_code=INVITE_NOT_FOUND", response_data=data)
                return False
            
            logger.log_success("Несуществующий токен корректно обработан", {
                "error_code": data["error_code"]
            })
            return True
            
        except Exception as e:
            logger.log_error("Ошибка при тестировании несуществующего токена", e)
            return False
    
    async def test_invite_list_no_auth(self):
        """Тест получения списка приглашений без авторизации"""
        logger.log_test_start("test_invite_list_no_auth", "Проверка доступа без авторизации")
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{API_V1}/auth/invite/list")
                
                if response.status_code == 401:
                    logger.log_success("Неавторизованный доступ корректно заблокирован")
                    return True
                else:
                    logger.log_error(f"Ожидался статус 401, получен {response.status_code}")
                    return False
                    
        except Exception as e:
            logger.log_error("Ошибка при тестировании неавторизованного доступа", e)
            return False
    
    async def test_invite_list_with_auth(self, admin_token):
        """Тест получения списка приглашений с авторизацией"""
        logger.log_test_start("test_invite_list_with_auth", "Проверка получения списка приглашений")
        
        if not admin_token:
            logger.log_skip("Нет токена администратора")
            return True
        
        try:
            response = await test_client.request(
                "GET", 
                f"{API_V1}/auth/invite/list",
                expected_status=200
            )
            
            if response.status_code != 200:
                logger.log_error(f"Неожиданный статус: {response.status_code}")
                return False
            
            data = response.json()
            
            if data.get("result") is not True:
                logger.log_error("Ожидался result=true", response_data=data)
                return False
            
            if "response" not in data:
                logger.log_error("Отсутствует поле 'response'", response_data=data)
                return False
            
            response_data = data["response"]
            
            if "invites" not in response_data:
                logger.log_error("Отсутствует поле 'invites'", response_data=data)
                return False
            
            if "pagination" not in response_data:
                logger.log_error("Отсутствует поле 'pagination'", response_data=data)
                return False
            
            logger.log_success("Список приглашений получен успешно", {
                "количество": len(response_data["invites"]),
                "пагинация": response_data["pagination"]
            })
            return True
            
        except Exception as e:
            logger.log_error("Ошибка при получении списка приглашений", e)
            return False

class TestUserEndpoints:
    """Тестирует пользовательские эндпоинты"""
    
    async def test_me_no_auth(self):
        """Тест получения текущего пользователя без авторизации"""
        logger.log_test_start("test_me_no_auth", "Проверка доступа к /me без авторизации")
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{API_V1}/users/me")
                
                if response.status_code == 401:
                    logger.log_success("Неавторизованный доступ корректно заблокирован")
                    return True
                else:
                    logger.log_error(f"Ожидался статус 401, получен {response.status_code}")
                    return False
                    
        except Exception as e:
            logger.log_error("Ошибка при тестировании неавторизованного доступа к /me", e)
            return False
    
    async def test_me_with_auth(self, admin_token):
        """Тест получения текущего пользователя с авторизацией"""
        logger.log_test_start("test_me_with_auth", "Проверка получения информации о текущем пользователе")
        
        if not admin_token:
            logger.log_skip("Нет токена администратора")
            return True
        
        try:
            response = await test_client.request(
                "GET", 
                f"{API_V1}/users/me",
                expected_status=200
            )
            
            if response.status_code != 200:
                logger.log_error(f"Неожиданный статус: {response.status_code}")
                return False
            
            data = response.json()
            
            if data.get("result") is not True:
                logger.log_error("Ожидался result=true", response_data=data)
                return False
            
            if "response" not in data:
                logger.log_error("Отсутствует поле 'response'", response_data=data)
                return False
            
            user_data = data["response"]
            required_fields = ["id", "email", "username", "role"]
            
            for field in required_fields:
                if field not in user_data:
                    logger.log_error(f"Отсутствует обязательное поле '{field}'", response_data=data)
                    return False
            
            logger.log_success("Информация о текущем пользователе получена", {
                "id": user_data["id"],
                "username": user_data["username"],
                "role": user_data["role"]
            })
            return True
            
        except Exception as e:
            logger.log_error("Ошибка при получении информации о текущем пользователе", e)
            return False
    
    async def test_users_list_no_auth(self):
        """Тест получения списка пользователей без авторизации"""
        logger.log_test_start("test_users_list_no_auth", "Проверка доступа к списку пользователей без авторизации")
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{API_V1}/users/")
                
                if response.status_code == 401:
                    logger.log_success("Неавторизованный доступ корректно заблокирован")
                    return True
                else:
                    logger.log_error(f"Ожидался статус 401, получен {response.status_code}")
                    return False
                    
        except Exception as e:
            logger.log_error("Ошибка при тестировании неавторизованного доступа к списку пользователей", e)
            return False
    
    async def test_users_list_with_auth(self, admin_token):
        """Тест получения списка пользователей с авторизацией"""
        logger.log_test_start("test_users_list_with_auth", "Проверка получения списка пользователей с пагинацией")
        
        if not admin_token:
            logger.log_skip("Нет токена администратора")
            return True
        
        try:
            response = await test_client.request(
                "GET", 
                f"{API_V1}/users/?skip=0&limit=5",
                expected_status=200
            )
            
            if response.status_code != 200:
                logger.log_error(f"Неожиданный статус: {response.status_code}")
                return False
            
            data = response.json()
            
            if data.get("result") is not True:
                logger.log_error("Ожидался result=true", response_data=data)
                return False
            
            response_data = data["response"]
            
            if "users" not in response_data:
                logger.log_error("Отсутствует поле 'users'", response_data=data)
                return False
            
            if "pagination" not in response_data:
                logger.log_error("Отсутствует поле 'pagination'", response_data=data)
                return False
            
            pagination = response_data["pagination"]
            required_pagination_fields = ["skip", "limit", "total"]
            
            for field in required_pagination_fields:
                if field not in pagination:
                    logger.log_error(f"Отсутствует поле пагинации '{field}'", response_data=data)
                    return False
            
            logger.log_success("Список пользователей получен успешно", {
                "количество_в_ответе": len(response_data["users"]),
                "пагинация": pagination
            })
            return True
            
        except Exception as e:
            logger.log_error("Ошибка при получении списка пользователей", e)
            return False
    
    async def test_user_by_id_not_found(self, admin_token):
        """Тест получения несуществующего пользователя"""
        logger.log_test_start("test_user_by_id_not_found", "Проверка обработки несуществующего пользователя")
        
        if not admin_token:
            logger.log_skip("Нет токена администратора")
            return True
        
        try:
            response = await test_client.request(
                "GET", 
                f"{API_V1}/users/99999",
                expected_status=200
            )
            
            if response.status_code != 200:
                logger.log_error(f"Неожиданный статус: {response.status_code}")
                return False
            
            data = response.json()
            
            if data.get("result") is not False:
                logger.log_error("Ожидался result=false для несуществующего пользователя", response_data=data)
                return False
            
            if data.get("error_code") != "USER_NOT_FOUND":
                logger.log_error("Ожидался error_code=USER_NOT_FOUND", response_data=data)
                return False
            
            logger.log_success("Несуществующий пользователь корректно обработан", {
                "error_code": data["error_code"]
            })
            return True
            
        except Exception as e:
            logger.log_error("Ошибка при тестировании несуществующего пользователя", e)
            return False
    
    async def test_students_list(self, admin_token):
        """Тест получения списка студентов"""
        logger.log_test_start("test_students_list", "Проверка получения списка студентов с корректной структурой")
        
        if not admin_token:
            logger.log_skip("Нет токена администратора")
            return True
        
        try:
            response = await test_client.request(
                "GET", 
                f"{API_V1}/users/students?skip=0&limit=3",
                expected_status=200
            )

            if response.status_code != 200:
                logger.log_error(f"Неожиданный статус: {response.status_code}")
                return False
            
            data = response.json()
            
            if data.get("result") is not True:
                logger.log_error("Ожидался result=true", response_data=data)
                return False
            
            response_data = data["response"]
            
            if "students" not in response_data:
                logger.log_error("Отсутствует поле 'students'", response_data=data)
                return False
            
            students = response_data["students"]
            
            # Проверяем структуру данных, если есть студенты
            if students:
                student = students[0]
                if "user" not in student:
                    logger.log_error("Отсутствует поле 'user' в структуре студента", response_data=data)
                    return False
                
                if "student_info" not in student:
                    logger.log_error("Отсутствует поле 'student_info' в структуре студента", response_data=data)
                    return False
                
                logger.log_success("Список студентов получен с корректной структурой", {
                    "количество": len(students),
                    "структура": "user + student_info",
                    "пагинация": response_data.get("pagination", {})
                })
            else:
                logger.log_success("Список студентов пуст (это нормально для тестовой БД)", {
                    "количество": 0
                })
            
            return True
            
        except Exception as e:
            logger.log_error("Ошибка при получении списка студентов", e)
            return False

class TestFileEndpoints:
    """Тестирует файловые эндпоинты"""
    
    async def test_file_not_found_no_auth(self):
        """Тест получения несуществующего файла без авторизации"""
        logger.log_test_start("test_file_not_found_no_auth", "Проверка доступа к файлам без авторизации")
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{API_V1}/files/99999")
                
                if response.status_code == 401:
                    logger.log_success("Неавторизованный доступ к файлам корректно заблокирован")
                    return True
                else:
                    logger.log_error(f"Ожидался статус 401, получен {response.status_code}")
                    return False
                    
        except Exception as e:
            logger.log_error("Ошибка при тестировании неавторизованного доступа к файлам", e)
            return False
    
    async def test_file_not_found_with_auth(self, admin_token):
        """Тест получения несуществующего файла с авторизацией"""
        logger.log_test_start("test_file_not_found_with_auth", "Проверка обработки несуществующего файла")
        
        if not admin_token:
            logger.log_skip("Нет токена администратора")
            return True
        
        try:
            response = await test_client.request(
                "GET", 
                f"{API_V1}/files/99999",
                expected_status=200
            )
            
            if response.status_code != 200:
                logger.log_error(f"Неожиданный статус: {response.status_code}")
                return False
            
            data = response.json()
            
            if data.get("result") is not False:
                logger.log_error("Ожидался result=false для несуществующего файла", response_data=data)
                return False
            
            if data.get("error_code") != "FILE_NOT_FOUND":
                logger.log_error("Ожидался error_code=FILE_NOT_FOUND", response_data=data)
                return False
            
            logger.log_success("Несуществующий файл корректно обработан", {
                "error_code": data["error_code"]
            })
            return True
            
        except Exception as e:
            logger.log_error("Ошибка при тестировании несуществующего файла", e)
            return False
    
    async def test_upload_valid_file(self, admin_token):
        """Тест загрузки валидного файла"""
        logger.log_test_start("test_upload_valid_file", "Проверка загрузки и получения файла")
        
        if not admin_token:
            logger.log_skip("Нет токена администратора")
            return True
        
        try:
            # Создаем тестовый файл
            test_content = b"Test file content for integration testing"
            files = {
                "file": ("test_integration.txt", io.BytesIO(test_content), "text/plain")
            }
            
            # Загружаем файл
            upload_response = await test_client.request(
                "POST", 
                f"{API_V1}/files/",
                files=files,
                expected_status=200
            )
            
            if upload_response.status_code != 200:
                logger.log_error(f"Ошибка загрузки: статус {upload_response.status_code}")
                return False
            
            upload_data = upload_response.json()
            
            if upload_data.get("result") is not True:
                logger.log_error("Загрузка не удалась", response_data=upload_data)
                return False
            
            if "response" not in upload_data:
                logger.log_error("Отсутствует поле 'response' в ответе загрузки", response_data=upload_data)
                return False
            
            file_info = upload_data["response"]
            file_id = file_info.get("id")
            
            if not file_id:
                logger.log_error("Отсутствует ID файла в ответе", response_data=upload_data)
                return False
            
            logger.log_success(f"Файл загружен успешно", {
                "file_id": file_id,
                "filename": file_info.get("filename", "unknown")
            })
            
            # Теперь пытаемся получить файл
            get_response = await test_client.request(
                "GET", 
                f"{API_V1}/files/{file_id}",
                expected_status=200
            )
            
            if get_response.status_code != 200:
                logger.log_error(f"Ошибка получения файла: статус {get_response.status_code}")
                return False
            
            get_data = get_response.json()
            
            if get_data.get("result") is not True:
                logger.log_error("Получение файла не удалось", response_data=get_data)
                return False
            
            logger.log_success("Файл успешно получен после загрузки", {
                "file_id": file_id,
                "filename": get_data["response"].get("filename", "unknown")
            })
            
            return True
            
        except Exception as e:
            logger.log_error("Ошибка при тестировании загрузки файла", e)
            return False

async def get_admin_token():
    """Получает токен администратора для тестов"""
    logger.log_info("🔐 Попытка получить токен администратора...")
    
    test_credentials = [
        {"username": "test_admin", "password": "admin123"},
        {"username": "admin", "password": "admin"},
        {"username": "admin", "password": "admin123"},
        {"username": "test_admin", "password": "password"},
    ]
    
    for i, creds in enumerate(test_credentials, 1):
        try:
            logger.log_info(f"Попытка #{i}: {creds['username']}")
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{API_V1}/auth/login",
                    data=creds,
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    result = response.json()
                    if result.get("result"):
                        token = result["response"]["access_token"]
                        test_client.set_token(token)
                        logger.log_success(f"Токен получен с учетными данными: {creds['username']}")
                        return token
                    else:
                        logger.log_warning(f"Неверные учетные данные для {creds['username']}")
                else:
                    logger.log_warning(f"HTTP {response.status_code} для {creds['username']}")
                    
        except Exception as e:
            logger.log_warning(f"Ошибка при попытке логина {creds['username']}: {str(e)}")
            continue
    
    logger.log_error("Не удалось получить токен администратора с любыми учетными данными")
    return None

async def run_all_tests():
    """Запускает все тесты последовательно с детальным логированием"""
    print(f"{Colors.BOLD}{Colors.BLUE}🚀 ШКОЛЬНЫЙ ДНЕВНИК - ИНТЕГРАЦИОННЫЕ ТЕСТЫ{Colors.END}")
    print(f"{Colors.CYAN}⏰ Начало: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{Colors.END}")
    print("="*60)
    
    # Получаем токен админа
    admin_token = await get_admin_token()
    
    if not admin_token:
        logger.log_warning("Некоторые тесты будут пропущены из-за отсутствия токена администратора")
        logger.log_info("💡 Для создания тестового админа запустите: python create_test_admin.py")
    
    # Создаем экземпляры тестовых классов
    health_tests = TestHealthCheck()
    auth_tests = TestAuthEndpoints()
    user_tests = TestUserEndpoints()
    file_tests = TestFileEndpoints()
    
    # Список всех тестов
    test_suite = [
        # Health Check
        ("🏥 Health Check", [
            (health_tests.test_root_endpoint, [])
        ]),
        
        # Auth Tests
        ("🔐 Authentication", [
            (auth_tests.test_login_invalid_credentials, []),
            (auth_tests.test_login_missing_data, []),
            (auth_tests.test_invite_token_invalid, []),
            (auth_tests.test_invite_list_no_auth, []),
            (auth_tests.test_invite_list_with_auth, [admin_token])
        ]),
        
        # User Tests
        ("👥 Users", [
            (user_tests.test_me_no_auth, []),
            (user_tests.test_me_with_auth, [admin_token]),
            (user_tests.test_users_list_no_auth, []),
            (user_tests.test_users_list_with_auth, [admin_token]),
            (user_tests.test_user_by_id_not_found, [admin_token]),
            (user_tests.test_students_list, [admin_token])
        ]),
        
        # File Tests
        ("📁 Files", [
            (file_tests.test_file_not_found_no_auth, []),
            (file_tests.test_file_not_found_with_auth, [admin_token]),
            (file_tests.test_upload_valid_file, [admin_token])
        ])
    ]
    
    # Выполняем тесты
    for category_name, tests in test_suite:
        print(f"\n{Colors.BOLD}{Colors.PURPLE}{'='*60}{Colors.END}")
        print(f"{Colors.BOLD}{Colors.PURPLE}{category_name} ТЕСТЫ{Colors.END}")
        print(f"{Colors.PURPLE}{'='*60}{Colors.END}")
        
        for test_func, args in tests:
            try:
                await test_func(*args)
            except Exception as e:
                logger.log_error(f"Критическая ошибка в тесте {test_func.__name__}", e)
    
    # Выводим итоговую статистику
    logger.print_summary()
    
    print(f"\n{Colors.CYAN}⏰ Окончание: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{Colors.END}")
    
    # Возвращаем код завершения
    return 0 if logger.failed_count == 0 else 1

if __name__ == "__main__":
    exit_code = asyncio.run(run_all_tests())
    sys.exit(exit_code) 