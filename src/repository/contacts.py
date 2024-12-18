from typing import List, Optional

from fastapi import HTTPException, status
from sqlalchemy import func, or_, and_
from sqlalchemy.orm import Session

from src.database.models import Contacts, User
from src.schemas import ContactCreate, ContactUpdate
from datetime import datetime, timedelta


async def get_contacts(skip: int, limit: int, user: User, db: Session) -> List[Contacts]:
    """
        Retrieves a list of contacts for a specific user with specified pagination parameters.

        :param skip: The number of contacts to skip.
        :type skip: int
        :param limit: The maximum number of contacts to return.
        :type limit: int
        :param user: The user to retrieve contacts for.
        :type user: User
        :param db: The database session.
        :type db: Session
        :return: A list of contacts.
        :rtype: List[Contact]
        """
    return db.query(Contacts).filter(Contacts.user_id == user.id).offset(skip).limit(limit).all()


async def get_contact(contact_id: int, user: User, db: Session) -> Contacts:
    """
        Retrieves a single Contact with the specified ID for a specific user.

        :param contact_id: The ID of the Contact to retrieve.
        :type contact_id: int
        :param user: The user to retrieve the Contact for.
        :type user: User
        :param db: The database session.
        :type db: Session
        :return: The Contact with the specified ID, or None if it does not exist.
        :rtype: Contact | None
        """
    return db.query(Contacts).filter(and_(Contacts.id == contact_id, Contacts.user_id == user.id)).first()


async def create_contact(body: ContactCreate, user: User, db: Session) -> Contacts:
    """
        Creates a new contact for a specific user.

        :param body: The data for the contact to create.
        :type body: ContactCreate
        :param user: The user to create the contact for.
        :type user: User
        :param db: The database session.
        :type db: Session
        :return: The newly created contact.
        :rtype: Contact
        """
    contact = Contacts(name=body.name, surname=body.surname, email=body.email, phone_number=body.phone_number,
                       birthday=body.birthday, user_id=user.id)
    db.add(contact)
    db.commit()
    db.refresh(contact)
    return contact


async def remove_contact(contact_id: int, user: User, db: Session) -> Contacts | None:
    """
        Removes a single contact with the specified ID for a specific user.

        :param contact_id: The ID of the contact to remove.
        :type contact_id: int
        :param user: The user to remove the contact for.
        :type user: User
        :param db: The database session.
        :type db: Session
        :return: The removed contact, or None if it does not exist.
        :rtype: Contact | None
        """
    contact = db.query(Contacts).filter(and_(Contacts.id == contact_id, Contacts.user_id == user.id)).first()
    if contact:
        db.delete(contact)
        db.commit()
    return contact


async def update_contact(contact_id: int, body: ContactUpdate, user: User, db: Session) -> Contacts | None:
    """
        Updates a single contact with the specified ID for a specific user.

        :param contact_id: The ID of the contact to update.
        :type contact_id: int
        :param body: The updated data for the contact.
        :type body: ContactUpdate
        :param user: The user to update the contact for.
        :type user: User
        :param db: The database session.
        :type db: Session
        :return: The updated contact, or None if it does not exist.
        :rtype: Contact | None
        """
    contact = db.query(Contacts).filter(and_(Contacts.id == contact_id, Contacts.user_id == user.id)).first()
    if contact:
        contact.name = body.name
        contact.surname = body.surname
        contact.email = body.email
        contact.phone_number = body.phone_number
        contact.birthday = body.birthday
        db.commit()
    return contact


async def filter_contacts(name: Optional[str], surname: Optional[str], email: Optional[str], user: User, db: Session) -> \
list[
    Contacts]:
    """
        Filters contacts based on the given criteria (name, surname, email) for a specific user.

        :param name: Optional name to filter contacts by.
        :type name: Optional[str]
        :param surname: Optional surname to filter contacts by.
        :type surname: Optional[str]
        :param email: Optional email to filter contacts by.
        :type email: Optional[str]
        :param user: The user whose contacts are being filtered.
        :type user: User
        :param db: The database session.
        :type db: Session
        :return: A list of contacts that match the given filters.
        :rtype: list[Contacts]
        :raises HTTPException: If no filters are provided.
        """
    conditions = [Contacts.user_id == user.id]
    if name:
        conditions.append(Contacts.name.ilike(f'%{name}%'))
    if surname:
        conditions.append(Contacts.surname.ilike(f'%{surname}%'))
    if email:
        conditions.append(Contacts.email.ilike(f'%{email}%'))
    if len(conditions) == 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Мінімум один фільтр повинен бути заданий")

    return db.query(Contacts).filter(and_(*conditions)).all()


async def get_birthday_contacts(user: User, db: Session) -> list[Contacts]:
    """
       Retrieves a list of contacts whose birthdays fall within the next seven days for a specific user.

       :param user: The user whose contacts are being queried.
       :type user: User
       :param db: The database session.
       :type db: Session
       :return: A list of contacts with upcoming birthdays within the next seven days.
       :rtype: list[Contacts]
       """
    today = datetime.today().date()
    seven_days_later = today + timedelta(days=7)

    today_day_of_year = func.extract('doy', today)
    seven_days_later_day_of_year = func.extract('doy', seven_days_later)

    query = db.query(Contacts).filter(
        Contacts.user_id == user.id,
        or_(
            and_(
                func.extract('doy', Contacts.birthday) >= today_day_of_year,
                func.extract('doy', Contacts.birthday) <= seven_days_later_day_of_year
            ),
            and_(
                func.extract('doy', Contacts.birthday) < (seven_days_later_day_of_year - 365),
                func.extract('doy', Contacts.birthday) >= today_day_of_year
            )
        )
    )

    return query.all()
