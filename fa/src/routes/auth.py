from fastapi import APIRouter, Depends, status, HTTPException, Security, BackgroundTasks, Request
from fastapi.security import OAuth2PasswordRequestForm, HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from src.database.db import get_db
from src.schemas.users import UserModel, UserResponseModel, TokenResponseModel, RequestEmail
from src.repository.users import create_user, get_user_by_email, update_token, confirme_email
from src.services.auth import auth_service
from src.services.email import send_email


router = APIRouter(prefix="/auth", tags=["Auth"])

security = HTTPBearer()


@router.post("/signup", response_model=UserResponseModel, status_code=status.HTTP_201_CREATED)
async def signup(body: UserModel, background_tasks: BackgroundTasks, request: Request, db: Session = Depends(get_db)):
    exist_user = await get_user_by_email(body.email, db)
    if exist_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Account already exists")
    body.password = auth_service.get_hashed_password(body.password)
    user = await create_user(body, db)
    background_tasks.add_task(send_email, user.email, user.username, request.base_url)
    return {"user": user, "detail": "User successfully created"}


@router.post("/login", response_model=TokenResponseModel)
async def login(body: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = await get_user_by_email(body.username, db)

    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email")
    if not user.confirmed:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Email not confirmed")
    if not auth_service.verify_password(body.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid password")
    
    access_token = auth_service.create_access_token({"sub": body.username})
    refresh_token = auth_service.create_refresh_token({"sub": body.username})
    await update_token(user, refresh_token, db)
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


@router.get("/refresh_token", response_model=TokenResponseModel)
async def refresh_token(credentials: HTTPAuthorizationCredentials = Security(security), db: Session = Depends(get_db)):
    token = credentials.credentials
    email = auth_service.decode_refresh_token(token)
    user = await get_user_by_email(email, db)

    if token != user.refresh_token:
        await update_token(user, None, db)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")
    
    access_token = auth_service.create_access_token({"sub": email})
    refresh_token = auth_service.create_refresh_token({"sub": email})
    await update_token(user, refresh_token, db)
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


@router.post('/request_email')
async def request_email(body: RequestEmail, background_tasks: BackgroundTasks, request: Request,
                        db: Session = Depends(get_db)):
    user = await get_user_by_email(body.email, db)

    if user and user.confirmed:
        return {"message": "Your email is already confirmed"}
    if user:
        background_tasks.add_task(send_email, user.email, user.username, str(request.base_url))
    return {"message": "Check your email for confirmation."}


@router.get('/confirmed_email/{email_token}')
async def confirmed_email(email_token: str, db: Session = Depends(get_db)):
    email = auth_service.get_email_from_token(email_token)
    user = await get_user_by_email(email, db)
    if user is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Verification error")
    if user.confirmed:
        return {"message": "Your email is already confirmed"}
    await confirme_email(email, db)
    return {"message": "Email confirmed"}