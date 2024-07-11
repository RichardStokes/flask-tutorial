import pytest
from flaskr.db import get_db

class TestComment:
    def test_create_comment(self, app, client, auth):
        auth.login()
        with app.app_context():
            db = get_db()
            inital_count = db.execute("""SELECT * FROM comment;""").fetchall()
            response = client.post("/1/comments/", data={
                'body': 'This is a test, this is only a test'
            })
            results = db.execute("""SELECT * FROM comment;""").fetchall()

        assert response.status_code == 302
        assert len(inital_count) == 0
        assert len(results) == 1

        
