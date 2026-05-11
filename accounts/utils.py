# accounts/utils.py

import random
from django.core.cache import cache

OTP_EXPIRE = 120
RESEND_TIME = 30

def generate_otp():
    return str(random.randint(1000, 9999))


def send_otp(phone):
    otp = generate_otp()

    cache.set(f"otp_{phone}", otp, timeout=OTP_EXPIRE)
    cache.set(f"otp_lock_{phone}", True, timeout=RESEND_TIME)

    print("OTP:", otp)

    return True


def verify_otp(phone, otp):
    saved = cache.get(f"otp_{phone}")
    return saved == otp


def can_resend(phone):
    return not cache.get(f"otp_lock_{phone}")






from django.core.paginator import Paginator

def paginate_queryset(request, queryset, per_page=10):

    paginator = Paginator(
        queryset,
        per_page
    )

    page_number = request.GET.get("page")

    page_obj = paginator.get_page(
        page_number
    )

    return page_obj