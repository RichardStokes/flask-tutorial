import pytest
from flaskr.db import get_db
from flask import g


def test_index(client, auth):
	response = client.get('/')
	assert b"Log In" in response.data
	assert b"Register" in response.data

	auth.login()
	response = client.get('/')
	assert b"Log Out" in response.data
	assert b"test title" in response.data
	assert b"by test on 2018-01-01" in response.data
	assert b"test\nbody" in response.data
	assert b'href="/1/update' in response.data


@pytest.mark.parametrize('path', (
	'/create',
	'/1/update',
	'/1/delete',
))
def test_login_required(client, path):
	response = client.post(path)
	assert response.headers['Location'] == "/auth/login"


def test_author_required(app, client, auth):
	with app.app_context():
		db = get_db()
		db.execute('UPDATE post SET author_id = 2 WHERE id = 1')
		db.commit()

	auth.login()
	assert client.post('/1/update').status_code == 403
	assert client.post('/1/delete').status_code == 403
	assert b'href="/1/update' not in client.get('/').data


@pytest.mark.parametrize('path', (
	'/2/update',
	'/2/delete',
))
def test_exists_required(client, auth, path):
	auth.login()
	assert client.post(path).status_code == 404


def test_create(client, auth, app):
	auth.login()
	assert client.get('/create').status_code == 200
	client.post('/create', data={'title': 'created', 'body': ''})

	with app.app_context():
		db = get_db()
		count = db.execute('SELECT COUNT(id) FROM post').fetchone()['COUNT(id)']
		assert count == 2


def test_update(client, auth, app):
	auth.login()
	assert client.get('/1/update').status_code == 200
	client.post('/1/update', data={'title': 'updated', 'body': ''})

	with app.app_context():
		db = get_db()
		post = db.execute('SELECT * FROM post WHERE id = 1').fetchone()
		assert post['title'] == 'updated'


@pytest.mark.parametrize('path', (
		'/create',
		'/1/update',
))
def test_create_update_validate(client, auth, path):
	auth.login()
	response = client.post(path, data={'title': '', 'body': ''})
	assert b'Title is required.' in response.data


def test_delete(client, auth, app):
	auth.login()
	response = client.post('/1/delete')
	assert response.headers["Location"] == "/"

	with app.app_context():
		db = get_db()
		post = db.execute('SELECT * FROM post WHERE id = 1').fetchone()
		assert post is None


def test_show(client):
	response = client.get('/1/')
	assert response.status_code == 200
	assert b'test' in response.data

def test_like(client, auth, app):
	with app.app_context():
		db = get_db()
		
		# assert that there are no likes to begin with
		like = db.execute('SELECT * FROM like').fetchone()
		assert like is None

		# assert that liking a post redirects you to that post's page
		auth.login(username='other', password='other')
		response = client.post('/1/like')
		assert response.headers["Location"] == "/1/"

		# assert that a post has in fact been created by hitting that route
		like = db.execute('SELECT * FROM like;').fetchone()
		assert like is not None
		assert like['user_id'] == 2
		assert like['post_id'] == 1

		# assert that hitting the route a second time will delete the post
		response = client.post('/1/like')
		like = db.execute('SELECT * FROM like;').fetchone()
		assert like is None

