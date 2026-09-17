from typing import Optional

from domain.models.auth import Auth
from domain.models.iauth_repository import IAuthRepository
from infrastructure.databases.factory_database import FactoryDatabase as db_factory
from infrastructure.models.auth.auth_role_model import AuthRoleModel, AuthUserRoleModel
from infrastructure.models.auth.auth_user_model import AuthUserModel
from werkzeug.security import check_password_hash


class AuthRepository(IAuthRepository):
    """Database repository used by the backend authentication API.

    A fresh SQLAlchemy session is used per operation so a long-running Flask
    process does not keep a stale DB session/connection alive.
    """

    def _session(self):
        return db_factory.get_database('POSTGREE').new_session()

    def login(self, auth: Auth) -> Optional[Auth]:
        session = self._session()
        try:
            user = session.query(AuthUserModel).filter(
                AuthUserModel.username == auth.username
            ).first()
            if not user or not check_password_hash(user.password_hash, auth.password):
                return None
            auth.id = user.id
            auth.email = user.email
            return auth
        finally:
            session.close()

    def get_user(self, user_id: int) -> Optional[dict]:
        session = self._session()
        try:
            user = session.query(AuthUserModel).filter(
                AuthUserModel.id == user_id
            ).first()
            if not user:
                return None
            role_row = (
                session.query(AuthRoleModel)
                .join(AuthUserRoleModel, AuthUserRoleModel.role_id == AuthRoleModel.id)
                .filter(AuthUserRoleModel.user_id == user.id)
                .first()
            )
            return {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'role': role_row.name if role_row else 'PASSENGER',
            }
        finally:
            session.close()

    def register(self, auth: Auth) -> Optional[Auth]:
        session = self._session()
        try:
            new_user = AuthUserModel(
                username=auth.username,
                password_hash=auth.password,
                email=auth.email
            )
            session.add(new_user)
            session.commit()
            session.refresh(new_user)
            auth.id = new_user.id
            return auth
        except Exception:
            session.rollback()
            return None
        finally:
            session.close()

    def remember_password(self) -> Optional[Auth]:
        return None

    def look_account(self, Id: int) -> bool:
        return True

    def un_look_account(self, course_id: int) -> None:
        pass

    def check_exist(self, username: str) -> bool:
        session = self._session()
        try:
            return session.query(AuthUserModel).filter(
                AuthUserModel.username == username.strip().lower()
            ).first() is not None
        finally:
            session.close()
