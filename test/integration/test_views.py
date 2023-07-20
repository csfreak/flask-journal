import typing as t

from flask import Flask
from flask.testing import FlaskClient

from flask_journal import models

from ..base import AppClientTestBase
from ..config import html_test_strings
from ..utils import authenticate


class HomeViewClientTest(AppClientTestBase):

    def test_index_view(self: t.Self, app: Flask, client: FlaskClient) -> None:
        rv = client.get('/')
        self.assertStatus(rv, 301)
        self.assertLocationHeader(rv, '/home')

    def test_home_view_anon(self: t.Self, app: Flask, client: FlaskClient) -> None:
        rv = client.get('/home')
        self.assertStatus(rv, 200)
        self.assertInResponse(b'<title>Journal</title>', rv)
        self.assertInResponse(html_test_strings['nav']['login'], rv)
        self.assertInResponse(html_test_strings['nav']['register'], rv)

    def test_home_view_authed(self: t.Self, app: Flask, client: FlaskClient) -> None:
        email = 'user1@example.test'
        authenticate(client, email)
        rv = client.get('/home')
        self.assertStatus(rv, 200)
        self.assertInResponse(b'<title>Journal</title>', rv)
        self.assertInResponse(html_test_strings['nav']['logout'], rv)
        self.assertInResponse(html_test_strings['nav']['settings'], rv)


class UserViewClientTest(AppClientTestBase):
    def test_users_view_admin(self: t.Self, app: Flask, client: FlaskClient) -> None:
        email = 'user1@example.test'
        authenticate(client, email)
        rv = client.get('/users')
        self.assertStatus(rv, 200)
        self.assertInResponse(html_test_strings['title'] % b'Users', rv)

    def test_users_view_manage(self: t.Self, app: Flask, client: FlaskClient) -> None:
        email = 'user2@example.test'
        authenticate(client, email)
        rv = client.get('/users')
        self.assertStatus(rv, 403)
        self.assertInResponse(html_test_strings['title'] % b'Error', rv)

    def test_user_view_admin(self: t.Self, app: Flask, client: FlaskClient) -> None:
        email = 'user1@example.test'
        authenticate(client, email)
        rv = client.get('/user?id=1')
        self.assertStatus(rv, 200)
        self.assertInResponse(html_test_strings['title'] % b'View User', rv)

    def test_user_create_view_admin(self: t.Self, app: Flask, client: FlaskClient) -> None:
        email = 'user1@example.test'
        authenticate(client, email)
        rv = client.get('/user')
        self.assertStatus(rv, 200)
        self.assertInResponse(html_test_strings['title'] % b'New User', rv)


class TagViewClientTest(AppClientTestBase):
    def test_tags_view_manage(self: t.Self, app: Flask, client: FlaskClient) -> None:
        email = 'user2@example.test'
        authenticate(client, email)
        rv = client.get('/tags')
        self.assertStatus(rv, 200)
        self.assertInResponse(html_test_strings['title'] % b'Tags', rv)
        self.assertInResponse(b'deleted_record', rv)

    def test_tags_view_user(self: t.Self, app: Flask, client: FlaskClient) -> None:
        email = 'user3@example.test'
        authenticate(client, email)
        rv = client.get('/tags')
        self.assertStatus(rv, 200)
        self.assertInResponse(html_test_strings['title'] % b'Tags', rv)
        self.assertNotIn(b'deleted_record', rv.data)

    def test_tag_view_manage(self: t.Self, app: Flask, client: FlaskClient) -> None:
        email = 'user2@example.test'
        tag = models.Tag(name='tag', user_id=2)
        models.db.session.add(tag)
        models.db.session.commit()
        authenticate(client, email)
        rv = client.get('/tag?id=%i' % tag.id)
        self.assertStatus(rv, 200)
        self.assertInResponse(html_test_strings['title'] % b'View Tag', rv)

    def test_tag_view_user(self: t.Self, app: Flask, client: FlaskClient) -> None:
        email = 'user3@example.test'
        authenticate(client, email)
        tag = models.Tag(name='tag', user_id=3)
        models.db.session.add(tag)
        models.db.session.commit()
        rv = client.get('/tag?id=%i' % tag.id)
        self.assertStatus(rv, 200)
        self.assertInResponse(html_test_strings['title'] % b'View Tag', rv)

    def test_tag_view_user_others_tag(self: t.Self, app: Flask, client: FlaskClient) -> None:
        email = 'user3@example.test'
        authenticate(client, email)
        tag = models.Tag(name='tag', user_id=1)
        models.db.session.add(tag)
        models.db.session.commit()
        rv = client.get('/tag?id=%i' % tag.id)
        self.assertStatus(rv, 404)
        self.assertInResponse(html_test_strings['title'] % b'Error', rv)

    def test_tag_create_view_manage(self: t.Self, app: Flask, client: FlaskClient) -> None:
        email = 'user2@example.test'
        authenticate(client, email)
        rv = client.get('/tag')
        self.assertStatus(rv, 200)
        self.assertInResponse(html_test_strings['title'] % b'New Tag', rv)

    def test_tag_create_view_user(self: t.Self, app: Flask, client: FlaskClient) -> None:
        email = 'user3@example.test'
        authenticate(client, email)
        rv = client.get('/tag')
        self.assertStatus(rv, 200)
        self.assertInResponse(html_test_strings['title'] % b'New Tag', rv)

    def test_tag_create_view_post_user(self: t.Self, app: Flask, client: FlaskClient) -> None:
        email = 'user3@example.test'
        authenticate(client, email)
        rv = client.post('/tag', data={'Name': 'tag', 'Create': 'Create'})
        self.assertStatus(rv, 200)
        self.assertInResponse(html_test_strings['title'] % b'View Tag', rv)
        self.assertIsInstance(models.Tag.query.filter_by(name='tag').first(), models.Tag)

    def test_tag_view_manage_delete(self: t.Self, app: Flask, client: FlaskClient) -> None:
        email = 'user2@example.test'
        tag = models.Tag(name='tag', user_id=2)
        models.db.session.add(tag)
        models.db.session.commit()
        id = tag.id
        authenticate(client, email)
        rv = client.get('/tag?id=%i' % tag.id)
        self.assertStatus(rv, 200)
        self.assertInResponse(html_test_strings['title'] % b'View Tag', rv)
        rv = client.post('/tag?id=%i' % tag.id, data={'Delete': 'Delete'})
        self.assertStatus(rv, 302)
        self.assertLocationHeader(rv, '/tags')
        self.assertIsNotNone(models.Tag.query.filter_by(id=id).execution_options(include_deleted=True).first())

    def test_tag_view_user_delete(self: t.Self, app: Flask, client: FlaskClient) -> None:
        email = 'user3@example.test'
        tag = models.Tag(name='tag', user_id=3)
        models.db.session.add(tag)
        models.db.session.commit()
        id = tag.id
        authenticate(client, email)
        rv = client.get('/tag?id=%i' % tag.id)
        self.assertStatus(rv, 200)
        self.assertInResponse(html_test_strings['title'] % b'View Tag', rv)
        rv = client.post('/tag?id=%i' % tag.id, data={'Delete': 'Delete'})
        self.assertStatus(rv, 302)
        self.assertLocationHeader(rv, '/tags')
        self.assertIsNotNone(models.Tag.query.filter_by(id=id).execution_options(include_deleted=True).first())

    def test_tag_view_user_delete_others_tag(self: t.Self, app: Flask, client: FlaskClient) -> None:
        email = 'user3@example.test'
        tag = models.Tag(name='tag', user_id=2)
        models.db.session.add(tag)
        models.db.session.commit()
        authenticate(client, email)
        rv = client.post('/tag?id=%i' % tag.id, data={'Delete': 'Delete'})
        self.assertStatus(rv, 404)
        self.assertIsNone(tag.deleted_at)

    def test_tag_view_user_edit(self: t.Self, app: Flask, client: FlaskClient) -> None:
        email = 'user3@example.test'
        tag = models.Tag(name='tag', user_id=3)
        models.db.session.add(tag)
        models.db.session.commit()
        authenticate(client, email)
        rv = client.get('/tag?id=%i' % tag.id)
        self.assertStatus(rv, 200)
        self.assertInResponse(html_test_strings['title'] % b'View Tag', rv)
        rv = client.post('/tag?id=%i' % tag.id, data={'Edit': 'Edit'})
        self.assertStatus(rv, 200)
        self.assertInResponse(html_test_strings['title'] % b'Edit Tag', rv)

    def test_tag_view_user_edit_others_tag(self: t.Self, app: Flask, client: FlaskClient) -> None:
        email = 'user3@example.test'
        tag = models.Tag(name='tag', user_id=2)
        models.db.session.add(tag)
        models.db.session.commit()
        authenticate(client, email)
        rv = client.post('/tag?id=%i' % tag.id, data={'Edit': 'Edit'})
        self.assertStatus(rv, 404)

    def test_tag_view_user_update(self: t.Self, app: Flask, client: FlaskClient) -> None:
        email = 'user3@example.test'
        tag = models.Tag(name='tag', user_id=3)
        models.db.session.add(tag)
        models.db.session.commit()
        authenticate(client, email)
        self.assertIsNone(tag.updated_at)
        rv = client.post('/tag?id=%i' % tag.id, data={'Update': 'Update', 'Name': 'tag2'})
        self.assertStatus(rv, 200)
        self.assertInResponse(html_test_strings['title'] % b'View Tag', rv)

        self.assertIsNotNone(tag.updated_at)

    def test_tag_view_user_update_others_tag(self: t.Self, app: Flask, client: FlaskClient) -> None:
        email = 'user3@example.test'
        tag = models.Tag(name='tag', user_id=2)
        models.db.session.add(tag)
        models.db.session.commit()
        authenticate(client, email)
        self.assertIsNone(tag.updated_at)
        rv = client.post('/tag?id=%i' % tag.id, data={'Update': 'Update', 'Name': 'tag2'})
        self.assertStatus(rv, 404)
        self.assertIsNone(tag.updated_at)

    def test_tag_view_manage_undelete(self: t.Self, app: Flask, client: FlaskClient) -> None:
        email = 'user2@example.test'
        tag = models.Tag(name='tag', user_id=2)
        models.db.session.add(tag)
        models.db.session.commit()
        authenticate(client, email)
        id = tag.id
        tag.delete()
        models.db.session.add(tag)
        models.db.session.commit()
        rv = client.post('/tag?id=%i' % id, data={'Undelete': 'Undelete'})
        self.assertStatus(rv, 200)
        self.assertInResponse(html_test_strings['title'] % b'View Tag', rv)
        self.assertIsNotNone(models.Tag.query.filter_by(id=id).first())

    def test_tag_view_manage_undelete_others_tag(self: t.Self, app: Flask, client: FlaskClient) -> None:
        email = 'user2@example.test'
        tag = models.Tag(name='tag', user_id=3)
        models.db.session.add(tag)
        models.db.session.commit()
        authenticate(client, email)
        id = tag.id
        tag.delete()
        models.db.session.add(tag)
        models.db.session.commit()
        rv = client.post('/tag?id=%i' % id, data={'Undelete': 'Undelete'})
        self.assertStatus(rv, 404)
        self.assertIsNone(models.Tag.query.filter_by(id=id).first())

    def test_tag_view_user_undelete(self: t.Self, app: Flask, client: FlaskClient) -> None:
        email = 'user3@example.test'
        tag = models.Tag(name='tag', user_id=3)
        models.db.session.add(tag)
        models.db.session.commit()
        authenticate(client, email)
        id = tag.id
        tag.delete()
        models.db.session.add(tag)
        models.db.session.commit()
        rv = client.post('/tag?id=%i' % id, data={'Undelete': 'Undelete'})
        self.assertStatus(rv, 404)
        self.assertIsNone(models.Tag.query.filter_by(id=id).first())


class EntryViewClientTest(AppClientTestBase):
    def test_entries_view_manage(self: t.Self, app: Flask, client: FlaskClient) -> None:
        email = 'user2@example.test'
        authenticate(client, email)
        rv = client.get('/entries')
        self.assertStatus(rv, 200)
        self.assertInResponse(html_test_strings['title'] % b'Entries', rv)
        self.assertInResponse(b'deleted_record', rv)

    def test_entries_view_user(self: t.Self, app: Flask, client: FlaskClient) -> None:
        email = 'user3@example.test'
        authenticate(client, email)
        rv = client.get('/entries')
        self.assertStatus(rv, 200)
        self.assertInResponse(html_test_strings['title'] % b'Entries', rv)
        self.assertNotIn(b'deleted_record', rv.data)

    def test_entry_view_manage(self: t.Self, app: Flask, client: FlaskClient) -> None:
        email = 'user2@example.test'
        entry = models.Entry()
        entry.title = 'entry'
        entry.content = 'lorem ipsum'
        entry.user_id = 2
        models.db.session.add(entry)
        models.db.session.commit()
        authenticate(client, email)
        rv = client.get('/entry?id=%i' % entry.id)
        self.assertStatus(rv, 200)
        self.assertInResponse(html_test_strings['title'] % b'View Entry', rv)

    def test_entry_view_user(self: t.Self, app: Flask, client: FlaskClient) -> None:
        email = 'user3@example.test'
        authenticate(client, email)
        entry = models.Entry()
        entry.title = 'entry'
        entry.content = 'lorem ipsum'
        entry.user_id = 3
        models.db.session.add(entry)
        models.db.session.commit()
        rv = client.get('/entry?id=%i' % entry.id)
        self.assertStatus(rv, 200)
        self.assertInResponse(html_test_strings['title'] % b'View Entry', rv)

    def test_entry_view_user_others_entry(self: t.Self, app: Flask, client: FlaskClient) -> None:
        email = 'user3@example.test'
        authenticate(client, email)
        entry = models.Entry()
        entry.title = 'entry'
        entry.content = 'lorem ipsum'
        entry.user_id = 1
        models.db.session.add(entry)
        models.db.session.commit()
        rv = client.get('/entry?id=%i' % entry.id)
        self.assertStatus(rv, 404)
        self.assertInResponse(html_test_strings['title'] % b'Error', rv)

    def test_entry_create_view_manage(self: t.Self, app: Flask, client: FlaskClient) -> None:
        email = 'user2@example.test'
        authenticate(client, email)
        rv = client.get('/entry')
        self.assertStatus(rv, 200)
        self.assertInResponse(html_test_strings['title'] % b'New Entry', rv)

    def test_entry_create_view_user(self: t.Self, app: Flask, client: FlaskClient) -> None:
        email = 'user3@example.test'
        authenticate(client, email)
        rv = client.get('/entry')
        self.assertStatus(rv, 200)
        self.assertInResponse(html_test_strings['title'] % b'New Entry', rv)

    def test_entry_create_view_post_user(self: t.Self, app: Flask, client: FlaskClient) -> None:
        email = 'user3@example.test'
        content = 'lorem ipsum'
        authenticate(client, email)
        rv = client.post('/entry', data={'Title': 'entry 1', 'Body': content, 'Tags': '', 'Create': 'Create'})
        self.assertStatus(rv, 200)
        self.assertInResponse(html_test_strings['title'] % b'View Entry', rv)
        entry = models.Entry.query.first()
        self.assertIsInstance(entry, models.Entry)
        self.assertEqual(entry.content, content)
        self.assertNotEqual(entry.content, entry._data)

    def test_entry_view_manage_delete(self: t.Self, app: Flask, client: FlaskClient) -> None:
        email = 'user2@example.test'
        entry = models.Entry()
        entry.title = 'entry'
        entry.content = 'lorem ipsum'
        entry.user_id = 2
        models.db.session.add(entry)
        models.db.session.commit()
        id = entry.id
        authenticate(client, email)
        rv = client.get('/entry?id=%i' % entry.id)
        self.assertStatus(rv, 200)
        self.assertInResponse(html_test_strings['title'] % b'View Entry', rv)
        rv = client.post('/entry?id=%i' % entry.id, data={'Delete': 'Delete'})
        self.assertStatus(rv, 302)
        self.assertLocationHeader(rv, '/entries')
        self.assertIsNotNone(models.Entry.query.filter_by(id=id).execution_options(include_deleted=True).first())

    def test_entry_view_user_delete(self: t.Self, app: Flask, client: FlaskClient) -> None:
        email = 'user3@example.test'
        entry = models.Entry()
        entry.title = 'entry'
        entry.content = 'lorem ipsum'
        entry.user_id = 3
        models.db.session.add(entry)
        models.db.session.commit()
        id = entry.id
        authenticate(client, email)
        rv = client.get('/entry?id=%i' % entry.id)
        self.assertStatus(rv, 200)
        self.assertInResponse(html_test_strings['title'] % b'View Entry', rv)
        rv = client.post('/entry?id=%i' % entry.id, data={'Delete': 'Delete'})
        self.assertStatus(rv, 302)
        self.assertLocationHeader(rv, '/entries')
        self.assertIsNotNone(models.Entry.query.filter_by(id=id).execution_options(include_deleted=True).first())

    def test_entry_view_user_delete_others_entry(self: t.Self, app: Flask, client: FlaskClient) -> None:
        email = 'user3@example.test'
        entry = models.Entry()
        entry.title = 'entry'
        entry.content = 'lorem ipsum'
        entry.user_id = 2
        models.db.session.add(entry)
        models.db.session.commit()
        authenticate(client, email)
        rv = client.post('/entry?id=%i' % entry.id, data={'Delete': 'Delete'})
        self.assertStatus(rv, 404)
        self.assertIsNone(entry.deleted_at)

    def test_entry_view_user_edit(self: t.Self, app: Flask, client: FlaskClient) -> None:
        email = 'user3@example.test'
        entry = models.Entry()
        entry.title = 'entry'
        entry.content = 'lorem ipsum'
        entry.user_id = 3
        models.db.session.add(entry)
        models.db.session.commit()
        authenticate(client, email)
        rv = client.get('/entry?id=%i' % entry.id)
        self.assertStatus(rv, 200)
        self.assertInResponse(html_test_strings['title'] % b'View Entry', rv)
        rv = client.post('/entry?id=%i' % entry.id, data={'Edit': 'Edit'})
        self.assertStatus(rv, 200)
        self.assertInResponse(html_test_strings['title'] % b'Edit Entry', rv)

    def test_entry_view_user_edit_others_entry(self: t.Self, app: Flask, client: FlaskClient) -> None:
        email = 'user3@example.test'
        entry = models.Entry()
        entry.title = 'entry'
        entry.content = 'lorem ipsum'
        entry.user_id = 2
        models.db.session.add(entry)
        models.db.session.commit()
        authenticate(client, email)
        rv = client.post('/entry?id=%i' % entry.id, data={'Edit': 'Edit'})
        self.assertStatus(rv, 404)

    def test_entry_view_user_update(self: t.Self, app: Flask, client: FlaskClient) -> None:
        email = 'user3@example.test'
        entry = models.Entry()
        entry.title = 'entry'
        entry.content = 'lorem ipsum'
        entry.user_id = 3
        models.db.session.add(entry)
        models.db.session.commit()
        authenticate(client, email)
        self.assertIsNone(entry.updated_at)
        rv = client.post('/entry?id=%i' % entry.id, data={'Update': 'Update', 'Title': 'entry2'})
        self.assertStatus(rv, 200)
        self.assertInResponse(html_test_strings['title'] % b'View Entry', rv)

        self.assertIsNotNone(entry.updated_at)

    def test_entry_view_user_update_others_entry(self: t.Self, app: Flask, client: FlaskClient) -> None:
        email = 'user3@example.test'
        entry = models.Entry()
        entry.title = 'entry'
        entry.content = 'lorem ipsum'
        entry.user_id = 2
        models.db.session.add(entry)
        models.db.session.commit()
        authenticate(client, email)
        self.assertIsNone(entry.updated_at)
        rv = client.post('/entry?id=%i' % entry.id, data={'Update': 'Update', 'Name': 'entry2'})
        self.assertStatus(rv, 404)
        self.assertIsNone(entry.updated_at)

    def test_entry_view_manage_undelete(self: t.Self, app: Flask, client: FlaskClient) -> None:
        email = 'user2@example.test'
        entry = models.Entry()
        entry.title = 'entry'
        entry.content = 'lorem ipsum'
        entry.user_id = 2
        models.db.session.add(entry)
        models.db.session.commit()
        authenticate(client, email)
        id = entry.id
        entry.delete()
        models.db.session.add(entry)
        models.db.session.commit()
        rv = client.post('/entry?id=%i' % id, data={'Undelete': 'Undelete'})
        self.assertStatus(rv, 200)
        self.assertInResponse(html_test_strings['title'] % b'View Entry', rv)
        self.assertIsNotNone(models.Entry.query.filter_by(id=id).first())

    def test_entry_view_manage_undelete_others_entry(self: t.Self, app: Flask, client: FlaskClient) -> None:
        email = 'user2@example.test'
        entry = models.Entry()
        entry.title = 'entry'
        entry.content = 'lorem ipsum'
        entry.user_id = 3
        models.db.session.add(entry)
        models.db.session.commit()
        authenticate(client, email)
        id = entry.id
        entry.delete()
        models.db.session.add(entry)
        models.db.session.commit()
        rv = client.post('/entry?id=%i' % id, data={'Undelete': 'Undelete'})
        self.assertStatus(rv, 404)
        self.assertIsNone(models.Entry.query.filter_by(id=id).first())

    def test_entry_view_user_undelete(self: t.Self, app: Flask, client: FlaskClient) -> None:
        email = 'user3@example.test'
        entry = models.Entry()
        entry.title = 'entry'
        entry.content = 'lorem ipsum'
        entry.user_id = 3
        models.db.session.add(entry)
        models.db.session.commit()
        authenticate(client, email)
        id = entry.id
        entry.delete()
        models.db.session.add(entry)
        models.db.session.commit()
        rv = client.post('/entry?id=%i' % id, data={'Undelete': 'Undelete'})
        self.assertStatus(rv, 404)
        self.assertIsNone(models.Entry.query.filter_by(id=id).first())
