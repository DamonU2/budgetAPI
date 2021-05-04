from datetime import date, datetime, timedelta
from sqlalchemy import func
from sqlalchemy.orm import Session
from dateutil.relativedelta import relativedelta
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from dotenv import load_dotenv
import os
from jose import JWTError, jwt

from schema import models, tables
from crud.entrycrud import entry_create
from crud.usercrud import get_user_by_email
from database import get_db


load_dotenv()
ACCESS_TOKEN_EXPIRE_MINUTES = 90
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/login")


def authenticate_user(db, email: str, password: str):
    user = get_user_by_email(db, email)
    if not user:
        return False
    if not pwd_context.verify(password, user.hashed_password):
        return False
    return user


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, os.getenv('SECRET_KEY'), algorithm=os.getenv('ALGORITHM'))
    return encoded_jwt


# Gets the current user from the authorization token
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, os.getenv('SECRET_KEY'), algorithms=os.getenv('ALGORITHM'))
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = models.TokenData(email=email)
    except JWTError:
        raise credentials_exception
    # Gets full user info from email in authorization token
    user = get_user_by_email(db, email=token_data.email)
    if user is None:
        raise credentials_exception
    return user


# Generates database entries for recurring items, up to today
def update_recurring_entries(user_id, db):
    today = date.today()

    # Dictionary of frequencies with time frames to be incremented
    frequencies = {'Weekly': (1, 0, 0), 'Biweekly': (2, 0, 0),
        'Monthly': (0, 1, 0), 'Yearly': (0, 0, 1)}
    
    # Iterates through dict to create entries
    for timeframe, adjustment in frequencies.items():
        # Gets most recent entry of each name from each frequencies entries
        recurring_entries = db.query(tables.Entry, func.max(tables.Entry.entry_date)
            ).filter(tables.Entry.user_id == user_id,
            tables.Entry.frequency == timeframe
            ).group_by(tables.Entry.name).all()
        for entry in recurring_entries:
            # Remove initial dictionary key from data
            stripped = entry['Entry']
            # Adjust date by necessary amount
            date_1 = stripped.entry_date + relativedelta(weeks=+adjustment[0],
                months=+adjustment[1], years=+adjustment[2])
            # Create entries as long as date does not exceed today
            while date_1 <= today:
                new_entry = models.EntryBase(
                    name = stripped.name,
                    amount = stripped.amount,
                    frequency = stripped.frequency,
                    category = stripped.category,
                    entry_date = date_1
                )
                entry_create(db, new_entry, user_id)
                # Adjust date again
                date_1 = date_1 + relativedelta(weeks=+adjustment[0],
                    months=+adjustment[1], years=+adjustment[2])
    
    # Seperate process for twice monthly entries
    # Gets most recent entries of each name
    twice_monthly_entries = db.query(tables.Entry, func.max(tables.Entry.entry_date)
            ).filter(tables.Entry.user_id == user_id,
            tables.Entry.frequency == 'Twice a month'
            ).group_by(tables.Entry.name).all()
    for entry in twice_monthly_entries:
        # Remove initial dictionary key from data
        stripped = entry['Entry']
        date_1 = stripped.entry_date
        # Set dates two weeks apart
        if date_1.day >= 15:
            # For date in the second half of the month, set two weeks earlier and one month later
            date_2 = date_1 + relativedelta(days=-14, months=+1)
        else:
            # In the first half of the month set 14 days later
            date_2 = date_1 + relativedelta(days=+14)
        # Adjust initial date forward
        date_1 = date_1 + relativedelta(months=+1)
        # Create entries for each date separately
        for dates in (date_1, date_2):
            while dates <= today:
                new_entry = models.EntryBase(
                    name = stripped.name,
                    amount = stripped.amount,
                    frequency = stripped.frequency,
                    category = stripped.category,
                    entry_date = dates
                )
                entry_create(db, new_entry, user_id)
                dates = dates + relativedelta(months=+1)