from flask import Blueprint, request, g, redirect, url_for
from flaskr.auth import login_required
from flaskr.db import get_db

bp = Blueprint('comment', __name__)

@bp.route('/<int:id>/comments/', methods=('POST',))
@login_required
def create_comment(id):
    comment_body = request.form['body']
    author_id = g.user['id']
    
    db = get_db()

    db.execute("""
        INSERT INTO comment (body, author_id, post_id)
        VALUES (?, ?, ?)
    """, (comment_body, author_id, id))
    db.commit()
    return redirect(url_for('blog.show', id=id))