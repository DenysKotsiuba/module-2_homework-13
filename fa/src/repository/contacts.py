from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import and_

from datetime import date

from src.database.db import get_db
from src.database.models import Contact, User
from src.schemas.contacts import ContactModel


async def get_contacts(limit: int, offset: int, user: User, db: Session):
    contacts = db.query(Contact).filter_by(user_id=user.id).order_by(Contact.id).limit(limit).offset(offset).all()
    
    return contacts


async def get_contact_by_id(contact_id: int, user: User, db: Session):
    contact = db.query(Contact).filter(and_(Contact.user_id==user.id, Contact.id==contact_id)).first()

    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    
    return contact


async def get_contact_by_first_name(contact_first_name: str, user: User, db: Session):
    contact = db.query(Contact).filter(and_(Contact.user_id==user.id, Contact.first_name==contact_first_name)).first()

    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    return contact


async def get_contact_by_last_name(contact_last_name: str, user: User, db: Session):
    contact = db.query(Contact).filter(and_(Contact.user_id==user.id, Contact.last_name==contact_last_name)).first()

    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    return contact


async def get_contact_by_email(contact_email: str, user: User, db: Session):
    contact = db.query(Contact).filter(and_(Contact.user_id==user.id, Contact.email==contact_email)).first()

    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    return contact


async def get_week_birthday_people(user: User, db: Session):
    birthday_people = []

    today = date.today()
    week = [date(year=today.year, month=today.month, day=today.day+num) for num in range(7)]

    objs = db.query(Contact).filter_by(user_id=user.id).all()

    for obj in objs:
        this_year_birthday = obj.birth_date.replace(year=today.year)

        if this_year_birthday in week:
            birthday_people.append(obj)

    return birthday_people


async def create_contact(body: ContactModel, user: User, db: Session):
    contact = db.query(Contact).filter_by(email=body.email).first()

    if contact:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email exists")
    
    contact = Contact(**body.dict(), user_id=user.id)
    db.add(contact)
    db.commit()
    db.refresh(contact)

    return contact
    

async def update_contact(body: ContactModel, contact_id: int, user: User, db: Session):
    contact = db.query(Contact).filter(Contact.email==body.email).first()

    if contact:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email exists")
    
    contact = db.query(Contact).filter(and_(Contact.user_id==user.id, Contact.id==contact_id)).first()

    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    
    contact.first_name = body.first_name
    contact.last_name = body.last_name
    contact.email = body.email
    contact.birth_date = body.birth_date
    contact.additional_data = body.additional_data
    db.commit()

    return contact


async def remove_contact(contact_id: int, user: User, db: Session):
    contact = db.query(Contact).filter(and_(Contact.user_id==user.id, Contact.id==contact_id)).first()

    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    
    db.delete(contact)
    db.commit()
