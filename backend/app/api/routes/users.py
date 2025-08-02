from fastapi import APIRouter, Depends
from app.utils.dependencies import get_current_user

router = APIRouter()

@router.get("/")
def get_users(current_user = Depends(get_current_user)):
    return {"message": "Authorized!", "user_id": current_user["user_id"]}
