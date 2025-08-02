from fastapi import APIRouter

router = APIRouter()

@router.get("/ping", tags=["Health"])
def ping():
    print("✅ /ping called")
    return {"status": "ok"}
