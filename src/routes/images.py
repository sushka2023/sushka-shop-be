from fastapi import Depends, HTTPException, status, Path, APIRouter, Query, UploadFile, File, Form
from sqlalchemy.orm import Session
from pydantic import ValidationError

from src.database.db import get_db
from src.database.models import User, Role, ImageType
from src.schemas.images import ImageModel, ImageResponse
from src.repository import images as repository_images
from src.services.cloud_image import CloudImage
from src.services.auth import auth_service
from src.services.roles import RoleAccess


router = APIRouter(prefix="/images", tags=['images'])

allowed_operation_admin = RoleAccess([Role.admin])
allowed_operation_admin_moderator = RoleAccess([Role.admin, Role.moderator])


@router.post("/create_img_product", response_model=ImageResponse, dependencies=[Depends(allowed_operation_admin_moderator)],
             status_code=status.HTTP_201_CREATED)
async def create_image(description: str = Form(),
                       image_file: UploadFile = File(),
                       db: Session = Depends(get_db)):

    try:
        body = ImageModel(description=description, image_type=ImageType.product)
    except ValidationError:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="UNPROCESSABLE_ENTITY")
    file_name = CloudImage.generate_name_image()
    CloudImage.upload(image_file.file, file_name, overwrite=False)
    image_url = CloudImage.get_url_for_image(file_name)
    image = await repository_images.create(body, image_url, db)
    transformation_image = CloudImage.get_transformation_image(image_url, "product")
    image.image_url = transformation_image
    return image
