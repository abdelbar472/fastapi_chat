from fastapi import FastAPI
from routers import messages, auth

app = FastAPI()

app.include_router(messages.router, prefix="/messages", tags=["messages"])
app.include_router(auth.router, prefix="/auth", tags=["auth"])