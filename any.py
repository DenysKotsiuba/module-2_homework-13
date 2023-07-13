from fastapi import HTTPException, status
from jose import jwt, JWTError
from datetime import datetime, timedelta
SECRET_KEY = "3efdb0bd9fef572516d19aa6bff146e264708df086a559230cf358ebee036172"
ALGORITHM = "HS256"



    
def create_email_token(data: dict):
    to_encode = data.copy()
    current_time = datetime.utcnow()
    expire = current_time + timedelta(days=7)
    scope = "email token"
    to_encode.update({"iat": current_time, "exp": expire, "scope": scope})
    encoded_email_token = jwt.encode(to_encode, SECRET_KEY, ALGORITHM)
    return encoded_email_token

def get_email_from_token(token: str):
        print(token, type(token))
        try:
            payload = jwt.decode(token, SECRET_KEY, ALGORITHM)

            if payload.get("scope") == "email token":
                email = payload.get("sub")
                return email
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid scope for token")
        except JWTError as e:
            print(e)
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                detail="Invalid token for email verification")
encoded_email_token = create_email_token({"sub": "python.course@meta.ua"})   
print(encoded_email_token, type(encoded_email_token))
print(get_email_from_token(encoded_email_token))