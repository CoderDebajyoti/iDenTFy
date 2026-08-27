from fastapi import APIRouter
from app.schemas.verification import ModuleStatus

router = APIRouter()

@router.get("/status", response_model=ModuleStatus)
def get_face_status():
    return ModuleStatus(
        module="face-verification",
        status="not_implemented",
        phase=1
    )
