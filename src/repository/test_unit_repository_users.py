import unittest
from unittest.mock import MagicMock

from sqlalchemy.orm import Session
from src.database.models import User
from src.schemas import UserModel
from src.repository.users import (
    get_user_by_email,
    create_user,
    update_token,
    confirmed_email,
    update_avatar
)
from libgravatar import Gravatar

class TestUsers(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.session = MagicMock(spec=Session)

    async def test_get_user_by_email_found(self):
        user = User(email="example@example.com")
        self.session.query().filter().first.return_value = user

        result = await get_user_by_email(email="example@example.com", db=self.session)
        self.assertIsNotNone(result)
        self.assertEqual(result.email, "example@example.com")


    async def test_get_user_by_email_not_found(self):
        self.session.query().filter().first.return_value = None

        result = await get_user_by_email(email="example@example.com", db=self.session)
        self.assertIsNone(result)

    async def test_create_user(self):
        body = UserModel(username="test111", email="example@example.com", password="password")
        avatar_url = "https://www.gravatar.com/avatar/example"

        self.session.add.return_value = None
        self.session.commit.return_value = None

        new_user = User(id=1, username=body.username, email=body.email, avatar=avatar_url, created_at="2024-12-11")
        self.session.refresh.return_value = new_user

        Gravatar.get_image = MagicMock(return_value=avatar_url)

        result = await create_user(body=body, db=self.session)

        self.assertEqual(result.username, body.username)
        self.assertEqual(result.email, body.email)
        self.assertEqual(result.avatar, avatar_url)
        self.session.add.assert_called_once()
        self.session.commit.assert_called_once()

    async def test_update_token(self):
        user = User(email="user@example.com", refresh_token = None)
        self.session.commit.return_value = None

        await update_token(user=user, token="new_refresh_token", db=self.session)

        self.assertEqual(user.refresh_token, "new_refresh_token")
        self.session.commit.assert_called_once()

    async def test_confirmed_email(self):
        user = User(email="user@example.com", confirmed=False)
        self.session.query().filter().first.return_value = user
        self.session.commit.return_value = None

        await confirmed_email(email="user@example.com", db=self.session)

        self.assertTrue(user.confirmed)
        self.session.commit.assert_called_once()

    async def test_update_avatar(self):
        user = User(email="user@example.com", avatar="old_avatar_url")
        new_avatar_url = "https://www.new-avatar.com/image.png"

        self.session.query().filter().first.return_value = user
        self.session.commit.return_value = None

        result = await update_avatar(email="user@example.com", url=new_avatar_url, db=self.session)

        self.assertEqual(result.avatar, new_avatar_url)
        self.session.commit.assert_called_once()

if __name__ == "__main__":
    unittest.main()