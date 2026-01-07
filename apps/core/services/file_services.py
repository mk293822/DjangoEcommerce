import os
import uuid
import shutil
from PIL import Image

class FileServices:
    
    @staticmethod
    def delete_file_from_media(file):
        if not file:
            return
        folder = os.path.dirname(file.path)
        if os.path.exists(folder):
            shutil.rmtree(folder)
            
            
    @staticmethod
    def generate_file_path(instance, filename, foldername, id = "id"):
        ext = filename.split('.')[-1]
        
        instance_uuid = getattr(instance, id, uuid.uuid4())
        return os.path.join(foldername, str(instance_uuid), f"product/original.{ext}")
    
    @staticmethod
    def resize_image(original_path, sizes):
        base_dir = os.path.dirname(original_path)
        _, ext = os.path.splitext(original_path)

        img = Image.open(original_path)
        img = img.convert("RGB")  # drop alpha

        resized_paths = {}

        for size_name, (w, h) in sizes.items():
            img_copy = img.copy()
            img_copy.thumbnail((w, h))
            resized_name = f"{size_name}{ext}"
            resized_path = os.path.join(base_dir, resized_name)
            img_copy.save(resized_path, "JPEG", quality=85)
            resized_paths[size_name] = resized_path

        return resized_paths