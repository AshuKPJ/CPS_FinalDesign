import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import login
from app.api.endpoints import (
    user_contact_profile,
    submit
)

app = FastAPI(title="CPS Automation API", version="1.0")

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update to specific origins in prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Route registration
app.include_router(login.router, tags=["Authentication"])
app.include_router(user_contact_profile.router, prefix="/usercontactprofile", tags=["User Contact Profile"])
app.include_router(submit.router, prefix="/submit", tags=["Campaign Submission"])
