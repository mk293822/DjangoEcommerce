from django.conf import settings

def ui_settings(request):
    return {
        "TOAST_DURATION": settings.TOAST_DURATION,
    }
