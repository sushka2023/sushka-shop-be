from cloudinary import api
from fastapi import Depends, HTTPException, status, APIRouter, UploadFile, File, Form
from sqlalchemy.orm import Session
from pydantic import ValidationError

from src.database.db import get_db
from src.database.models import Role, ImageType
from src.repository.images import get_image_by_id, remove_img
from src.schemas.images import ImageModel, ImageResponse, ImageResponseReview, ImageModelReview, ImageDeletedModel
from src.repository import images as repository_images
from src.services.cache_in_redis import delete_cache_in_redis
from src.services.cloud_image import CloudImage
from src.services.roles import RoleAccess
from src.services.exception_detail import ExDetail as Ex


router = APIRouter(prefix="/images", tags=['images'])

allowed_operation_admin = RoleAccess([Role.admin])
allowed_operation_admin_moderator = RoleAccess([Role.admin, Role.moderator])
allowed_operation_admin_moderator_user = RoleAccess([Role.admin, Role.moderator, Role.user])


@router.post("/create_img_product", response_model=ImageResponse, dependencies=[Depends(allowed_operation_admin_moderator)],
             status_code=status.HTTP_201_CREATED)
async def create_image(description: str = Form(),
                       image_file: UploadFile = File(),
                       product_id: int = Form(),
                       main_image: bool = Form(),
                       db: Session = Depends(get_db)):

    try:
        body = ImageModel(description=description, image_type=ImageType.product, product_id=product_id, main_image=main_image)
    except ValidationError:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=Ex.HTTP_422_UNPROCESSABLE_ENTITY)
    file_name = CloudImage.generate_name_image()
    CloudImage.upload(image_file.file, file_name, overwrite=False)
    image_url = CloudImage.get_url_for_image(file_name)
    image = await repository_images.create(body, image_url, product_id, db)
    transformation_image_product = CloudImage.get_transformation_image(image_url, "product")
    image.image_url = transformation_image_product

    await delete_cache_in_redis()

    return image


@router.delete("/remove_img_product",
               status_code=status.HTTP_204_NO_CONTENT,
               dependencies=[Depends(allowed_operation_admin_moderator)])
async def remove_img_product(body: ImageDeletedModel,
                             db: Session = Depends(get_db)):

    image = await get_image_by_id(body.id, db)

    if not image:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=Ex.HTTP_404_NOT_FOUND)

    parts = image.image_url.split('/')
    public_id = parts[-1]

    print(public_id)

    print(CloudImage.deleted_img_cloudinary(public_id))

    await remove_img(image, db)

    await delete_cache_in_redis()


@router.post("/create_img_review", response_model=ImageResponseReview, dependencies=[Depends(allowed_operation_admin_moderator_user)],
             status_code=status.HTTP_201_CREATED)
async def create_image(description: str = Form(),
                       image_file: UploadFile = File(),
                       product_id: int = Form(),
                       review_id: int = Form(),
                       db: Session = Depends(get_db)):

    try:
        body = ImageModelReview(description=description, image_type=ImageType.review, product_id=product_id, review_id=review_id)
    except ValidationError:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=Ex.HTTP_422_UNPROCESSABLE_ENTITY)
    file_name = CloudImage.generate_name_image()
    CloudImage.upload(image_file.file, file_name, overwrite=False)
    image_url = CloudImage.get_url_for_image(file_name)
    image = await repository_images.create_image_review(body, image_url, product_id, db)
    transformation_image_review = CloudImage.get_transformation_image(image_url, "review")
    image.image_url = transformation_image_review

    await delete_cache_in_redis()

    return image
