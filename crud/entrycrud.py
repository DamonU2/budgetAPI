from sqlalchemy import extract
from fastapi import status, HTTPException

from schema import tables


def get_month_entries(user_id, year, month, db, category=None):
    # Gets all database entries (by category if entered) for current user
    if category:
        return db.query(tables.Entry).filter(tables.Entry.user_id == user_id,
        tables.Entry.category == category,
        (extract('year', tables.Entry.entry_date) == year),
        (extract('month', tables.Entry.entry_date) == month)).all()
    return db.query(tables.Entry).filter(tables.Entry.user_id == user_id,
    (extract('year', tables.Entry.entry_date) == year),
    (extract('month', tables.Entry.entry_date) == month)).all()


def get_year_entries(user_id, year, db, category):
    # Gets entries for entire year by category
    return db.query(tables.Entry.amount).filter(tables.Entry.user_id == user_id,
            tables.Entry.category == category,
            (extract('year', tables.Entry.entry_date) == year)).all()


def entry_create(db, entry, user_id):
    # Create new entry for database
    # For consistency, income entries are positive, all others are negative
    if entry.category != 'Income':
        entry.amount = - abs(entry.amount)
    db_entry = tables.Entry(**entry.dict(), user_id=user_id)
    db.add(db_entry)
    db.commit()
    db.refresh(db_entry)
    return db_entry


def entry_delete(db, entry_id, user_id):
    # Removes database entry
    entry = db.query(tables.Entry).filter(tables.Entry.id == entry_id)
    # Ensure entry exists
    if not entry.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'Entry with id {id} not available')
    # Ensure entry belongs to current user 
    if entry.first().user_id != user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    entry.delete(synchronize_session=False)
    db.commit()
    return 'Deleted'


def entry_update(db, entry, entry_id, user_id):
    # Update an entry
    db_entry = db.query(tables.Entry).filter(tables.Entry.id == entry_id)
    # Ensure entry exists
    if not db_entry.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'Entry with id {entry_id} not available')
    # Ensure entry belongs to current user 
    if db_entry.first().user_id != user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    db_entry.update({'name': entry.name, 'amount': entry.amount,
                    'frequency': entry.frequency, 'category': entry.category,
                    'entry_date': entry.entry_date})
    db.commit()
    return entry