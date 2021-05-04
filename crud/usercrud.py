from schema import tables
from passlib.context import CryptContext


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_user(db, user_id):
    # Gets user info
    return db.query(tables.User).filter(tables.User.id == user_id).first()


def get_user_by_email(db, email):
    # Gets user info using email
    return db.query(tables.User).filter(tables.User.email == email).first()


def create_user(db, user):
    # Creates a new user
    hashed_password = pwd_context.hash(user.password)
    db_user = tables.User(email=user.email, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user