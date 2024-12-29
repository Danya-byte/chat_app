# add_users.py
from app import app, db
from models import User
from getpass import getpass


def add_user():
    with app.app_context():
        username = input("Enter username: ")
        email = input("Enter email: ")
        password = getpass("Enter password: ")
        is_admin = input("Is this user an admin? (yes/no): ").lower() == 'yes'

        user = User.query.filter((User.email == email) | (User.username == username)).first()
        if user:
            print("Email or username already registered")
        else:
            new_user = User(username=username, email=email, is_admin=is_admin)
            new_user.set_password(password)
            db.session.add(new_user)
            db.session.commit()
            print("User added successfully")


if __name__ == "__main__":
    add_user()
