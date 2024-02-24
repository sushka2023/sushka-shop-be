import hashlib
import re
from uuid import uuid4

import cloudinary
import cloudinary.uploader
from fastapi import HTTPException
from starlette import status

from src.conf.config import settings


class CloudImage:
    cloudinary.config(
        cloud_name=settings.cloudinary_name,
        api_key=settings.cloudinary_api_key,
        api_secret=settings.cloudinary_api_secret,
        secure=True
    )

    @staticmethod
    def deleted_img_cloudinary(public_id: str):
        r = cloudinary.uploader.destroy(public_id=public_id, invalidate=True)
        return r

    @staticmethod
    def generate_name_image():
        name = hashlib.sha256(str(uuid4()).encode('utf-8')).hexdigest()
        return f"sushka_store/{name}"

    @staticmethod
    def upload(file, public_id: str, overwrite=True):
        r = cloudinary.uploader.upload(file, public_id=public_id, overwrite=overwrite)
        return r

    @staticmethod
    def get_url_for_image(file_name):
        src_url = cloudinary.utils.cloudinary_url(file_name)
        return src_url[0]

    @staticmethod
    def get_transformation_image(public_id: str, transformation: str):
        public_id = re.search(r'(?<=/v\d/).+', public_id).group(0)
        if transformation in Transformation.name.keys():
            transformation_image_url = cloudinary.utils.cloudinary_url(public_id,
                                                                       transformation=[
                                                                           Transformation.name.get(transformation)])[0]
            return transformation_image_url

        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not Found")


class ProductImg:
    name = "product"
    transformation = {"width": 711, "height": 475}


class ReviewImg:
    name = "review"
    transformation = {"width": 711, "height": 475}


class Transformation:
    """
    Transformation images cloudinary.

    """
    name = {
        "product": ProductImg.transformation,
        "review": ReviewImg.transformation,
    }
