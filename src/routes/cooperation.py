from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse

from src.schemas.cooperation import CooperationModel
from src.services.cooperation import email_service


router = APIRouter(prefix="/cooperation", tags=["cooperation"])


@router.post("/", response_class=JSONResponse)
async def send_email(body: CooperationModel = Depends()):
    try:
        await email_service.send_email(body.name, body.email, body.phone_number, body.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send email. Error: {str(e)}")

    return JSONResponse(content={"message": "Email sent successfully!"})
