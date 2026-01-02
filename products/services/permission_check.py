from django.core.exceptions import PermissionDenied

def has_permission_to_create(creator, user):
    if creator != user:
        raise PermissionDenied(
            "Only the creator of the product can add variation type options"
        )