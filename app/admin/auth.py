from typing import Optional

from fastapi import Depends, Request, Response
from jose import ExpiredSignatureError, JWTError, jwt
from settings import settings
from sqladmin.authentication import AuthenticationBackend
from v1.auth.service_auth import set_tokens
from v1.dependencies.auth_dep import get_current_admin_user
from v1.dependencies.dao_dep import get_session_without_commit
from v1.users.dao import UserDAO


class AdminAuth(AuthenticationBackend):
    """Класс аутентификации для админ-панели с использованием JWT токенов."""
    
    async def login(self, request: Request) -> bool:
        """Обработка входа пользователя."""
        form = await request.form()
        email = form.get("username")
        password = form.get("password")
        
        if not email or not password:
            return False
        
        # Получаем сессию для работы с БД
        session = await get_session_without_commit()
        
        try:
            # Ищем пользователя по email
            user_dao = UserDAO(session)
            user = await user_dao.find_one_or_none(email=email)
            
            if not user:
                return False
            
            # Проверяем пароль и роль пользователя
            from v1.auth.service_auth import authenticate_user
            if not await authenticate_user(user=user, password=password):
                return False
                
            # Проверяем, имеет ли пользователь права администратора
            if user.role.value not in ["superuser", "fund_admin"]:
                return False
                
            # Устанавливаем JWT токены в cookies
            response = Response()
            set_tokens(response, user.id)
            
            # Копируем cookies из ответа в запрос
            for key, value in response.headers.items():
                if key == 'set-cookie':
                    request.cookies.update({
                        cookie.split('=')[0].strip(): cookie.split('=')[1].split(';')[0].strip()
                        for cookie in value.split(',')
                    })
                    
            return True
        except Exception:
            return False
        finally:
            await session.close()
    
    async def logout(self, request: Request) -> bool:
        """Обработка выхода пользователя."""
        # Удаляем cookies с токенами
        response = Response()
        response.delete_cookie("user_access_token")
        response.delete_cookie("user_refresh_token")
        
        # Очищаем cookies в запросе
        if "user_access_token" in request.cookies:
            request.cookies.pop("user_access_token")
        if "user_refresh_token" in request.cookies:
            request.cookies.pop("user_refresh_token")
            
        return True
    
    async def authenticate(self, request: Request) -> Optional[bool]:
        """Проверка аутентификации для каждого запроса к админке."""
        # Проверяем наличие токена
        token = request.cookies.get("user_access_token")
        if not token:
            return False
        
        try:
            # Декодируем токен
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            user_id = payload.get("sub")
            
            if not user_id:
                return False
            
            # Получаем сессию для работы с БД
            session = await get_session_without_commit()
            
            try:
                # Проверяем существование пользователя и его права
                user_dao = UserDAO(session)
                user = await user_dao.find_one_or_none_by_id(data_id=int(user_id))
                
                if not user:
                    return False
                
                # Проверяем роль пользователя
                if user.role.value not in ["superuser", "fund_admin"]:
                    return False
                
                return True
            finally:
                await session.close()
                
        except ExpiredSignatureError:
            return False
        except JWTError:
            return False
        except Exception:
            return False
