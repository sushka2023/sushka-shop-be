import logging

from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse

from src.schemas.cooperation import CooperationModel
from src.services.cooperation import email_service
from src.services.validation import validate_phone_number

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/cooperation", tags=["cooperation"])


@router.post("/", response_class=JSONResponse)
async def send_email(body: CooperationModel = Depends()):
    try:
        validate_phone_number(body.phone_number)
        await email_service.send_email(**body.dict())
    except ValueError as ve:
        logger.error(f"Validation error: {str(ve)}")
        return JSONResponse(content={"error": str(ve)}, status_code=422)
    except Exception as e:
        logger.exception(f"An unexpected error occurred: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to send email. Error: {str(e)}")

    return JSONResponse(content={"message": "Email sent successfully!"})
