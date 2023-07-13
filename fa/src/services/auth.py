from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from jose import jwt, JWTError
from redis import Redis

from datetime import datetime, timedelta
import pickle

from src.database.db import get_db
from src.database.redis_db import get_async_redis_client
from src.repository.users import get_user_by_email


class Auth:
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    SECRET_KEY = "3efdb0bd9fef572516d19aa6bff146e264708df086a559230cf358ebee036172"
    ALGORITHM = "HS256"
    oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

    def get_hashed_password(self, password: str):
        hashed_password = self.pwd_context.hash(password)
        return hashed_password

    def verify_password(self, password, hashed_password):
        verify = self.pwd_context.verify(password, hashed_password)
        return verify

    def create_access_token(self, data: dict):
        to_encode = data.copy()
        current_time = datetime.utcnow()
        expire = current_time + timedelta(minutes=15)
        scope = "access token"
        to_encode.update({"iat": current_time, "exp": expire, "scope": scope})
        encoded_access_token = jwt.encode(to_encode, self.SECRET_KEY, self.ALGORITHM)
        return encoded_access_token

    def create_refresh_token(self, data: dict):
        to_encode = data.copy()
        current_time = datetime.utcnow()
        expire = current_time + timedelta(days=7)
        scope = "refresh token"
        to_encode.update({"iat": current_time, "exp": expire, "scope": scope})
        encoded_access_token = jwt.encode(to_encode, self.SECRET_KEY, self.ALGORITHM)
        return encoded_access_token
    
    def create_email_token(self, data: dict):
        to_encode = data.copy()
        current_time = datetime.utcnow()
        expire = current_time + timedelta(days=7)
        scope = "email token"
        to_encode.update({"iat": current_time, "exp": expire, "scope": scope})
        encoded_email_token = jwt.encode(to_encode, self.SECRET_KEY, self.ALGORITHM)
        return encoded_email_token

    def decode_refresh_token(self, token: str):
        try:
            payload = jwt.decode(token, self.SECRET_KEY, self.ALGORITHM)

            if payload.get("scope") == "refresh token":
                email = payload.get("sub")
                return email
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid scope for token")
        except JWTError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials")
    
    def get_email_from_token(self, token: str):
        try:
            payload = jwt.decode(token, self.SECRET_KEY, self.ALGORITHM)

            if payload.get("scope") == "email token":
                email = payload.get("sub")
                return email
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid scope for token")
        except JWTError as e:
            print(e)
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                detail=f"{e}\nInvalid token for email verification")

    async def get_current_user(self, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
        credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, 
                                          detail="Could not validate credentials", 
                                          headers={"WWW-Authenticate": "Bearer"})

        try:
            payload = jwt.decode(token, self.SECRET_KEY, self.ALGORITHM)

            if payload.get("scope") == "access token":
                email = payload.get("sub")

                if email is None:
                    raise credentials_exception
            else:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid scope for token")
        except JWTError:
            raise credentials_exception
        
        redis_client = await get_async_redis_client()
        user = await redis_client.get(f"user:{email}")
        if user is None:
            user = await get_user_by_email(email, db)
            if user is None:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User doesn't exist")
            redis_client.set(f"user:{email}", pickle.dumps(user))
            redis_client.expire(f"user:{email}", 900)
        else:
            user = pickle.loads(user)
        return user
    

auth_service = Auth()
