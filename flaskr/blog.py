from flask import (
	Blueprint, flash, g, redirect, render_template, request, url_for
)

from werkzeug.exceptions import abort

from flaskr.auth import login_required
from flaskr.db import get_db

bp = Blueprint('blog', __name__)

@bp.route('/')
def index():
	db = get_db()
	posts = db.execute("""
		SELECT p.id, title, body, created, author_id, username 
		FROM post p JOIN user u 
		ON p.author_id = u.id ORDER BY created DESC
		"""
	).fetchall()
	return render_template('blog/index.html', posts=posts)

@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
	if request.method == 'POST':
		title = request.form['title']
		body = request.form['body']
		author_id = g.user['id']
		error = None

		if not title:
			error = 'Title is required.'
		
		if error is not None:
			flash(error)
		else:
			db = get_db()
			db.execute('INSERT INTO post (author_id, title, body) VALUES (?, ?, ?)',
				(author_id, title, body))
			db.commit()
			return redirect(url_for('blog.index'))

	return render_template('blog/create.html')

def get_post(id, check_author=True):
	db = get_db()
	post = db.execute("""
		SELECT p.id, title, body, created, author_id, username
		FROM post p JOIN user u ON p.author_id = u.id 
		WHERE p.id = ?
		""", (id,)
	).fetchone()

	likes = db.execute("""
							SELECT user_id
							FROM like
							WHERE post_id = ?
							""", (id,)
	).fetchall()
	if post:
		post['likes'] = (like['user_id'] for like in likes)

	if post is None:
		abort(404, f'Post id {id} doesn\'t exist')

	if check_author and post['author_id'] != g.user['id']:
		abort(403)

	return post


@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
	post = get_post(id)

	if request.method == 'POST':
		title = request.form['title']
		body = request.form['body']
		error = None

		if not title:
			error = 'Title is required.'

		if error is not None:
			flash(error)
		else:
			db = get_db()
			db.execute("""
				UPDATE post SET title = ?, body = ?
				WHERE id = ?""",
				(title, body, id)
			)
			db.commit()
			return redirect(url_for('blog.index'))
			
	return render_template('blog/update.html', post=post)

@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
	get_post(id)
	db = get_db()
	db.execute("""
		DELETE FROM post
		WHERE id = ?
		""", (id,)
	)
	db.commit()
	return redirect(url_for('blog.index'))


@bp.route('/<int:id>/', methods=('GET',))
def show(id):
	post = get_post(id, check_author=False)
	liked = g.user['id'] in post['likes'] if g.user else None
	return render_template('blog/show.html', post=post, liked=liked)
		

@bp.route('/<int:id>/like', methods=('POST',))
@login_required
def like(id):
	post = get_post(id, check_author=False)
	user = g.user
	db = get_db()
	liked = user['id'] in post['likes']
	like_vals = (user['id'], post['id'])
	
	if liked:
		db.execute("""
			 DELETE FROM like
			 WHERE user_id = ?
			 AND post_id = ?"""
		, like_vals
		)
		db.commit()
	else:
		db.execute("""
			 INSERT INTO like(user_id, post_id)
			 VALUES (?, ?)
			 """, like_vals
		)
		db.commit()
	return redirect(url_for('blog.show', id=post['id']))

