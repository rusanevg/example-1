import click

from app.flask_app import db, usersbp
from models.user import User
from utils.api_utils import generate_password_hash
from utils.partition_auth_history import create_partition_year


@usersbp.cli.command("create_superuser")
@click.argument("username")
@click.argument("password")
def create_superuser(username, password):
    pwd_hash, salt = generate_password_hash(password)
    db.session.add(User(username=username, password=pwd_hash, salt=salt, is_superuser=True))
    db.session.commit()
    print(f"Superuser with name {username} created")


@usersbp.cli.command("create_partition_year")
@click.argument("year")
def create_db(year):
    with db.engine.connect() as con:
        create_partition_year(connection=con, year=year)
        con.close()
