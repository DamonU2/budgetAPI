from fastapi import FastAPI
from database import engine
from schema import tables
from routers import users, entries


tables.Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(users.router)
app.include_router(entries.router)
