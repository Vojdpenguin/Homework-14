import unittest
from unittest.mock import MagicMock

from sqlalchemy.orm import Session

from src.database.models import Contacts, User
from src.schemas import ContactCreate, ContactUpdate
from src.repository.contacts import (
    get_contacts,
    get_contact,
    create_contact,
    remove_contact,
    update_contact
)


class TestContacts(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.session = MagicMock(spec=Session)
        self.user = User(id=7)

    async def test_get_contacts(self):
        contacts = [Contacts(), Contacts(), Contacts()]
        self.session.query().filter().offset().limit().all.return_value = contacts
        result = await get_contacts(skip=0, limit=10, user=self.user, db=self.session)
        self.assertEqual(result, contacts)

    async def test_get_contact_found(self):
        contact = Contacts()
        self.session.query().filter().first.return_value = contact
        result = await get_contact(1, user=self.user, db=self.session)
        self.assertIsNotNone(result)

    async def test_get_contact_not_found(self):
        self.session.query().filter().first.return_value = None
        result = await get_contact(contact_id=1, user=self.user, db=self.session)
        self.assertIsNone(result)

    async def test_create_contact(self):
        body = ContactCreate(name="Max", surname="Vojd", email="example@example.com", phone_number="123456789",
                             birthday=None)

        contact = Contacts(name=body.name, surname=body.surname, email=body.email, phone_number=body.phone_number,
                           birthday=body.birthday)

        self.session.add.return_value = None
        self.session.commit.return_value = None
        self.session.refresh.return_value = contact

        self.session.query().filter().first.return_value = contact

        result = await create_contact(body=body, user=self.user, db=self.session)

        self.assertEqual(result.name, body.name)
        self.assertEqual(result.surname, body.surname)
        self.assertEqual(result.email, body.email)
        self.assertEqual(result.phone_number, body.phone_number)
        self.assertEqual(result.birthday, body.birthday)

    async def test_remove_contact_found(self):
        contact = Contacts()
        self.session.query().filter().first.return_value = contact
        result = await remove_contact(contact_id=1, user=self.user, db=self.session)
        self.assertEqual(result, contact)

    async def test_remove_contact_not_found(self):
        self.session.query().filter().first.return_value = None
        result = await remove_contact(contact_id=1, user=self.user, db=self.session)
        self.assertIsNone(result)

    async def test_update_contact_found(self):
        contact_id = 1
        contact = Contacts(id=contact_id, name="Old Name", surname="Old Surname", email="old_email@example.com")
        user = User(id=1)
        contact_update = ContactUpdate(
            name="New Name", surname="New Surname", email="new_email@example.com", phone_number="123456789",
            birthday=None
        )

        db = MagicMock(Session)
        db.query().filter().first.return_value = contact

        result = await update_contact(contact_id=contact_id, body=contact_update, user=user, db=db)

        assert result is not None
        assert result.name == "New Name"
        assert result.surname == "New Surname"
        assert result.email == "new_email@example.com"
        assert result.phone_number == "123456789"
        assert result.birthday is None
        db.commit.assert_called_once()

    async def test_update_contact_not_found(self):
        contact_id = 1
        user = User(id=1)
        contact_update = ContactUpdate(
            name="New Name", surname="New Surname", email="new_email@example.com", phone_number="123456789",
            birthday=None
        )

        db = MagicMock(Session)
        db.query().filter().first.return_value = None

        result = await update_contact(contact_id=contact_id, body=contact_update, user=user, db=db)

        assert result is None
        db.commit.assert_not_called()

if __name__ == "__main__":
    unittest.main()