from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from schema import models
from crud.usercrud import create_user, get_user, get_user_by_email
from database import get_db
from utilities import get_current_user, authenticate_user, create_access_token, update_recurring_entries


router = APIRouter(
    prefix='/users',
    tags=['Users']
)


# Login route, creates access token for user
@router.post("/login", response_model=models.Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(),
                        db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    # Exception if authentication fails
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user.email})
    # Auto create recurring entries up to today
    update_recurring_entries(user.id, db)
    return {"access_token": access_token, "token_type": "bearer"}


# Route for new user
@router.post('/', response_model=models.User)
def new_user(user: models.UserCreate, db: Session = Depends(get_db)):
    db_user = get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return create_user(db, user)


# Route to access user info (really just id)
@router.get('/me', response_model=models.User)
def get_me(current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    return current_user