from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from schema import models
from database import get_db
from crud import entrycrud
from utilities import update_recurring_entries, get_current_user


router = APIRouter(
    prefix='/entries',
    tags=['Entries']
)

# List of allowed categories
categories = ['Income', 'Housing', 'Food', 'Personal',
            'Entertainment', 'Transportation', 'Other Expense']


# Route to create a new database entry, by current user
@router.post("/", response_model=models.Entry)
def create_entry(
    entry: models.EntryBase, db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)    
):
    return entrycrud.entry_create(db, entry, current_user.id)


# Route to edit entry (by entry id) of current user
@router.put("/{id}", response_model=models.EntryBase)
def update_entry(
    id: int, entry: models.EntryBase, db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    return entrycrud.entry_update(db, entry, id, current_user.id)


# Route to delete entry by entry id
@router.delete("/{id}")
def delete_entry(
    id: int, db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
    ):
    return entrycrud.entry_delete(db, id, current_user.id)


# Route to get overview of month with category summaries and net
@router.get("/month/")
def month_overview(
    year: int = datetime.now().year, month: int = datetime.now().month,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    amounts = {}
    # Iterates over all categories and adds non empty amounts to dict
    for category in categories:
        amount = 0
        entries = entrycrud.get_month_entries(current_user.id, year, month, db, category)
        if entries:
            for entry in entries:
                amount += entry.amount
            amounts[category] = amount
    # Calculate net expenditure
    amounts['Net'] = sum(x for x in amounts.values())
    return amounts


# Route to get overview of year with category summaries and net
@router.get("/year/{year}/")
def year_overview(
    year: int, db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
    ):
    amounts = {}
    # Iterates over all categories and adds non empty amounts to dict
    for category in categories:
        amount = 0
        entries = entrycrud.get_year_entries(current_user.id, year, db, category)
        if entries:
            amount = sum(x[0] for x in entries)
            amounts[category] = amount
    # Calculate net expenditure
    amounts['Net'] = sum(x for x in amounts.values())
    return amounts


# Gets list of all entries in a month
@router.get("/month/{month}/", response_model=List[models.Entry])
def month_entries(
    month: int, year: int = datetime.now().year, db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    return entrycrud.get_month_entries(current_user.id, year, month, db)


# Gets list of all entries in a category for given month
@router.get("/month/{month}/{category}/", response_model=List[models.Entry])
def month_entries_by_category(
    category: str, month: int, year: int = datetime.now().year,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    return entrycrud.get_month_entries(current_user.id, year, month, db, category)