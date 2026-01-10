import uuid
from django.utils.text import slugify
from django.db.models import Model

class SlugService:
    @staticmethod
    def generate_unique_slug(name: str) -> str:
        base_slug = slugify(name)
        short_uuid = str(uuid.uuid4())[:8]
        
        return f"{base_slug}-{short_uuid}"
    
    @staticmethod
    def assign_slug_to_model(model: Model) -> str:
        if not model.slug:
            model.slug = SlugService.generate_unique_slug(model.name)
        
        return model.slug
        