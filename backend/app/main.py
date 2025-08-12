from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.endpoints import submit

app = FastAPI(title="CPS Automation API", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 🚀 Register endpoints
app.include_router(submit.router, prefix="/submit", tags=["Form Submission"])


# Route registration
#app.include_router(login.router, tags=["Authentication"])
#app.include_router(user_contact_profile.router, prefix="/usercontactprofile", tags=["User Contact Profile"])
#app.include_router(submit.router, prefix="/submit", tags=["Campaign Submission"])
