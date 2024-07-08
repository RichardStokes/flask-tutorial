# import sqlite3
from faker import Faker


def build_query(table_name, data = {}):
    vals = zip(*data.values())
    str_vals = ', '.join(map(str, vals))
    col_names = tuple(data.keys())
    query = f"INSERT INTO {table_name} {col_names} VALUES {str_vals};"
    return query

def seed_data():
    fake = Faker()
    Faker.seed(0)

    data = {
        'user': {
            'username': (fake.name() for _ in range(10)),
            'password': ('pwd' for _ in range(10))
        },
        'post': {
            'author_id': range(1,11),
            'title': (fake.sentence() for _ in range(10)),
            'body': (fake.paragraph() for _ in range(10))
        },
        'like': {
            'user_id': (range(1,6)),
            'post_id': (range(6,11))
        },
        'comment': {
            'author_id': range(1,6),
            'post_id': (range(6,11)),
            'body': (fake.paragraph() for _ in range(10))
        }
    }

    return data





