from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def get_campaigns():
    return {"message": "Campaigns endpoint is active"}
