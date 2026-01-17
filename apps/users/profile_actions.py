from apps.users import constants
from .profile_handlers import handle_user_info, handle_update_password, handle_delete_account, handle_apply_vendor, handle_vendor_details, handle_stripe_connect

FORM_HANDLERS = {
    constants.FORM_USER_INFO: handle_user_info,
    constants.FORM_UPDATE_PASSWORD: handle_update_password,
    constants.FORM_DELETE_ACCOUNT: handle_delete_account,
    constants.FORM_APPLY_VENDOR: handle_apply_vendor,
    constants.FORM_VENDOR_DETAILS: handle_vendor_details,
    constants.FORM_STRIPE_CONNECT: handle_stripe_connect,
}
