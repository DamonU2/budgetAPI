from typing import List, Optional
from enum import Enum
from datetime import date, datetime
from pydantic import BaseModel


# List of allowed frequency entries
class Frequency(str, Enum):
    onetime = 'One time'
    weekly = 'Weekly'
    biweekly = 'Biweekly'
    twice = 'Twice a month'
    monthly = 'Monthly'
    yearly = 'Yearly'


# # List of allowed category entries
class Category(str, Enum):
    income = 'Income'
    housing = 'Housing'
    food = 'Food'
    personal = 'Personal'
    entertainment = 'Entertainment'
    transportation = 'Transportation'
    other = 'Other Expense'


class EntryBase(BaseModel):
    name: str
    amount: float
    frequency: Frequency # Limits entries to list above
    category: Category # Limits entries to list above
    entry_date: Optional[date] = None


class Entry(EntryBase):
    id: int
    user_id: int

    class Config:
        orm_mode = True


class UserBase(BaseModel):
    email: str


class UserCreate(UserBase):
    password: str


class User(UserBase):
    id: int

    class Config:
        orm_mode = True


class UserInDB(User):
    hashed_password: str


# Model for authorization token
class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: Optional[str] = None