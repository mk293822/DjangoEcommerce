# file: services/file_services.py

import os
import uuid
from io import BytesIO
from PIL import Image
from django.core.files.base import ContentFile
from django.conf import settings

class FileServices:
    
    @staticmethod
    def get_public_url(path):
        path = path.split('media/')[-1]
        return f"https://{settings.SUPABASE_PROJECT_REF}.supabase.co/storage/v1/object/public/media/{path}"

    @staticmethod
    def get_resized_image(url, size='thumb'):
        folder = os.path.dirname(url)
        return FileServices.get_public_url(f"{folder}/{size}.jpg")

    @staticmethod
    def generate_file_path(instance, filename, foldername, id="id", model=""):
        ext = filename.split('.')[-1]
        instance_uuid = getattr(instance, id, uuid.uuid4())
        return f"{foldername}/{instance_uuid}/{model}original.{ext}"

    @staticmethod
    def get_image(product, variation):

        if variation:
            vr_type = (
                product.variation_types
                .filter(type='image')
                .first()
            )

            if vr_type:
                option = (
                    vr_type.options
                    .filter(id__in=variation.variation_type_option)
                    .first()
                )

                if option:
                    image_obj = option.images.first()
                    if image_obj and image_obj.image:
                        return FileServices.get_resized_image(image_obj.image.url)

        if product.image:
            return FileServices.get_resized_image(product.image.url)

        return None

    @staticmethod
    def resize_image(field, sizes):
        """
        field: ImageField (like user.avatar)
        sizes: dict, e.g. {"thumb": (128,128), "large": (1024,1024)}
        """

        if not field:
            return {}

        with field.open("rb") as f:
            img = Image.open(f).convert("RGB")

        results = {}
        
        folder = os.path.dirname(field.name)

        for size_name, (w, h) in sizes.items():
            img_copy = img.copy()
            img_copy.thumbnail((w, h))

            buffer = BytesIO()
            img_copy.save(buffer, "JPEG", quality=85)
            buffer.seek(0)

            file_name = f"{folder}/{size_name}.jpg"

            saved_name = field.storage.save(file_name, ContentFile(buffer.read()))
            results[size_name] = field.storage.url(saved_name)

        return results

    @staticmethod
    def delete_remote_folder(field):
        if not field:
            return

        sizes = ["original", "thumb", "medium", "large"]
        folder = os.path.dirname(field.name) 

        for size in sizes:
            if size == "original":
                file_name = field.name
            else:
                file_name = os.path.join(folder, f"{size}.jpg")
            
            storage = field.storage
            if storage.exists(file_name):
                storage.delete(file_name)
