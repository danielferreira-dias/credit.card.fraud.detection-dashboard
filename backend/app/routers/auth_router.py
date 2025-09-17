from app.infra.logger import setup_logger
from app.exception.user_exceptions import UserCredentialsException
from app.settings.database import get_db
from app.service.auth_service import AuthService
from app.service.user_service import UserService
from app.schemas.user_schema import UserLoginAuthentication
from app.security.security import SecurityManager
from fastapi import APIRouter, Depends
from fastapi.security import HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.auth_schema import TokenResponse

router = APIRouter(
    prefix="/auth",
    tags=["auths"]
)

logger = setup_logger(__name__)
security = HTTPBearer()

# --- dependencies ------------------------
def get_security_manager(db: AsyncSession = Depends(get_db)) -> SecurityManager:
    user_service = UserService(db)
    return SecurityManager(user_service)

def get_current_user(token: str = Depends(security), security_manager: SecurityManager = Depends(get_security_manager)):
    """
        Gets the current User's token to see if it matches to request protected Router
    """
    payload = security_manager.verify_token(token.credentials)
    if payload is None:
        raise UserCredentialsException("User is not authorized")
    return payload

def get_security_service(db: AsyncSession = Depends(get_db)) -> AuthService:
    user_service = UserService(db)
    security_manager = SecurityManager(user_service)
    return AuthService(security_manager, user_service)
    
# --- router ------------------------

@router.post('/login')
async def login( credentials: UserLoginAuthentication, auth_service: AuthService = Depends(get_security_service)) -> TokenResponse:
    token = await auth_service.login_service(credentials.email, credentials.password)
    return token
    