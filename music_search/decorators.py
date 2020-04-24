from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.decorators import user_passes_test

def admin_required(function=None, redirect_field_name=REDIRECT_FIELD_NAME, login_url='/log/login'):
    actual_decorator = user_passes_test(
        lambda u: u.admin,
        login_url=login_url,
        redirect_field_name=redirect_field_name
    )
    if function:
        return actual_decorator(function)
    return actual_decorator