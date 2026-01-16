# services/user_services.py
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

class UserServices:

    @staticmethod
    def update_user_information(post_data, files, user):
        name = post_data.get("name", "").strip()
        email = post_data.get("email", "").strip()
        avatar = files.get("avatar")

        fields = []

        # ---- changes ----
        if name != user.name:
            user.name = name
            fields.append("name")

        if email != user.email:
            user.email = email
            fields.append("email")

        if avatar:
            user.avatar = avatar
            fields.append("avatar")

        if not fields:
            return {"updated": False}

        user.save(update_fields=fields)

        return {"updated": True}
        