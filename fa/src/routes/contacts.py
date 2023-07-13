from fastapi import Depends, status, Path, Query, APIRouter
from fastapi_limiter.depends import RateLimiter
from sqlalchemy.orm import Session
from sqlalchemy import and_

from typing import List

from src.database.db import get_db
from src.database.models import User
from src.schemas.contacts import ContactModel, ContactResponseModel
from src.repository import contacts as repository_contacts
from src.services.auth import auth_service


router = APIRouter(prefix="/contacts", tags=["contacts"])    

@router.get("/", response_model=List[ContactResponseModel], 
            description='No more than 2 requests per 5 seconds',
            dependencies=[Depends(RateLimiter(times=2, seconds=5))])
async def get_contacts(limit: int = Query(10, le=100), skip: int = 0, user: User = Depends(auth_service.get_current_user), db: Session = Depends(get_db)):
    contacts = await repository_contacts.get_contacts(limit, skip, user, db)
    
    return contacts


@router.get("/week_birthday_people", response_model=List[ContactResponseModel], 
            description='No more than 2 requests per 5 seconds',
            dependencies=[Depends(RateLimiter(times=2, seconds=5))])
async def get_week_birthday_people(user: User = Depends(auth_service.get_current_user), db: Session = Depends(get_db)):
    contacts = await repository_contacts.get_week_birthday_people(user, db)
    return contacts


@router.get("/{contact_id}", response_model=ContactResponseModel, 
            description='No more than 2 requests per 5 seconds',
            dependencies=[Depends(RateLimiter(times=2, seconds=5))])
async def get_contact_by_id(contact_id: int = Path(ge=1), user: User = Depends(auth_service.get_current_user), db: Session = Depends(get_db)):
    contact = await repository_contacts.get_contact_by_id(contact_id, user, db)
    
    return contact


@router.get("/first_name/{contact_first_name}", response_model=ContactResponseModel, 
            description='No more than 2 requests per 5 seconds',
            dependencies=[Depends(RateLimiter(times=2, seconds=5))])
async def get_contact_by_first_name(contact_first_name, user: User = Depends(auth_service.get_current_user), db: Session = Depends(get_db)):
    contact = await repository_contacts.get_contact_by_first_name(contact_first_name, user, db)

    return contact


@router.get("/last_name/{contact_last_name}", response_model=ContactResponseModel, 
            description='No more than 2 requests per 5 seconds',
            dependencies=[Depends(RateLimiter(times=2, seconds=5))])
async def get_contact_by_last_name(contact_last_name, user: User = Depends(auth_service.get_current_user), db: Session = Depends(get_db)):
    contact = await repository_contacts.get_contact_by_last_name(contact_last_name, user, db)

    return contact


@router.get("/email/{contact_email}", response_model=ContactResponseModel, 
            description='No more than 2 requests per 5 seconds',
            dependencies=[Depends(RateLimiter(times=2, seconds=5))])
async def get_contact_by_email(contact_email, user: User = Depends(auth_service.get_current_user), db: Session = Depends(get_db)):
    contact = await repository_contacts.get_contact_by_email(contact_email, user, db)

    return contact


@router.post("/", response_model=ContactResponseModel, status_code=status.HTTP_201_CREATED, 
            description='No more than 2 requests per 5 seconds',
            dependencies=[Depends(RateLimiter(times=2, seconds=5))])
async def create_contact(body: ContactModel, user: User = Depends(auth_service.get_current_user), db: Session = Depends(get_db)):
    contact = await repository_contacts.create_contact(body, user, db)

    return contact
    

@router.put("/{contact_id}", response_model=ContactResponseModel, 
            description='No more than 2 requests per 5 seconds',
            dependencies=[Depends(RateLimiter(times=2, seconds=5))])
async def update_contact(body: ContactModel, contact_id: int, user: User = Depends(auth_service.get_current_user), db: Session = Depends(get_db)):
    contact = await repository_contacts.update_contact(body, contact_id, user, db)

    return contact


@router.delete("/{contact_id}", status_code=status.HTTP_204_NO_CONTENT, 
            description='No more than 2 requests per 5 seconds',
            dependencies=[Depends(RateLimiter(times=2, seconds=5))])
async def remove_contact(contact_id: int, user: User = Depends(auth_service.get_current_user), db: Session = Depends(get_db)):
    await repository_contacts.remove_contact(contact_id, user, db)
