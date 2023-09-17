import hashlib
import re
# from io import BytesIO
from uuid import uuid4

# import qrcode
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
    def generate_name_image():
        name = hashlib.sha256(str(uuid4()).encode('utf-8')).hexdigest()
        return f"sushka_store/{name}"

    # @staticmethod
    # def generate_name_avatar(email: str):
    #     name = hashlib.sha256(email.encode('utf-8')).hexdigest()[:12]
    #     return f"web9/{name}"

    @staticmethod
    def upload(file, public_id: str, overwrite=True):
        r = cloudinary.uploader.upload(file, public_id=public_id, overwrite=overwrite)
        return r

    # @staticmethod
    # def get_url_for_avatar(public_id, r):
    #     src_url = cloudinary.CloudinaryImage(public_id) \
    #         .build_url(width=250, height=250, crop='fill', version=r.get('version'))
    #     return src_url

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

    # @staticmethod
    # async def create_qr_code_image(url: str):
    #     qr = qrcode.QRCode(
    #         version=1,
    #         error_correction=qrcode.constants.ERROR_CORRECT_L,
    #         box_size=3,
    #         border=4,
    #     )
    #     qr.add_data(url)
    #     qr.make(fit=True)
    #
    #     img = qr.make_image(fill_color="black", back_color="white")
    #
    #     output = BytesIO()
    #     img.save(output)
    #     output.seek(0)
    #     return output


class ProductImg:
    name = "product"
    transformation = {"width": 500, "height": 500, "gravity": "faces", "crop": "fill"}  # TODO


class ReviewImg:
    name = "review"
    transformation = {"radius": "max", "width": 500, "height": 500, "gravity": "faces", "crop": "fill"}  # TODO


class Transformation:
    """
    Transformation images cloudinary.

    """
    name = {
        "product": ProductImg.transformation,
        "review": ReviewImg.transformation,
    }
