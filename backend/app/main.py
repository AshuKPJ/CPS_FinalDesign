# backend/app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.endpoints import auth, users, submit, dashboards, campaigns, logs, user_contact_profile

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000","http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router,       prefix="/auth", tags=["auth"])
app.include_router(users.router)  # users router already carries prefix="/users"
app.include_router(submit.router,     prefix="/submit", tags=["submit"])
app.include_router(dashboards.router, prefix="/dashboards", tags=["dashboards"])
app.include_router(campaigns.router,  prefix="/campaigns", tags=["campaigns"])
app.include_router(logs.router,       prefix="/logs", tags=["logs"])
app.include_router(user_contact_profile.router, prefix="/usercontactprofile", tags=["user-contact-profile"])
